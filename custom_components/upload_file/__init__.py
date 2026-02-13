"""Upload File integration."""
from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers import aiohttp_client

DOMAIN = "upload_file"
SERVICE_UPLOAD = "upload_file"
SERVICE_EXISTS = "file_exists"

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Optional("url"): vol.Url(),
        vol.Optional("data_base64"): str,
        vol.Optional("filename"): str,
        vol.Optional("path"): str,
    }
)

EXISTS_SCHEMA = vol.Schema(
    {
        vol.Optional("path"): str,
        vol.Optional("filename"): str,
        vol.Optional("local_url"): str,
    }
)


def _normalize_path(raw_path: str | None) -> str:
    path = (raw_path or "www/upload_file").lstrip("/").rstrip("/")
    if not path.startswith("www/"):
        path = f"www/{path}"
    if ".." in Path(path).parts:
        raise vol.Invalid("Invalid path.")
    return path


def _normalize_filename(raw_filename: str | None) -> str | None:
    if not raw_filename:
        return None
    filename = os.path.basename(raw_filename)
    if filename in {"", ".", ".."}:
        return None
    return filename


def _normalize_local_url(raw_url: str | None) -> str | None:
    if not raw_url:
        return None
    trimmed = str(raw_url).strip()
    if not trimmed:
        return None
    return trimmed.split("?", 1)[0]


def _resolve_local_path(local_url: str) -> str:
    if local_url.startswith("http://") or local_url.startswith("https://"):
        from urllib.parse import urlparse

        parsed = urlparse(local_url)
        local_path = parsed.path
    else:
        local_path = local_url

    if local_path.startswith("/local/"):
        rel = local_path[len("/local/") :]
    elif local_path.startswith("local/"):
        rel = local_path[len("local/") :]
    else:
        raise vol.Invalid("local_url must start with /local/")

    if ".." in Path(rel).parts:
        raise vol.Invalid("Invalid local_url path.")

    rel = rel.strip("/")
    return f"www/{rel}" if rel else "www"


def _guess_extension(mime_type: str | None, url: str | None) -> str:
    if mime_type:
        if "png" in mime_type:
            return "png"
        if "jpeg" in mime_type or "jpg" in mime_type:
            return "jpg"
        if "webp" in mime_type:
            return "webp"
    if url:
        for ext in ("png", "jpg", "jpeg", "webp"):
            if f".{ext}" in url.lower():
                return "jpg" if ext == "jpeg" else ext
    return "png"


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def _parse_data_base64(data_base64: str) -> tuple[bytes, str | None]:
    if data_base64.startswith("data:"):
        header, encoded = data_base64.split(",", 1)
        mime_type = header.split(";")[0].replace("data:", "")
        return base64.b64decode(encoded), mime_type
    return base64.b64decode(data_base64), None


async def _async_register_service(hass: HomeAssistant) -> None:

    async def _handle_upload(call: ServiceCall) -> dict[str, Any]:
        url = call.data.get("url")
        data_base64 = call.data.get("data_base64")

        if not url and not data_base64:
            raise vol.Invalid("url or data_base64 required")

        path = _normalize_path(call.data.get("path"))
        filename = _normalize_filename(call.data.get("filename"))

        image_bytes: bytes
        mime_type: str | None = None

        if url:
            session = aiohttp_client.async_get_clientsession(hass)
            async with session.get(url) as resp:
                resp.raise_for_status()
                image_bytes = await resp.read()
                mime_type = resp.headers.get("Content-Type")
        else:
            image_bytes, mime_type = _parse_data_base64(str(data_base64))

        extension = _guess_extension(mime_type, url)
        if not filename:
            filename = f"{_hash_bytes(image_bytes)}.{extension}"
        elif "." not in filename:
            filename = f"{filename}.{extension}"

        full_dir = Path(hass.config.path(path))
        full_dir.mkdir(parents=True, exist_ok=True)
        full_path = full_dir / filename
        full_path.write_bytes(image_bytes)

        local_path = path[4:] if path.startswith("www/") else path
        local_path = local_path.strip("/")
        local_url = f"/local/{local_path}/{filename}" if local_path else f"/local/{filename}"

        return {
            "local_url": local_url,
            "filename": str(full_path),
        }

    async def _handle_exists(call: ServiceCall) -> dict[str, Any]:
        local_url = _normalize_local_url(call.data.get("local_url"))
        path = call.data.get("path")
        filename = call.data.get("filename")

        if local_url:
            normalized_path = _resolve_local_path(local_url)
            full_path = Path(hass.config.path(normalized_path))
        else:
            if not path or not filename:
                raise vol.Invalid("local_url or path+filename required")
            normalized_path = _normalize_path(path)
            normalized_filename = _normalize_filename(filename)
            if not normalized_filename:
                raise vol.Invalid("Invalid filename")
            full_path = Path(hass.config.path(normalized_path)) / normalized_filename

        exists = full_path.exists() and full_path.is_file()
        return {"exists": exists}

    if not hass.services.has_service(DOMAIN, SERVICE_UPLOAD):
        hass.services.async_register(
            DOMAIN,
            SERVICE_UPLOAD,
            _handle_upload,
            schema=SERVICE_SCHEMA,
            supports_response=SupportsResponse.OPTIONAL,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_EXISTS):
        hass.services.async_register(
            DOMAIN,
            SERVICE_EXISTS,
            _handle_exists,
            schema=EXISTS_SCHEMA,
            supports_response=SupportsResponse.OPTIONAL,
        )


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    await _async_register_service(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await _async_register_service(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True
