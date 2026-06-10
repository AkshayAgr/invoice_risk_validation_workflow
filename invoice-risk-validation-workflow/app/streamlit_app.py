import os

import requests
import streamlit as st


API_URL = os.getenv("INVOICE_API_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(page_title="Invoice Risk Validation Workflow", layout="wide")
st.title("Invoice Risk Validation Workflow")
st.caption("Enterprise invoice validation powered by a published Microsoft Foundry workflow.")

invoice_number = st.text_input("Enter invoice number", value="INV-2026-014", max_chars=64)

if st.button("Run Validation", type="primary", disabled=not invoice_number.strip()):
    try:
        with st.spinner("Validating invoice evidence..."):
            response = requests.post(
                f"{API_URL}/v1/validations",
                json={"invoice_number": invoice_number.strip()},
                timeout=150,
            )
            response.raise_for_status()
            envelope = response.json()
            result = envelope["result"]

        if isinstance(result, dict) and {"decision_status", "risk_score", "risk_level"} <= result.keys():
            col1, col2, col3 = st.columns(3)
            col1.metric("Decision", result["decision_status"])
            col2.metric("Risk Score", result["risk_score"])
            col3.metric("Risk Level", result["risk_level"])
        st.subheader("Validation Result")
        st.json(result)
        st.caption(f"Request ID: {envelope['request_id']}")
    except requests.HTTPError as exc:
        request_id = exc.response.headers.get("x-request-id", "unknown")
        st.error(f"Validation failed. Request ID: {request_id}")
    except requests.RequestException:
        st.error("The validation service is unavailable. Try again shortly.")
