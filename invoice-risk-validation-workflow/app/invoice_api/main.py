import logging
import os
import re
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pythonjsonlogger.json import JsonFormatter

from .config import get_settings
from .foundry import FoundryClient, FoundryError
from .models import ErrorResponse, FinalDecision, ValidationRequest, ValidationResponse


settings = get_settings()
REQUEST_COUNT = Counter("invoice_api_requests_total", "API requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("invoice_api_request_duration_seconds", "API request latency", ["path"])
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logging.basicConfig(level=settings.log_level, handlers=[handler], force=True)
    if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(logger_name="invoice_api")


configure_logging()
logger = logging.getLogger("invoice_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.foundry = FoundryClient(settings)
    yield
    await app.state.foundry.close()


app = FastAPI(
    title="Invoice Risk Validation API",
    version="1.0.0",
    docs_url=None if settings.auth_mode == "entra" else "/docs",
    lifespan=lifespan,
)


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=str(exc.detail), request_id=request_id).model_dump(),
        headers=exc.headers,
    )


if settings.origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_credentials=True,
        allow_methods=["POST", "GET"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )


@app.middleware("http")
async def request_controls(request: Request, call_next):
    candidate_request_id = request.headers.get("x-request-id", "")
    request_id = candidate_request_id if REQUEST_ID_PATTERN.fullmatch(candidate_request_id) else str(uuid.uuid4())
    request.state.request_id = request_id
    started = time.perf_counter()

    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > settings.max_request_bytes:
        response = JSONResponse(
            status_code=413,
            content=ErrorResponse(error="Request body is too large", request_id=request_id).model_dump(),
        )
    else:
        public_paths = {"/health/live", "/health/ready"}
        if settings.auth_mode == "entra" and request.url.path not in public_paths and not request.headers.get(
            "x-ms-client-principal-id"
        ):
            response = JSONResponse(
                status_code=401,
                content=ErrorResponse(error="Authentication required", request_id=request_id).model_dump(),
            )
        else:
            try:
                response = await call_next(request)
            except Exception:
                logger.exception("unhandled_request_error", extra={"request_id": request_id})
                response = JSONResponse(
                    status_code=500,
                    content=ErrorResponse(error="Internal server error", request_id=request_id).model_dump(),
                )

    duration = time.perf_counter() - started
    route = request.scope.get("route")
    metric_path = getattr(route, "path", "unmatched")
    response.headers["x-request-id"] = request_id
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["x-frame-options"] = "DENY"
    response.headers["cache-control"] = "no-store"
    REQUEST_COUNT.labels(request.method, metric_path, response.status_code).inc()
    REQUEST_LATENCY.labels(metric_path).observe(duration)
    logger.info(
        "request_complete",
        extra={"request_id": request_id, "path": metric_path, "status": response.status_code, "duration": duration},
    )
    return response


@app.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready")
async def ready() -> dict[str, str]:
    if not settings.foundry_agent_endpoint:
        raise HTTPException(status_code=503, detail="Foundry endpoint is not configured")
    return {"status": "ready"}


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post(
    "/v1/validations",
    response_model=ValidationResponse,
    responses={502: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def validate(payload: ValidationRequest, request: Request) -> ValidationResponse:
    try:
        raw_result, response_id = await request.app.state.foundry.validate_invoice(payload.invoice_number)
        result = FinalDecision.model_validate(raw_result)
    except FoundryError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except ValueError as exc:
        logger.warning("invalid_foundry_output", extra={"request_id": request.state.request_id})
        raise HTTPException(status_code=502, detail="Foundry returned an invalid decision") from exc
    return ValidationResponse(
        request_id=request.state.request_id,
        invoice_number=payload.invoice_number,
        result=result,
        foundry_response_id=response_id,
    )
