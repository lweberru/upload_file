# Upload File (Home Assistant)

Eine minimale Home-Assistant-Integration zum Speichern von Bildern nach `/config/www` und Rückgabe der `/local/`-URL. Unterstützt das Hochladen per URL oder Base64 (auch als data URI).

## Installation (HACS)

1. Füge dieses Repository als Custom-Repository in HACS hinzu.
2. Installiere die Integration **Upload File**.
3. Starte Home Assistant neu.

## Service

### `upload_file.upload_file`

Lädt ein Bild von einer URL oder Base64-Daten nach `/config/www` und gibt die lokale URL zurück.

**Felder**
- `url` (optional): Bild-URL zum Herunterladen.
- `data_base64` (optional): Base64-Inhalt oder data URI.
- `filename` (optional): Dateiname (ohne Pfad).
- `path` (optional): Zielpfad relativ zu `/config` (Standard: `www/upload_file`).

**Antwort**
- `local_url`: Pfad unter `/local/…`
- `filename`: Vollständiger Pfad auf dem Dateisystem

### Beispiel: URL
```yaml
service: upload_file.upload_file
data:
  url: https://example.com/image.png
  path: www/upload_file
```

### Beispiel: Base64
```yaml
service: upload_file.upload_file
data:
  data_base64: "data:image/png;base64,iVBORw0KGgo..."
  filename: test.png
  path: www/upload_file
```

## Hinweise

- Der Zielpfad muss unter `/config/www` liegen, damit Home Assistant ihn als `/local/…` ausliefert.
- Es werden einfache Bildtypen unterstützt (png, jpg, webp). Der Dateityp wird aus MIME-Type oder URL abgeleitet.

## Lizenz

MIT
