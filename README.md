# Upload File (Home Assistant)

A minimal Home Assistant integration to store files under `/config/www` and return the `/local/` URL. Supports upload via URL or Base64 (including data URI).

## Installation (HACS)

1. Add this repository as a custom repository in HACS.
2. Install the **Upload File** integration.
3. Restart Home Assistant.

## Add via UI

Settings → Devices & Services → Add Integration → **Upload File**.

## Service

### `upload_file.upload_file`

Downloads a file from URL or Base64 data to `/config/www` and returns the local URL.

**Fields**
- `url` (optional): Image URL to download.
- `data_base64` (optional): Base64 content or data URI.
- `filename` (optional): Filename (without path).
- `path` (optional): Target path relative to `/config` (default: `www/upload_file`).

**Response**
- `local_url`: Path under `/local/…`
- `filename`: Full path on the filesystem

### `upload_file.file_exists`

Checks whether a file exists in `/config/www`. You can provide either a `/local/…` URL or a `path` + `filename`.

**Fields**
- `local_url` (optional): `/local/...` URL to check.
- `path` (optional): Target path relative to `/config` (default: `www/upload_file`).
- `filename` (optional): Filename (without path).

**Response**
- `exists`: `true` if the file exists, otherwise `false`.

### Example: local_url
```yaml
service: upload_file.file_exists
data:
  local_url: /local/upload_file/example.png
```

### Example: path + filename
```yaml
service: upload_file.file_exists
data:
  path: www/upload_file
  filename: example.png
```

### Example: URL
```yaml
service: upload_file.upload_file
data:
  url: https://example.com/image.png
  path: www/upload_file
```

### Example: Base64
```yaml
service: upload_file.upload_file
data:
  data_base64: "data:image/png;base64,iVBORw0KGgo..."
  filename: test.png
  path: www/upload_file
```

## Notes

- Target path must be under `/config/www` to be served via `/local/…`.
- Supported image types: png, jpg, webp. The file type is inferred from MIME type or URL.

## License

MIT
