import json
from pathlib import Path

from jsonschema import validate


ROOT = Path(__file__).parents[2]


def test_sample_final_decision_matches_schema():
    wrapper = json.loads((ROOT / "workflow/json-schemas/final-decision-result.schema.json").read_text(encoding="utf-8"))
    sample = json.loads((ROOT / "outputs/sample-agent-output.json").read_text(encoding="utf-8"))
    validate(instance=sample, schema=wrapper["schema"])
