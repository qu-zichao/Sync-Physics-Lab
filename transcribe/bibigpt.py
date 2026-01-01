import os
from typing import Optional

import requests


API_URL = "https://api.bibigpt.co/api/v1/getSubtitle"


def _attach_response_details(
    error: RuntimeError, status_code: Optional[int], body_snippet: Optional[str]
) -> None:
    error.status_code = status_code
    error.body_snippet = body_snippet


def get_subtitle(url: str, audio_language: str = "auto") -> list[dict]:
    token = os.getenv("BIBIGPT_API_TOKEN")
    if not token:
        raise RuntimeError("Missing BIBIGPT_API_TOKEN. 请在 .env 设置 BIBIGPT_API_TOKEN")

    params = {"url": url}
    if audio_language:
        params["audioLanguage"] = audio_language

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=30)
    except requests.RequestException as exc:
        status_code = getattr(exc.response, "status_code", None) if getattr(exc, "response", None) else None
        body_snippet = None
        if getattr(exc, "response", None) is not None and exc.response.text:
            body_snippet = exc.response.text[:300]
        error = RuntimeError("Failed to reach BibiGPT API.")
        _attach_response_details(error, status_code, body_snippet)
        raise error from exc

    body_snippet = response.text[:300] if response.text else None
    status_code = response.status_code

    try:
        payload = response.json()
    except ValueError as exc:
        error = RuntimeError("Invalid JSON response from BibiGPT API.")
        _attach_response_details(error, status_code, body_snippet)
        raise error from exc

    if not response.ok:
        error = RuntimeError("BibiGPT API request failed.")
        _attach_response_details(error, status_code, body_snippet)
        raise error

    if payload.get("success") is not True:
        info = payload.get("message") or payload.get("detail") or payload
        error = RuntimeError(f"BibiGPT API error: {str(info)[:200]}")
        _attach_response_details(error, status_code, body_snippet)
        raise error

    subtitles = payload.get("detail", {}).get("subtitlesArray")
    if subtitles is None:
        error = RuntimeError("BibiGPT API response missing subtitlesArray.")
        _attach_response_details(error, status_code, body_snippet)
        raise error

    return subtitles
