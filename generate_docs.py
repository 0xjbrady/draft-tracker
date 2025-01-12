"""Script to generate API documentation."""
import json
import yaml
from pathlib import Path
from app.main import app

# Create docs directory if it doesn't exist
docs_dir = Path("docs")
docs_dir.mkdir(exist_ok=True)

# Generate OpenAPI spec in JSON format
with open(docs_dir / "openapi.json", "w") as f:
    json.dump(app.openapi(), f, indent=2)

# Generate OpenAPI spec in YAML format
with open(docs_dir / "openapi.yaml", "w") as f:
    yaml.dump(app.openapi(), f, sort_keys=False)

print("API documentation generated in docs/") 