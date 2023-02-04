import os
from typing import Any

import sentry_sdk
from flask import Flask, request
from pydantic import ValidationError
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.exceptions import HTTPException

from wumpus.sanitizer import Sanitizer, SanitizeSchema

SENTRY_DSN = os.environ.get("SENTRY_DSN")
sentry_sdk.init(SENTRY_DSN, integrations=[FlaskIntegration()], traces_sample_rate=0.1)

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.post("/v1/sanitize")
def sanitize() -> dict[str, str]:
    data = SanitizeSchema(**request.json or {})
    return Sanitizer.sanitize(data)


@app.errorhandler(HTTPException)
def handle_http_exception(error: HTTPException) -> tuple[dict[str, str], int]:
    return {"message": error.name}, error.code or 500


@app.errorhandler(ValidationError)
def handle_validation_error(error: ValidationError) -> tuple[dict[str, Any], int]:
    return {"message": "Bad Request", "errors": error.errors()}, 400
