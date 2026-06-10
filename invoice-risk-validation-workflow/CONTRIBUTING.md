# Contributing

Use pull requests for all changes. Keep agent prompts, workflow mappings, schemas, tests, and published Foundry versions aligned.

Before opening a pull request:

```powershell
cd app
pip install -r requirements-dev.txt
pytest -q
python -m compileall invoice_api
docker build -t invoice-risk-api:test .
```

Include synthetic evaluation evidence for prompt or workflow changes. Never commit real business documents, personal data, API keys, tokens, connection strings, or production traces.
