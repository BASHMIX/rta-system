# Contract: Profile JSON Schema

Each profile is a JSON file conforming to the extended `config.json` schema
from the roadmap. The schema adds metadata fields (`name`, `created_at`,
`updated_at`) to the base config structure.

## Schema

```json
{
  "$schema": "https://json-schema.org/draft/07/schema#",
  "title": "GameProfile",
  "type": "object",
  "required": ["name", "system", "players", "obs_events", "created_at", "updated_at"],
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "system": {
      "type": "object",
      "required": ["resolution", "target_fps", "obs_websocket"],
      "properties": {
        "resolution": {
          "type": "array",
          "items": [{ "type": "integer", "minimum": 1 }],
          "minItems": 2,
          "maxItems": 2
        },
        "target_fps": { "type": "integer", "minimum": 1 },
        "obs_websocket": {
          "type": "object",
          "required": ["host", "port", "password"],
          "properties": {
            "host": { "type": "string" },
            "port": { "type": "integer", "minimum": 1, "maximum": 65535 },
            "password": { "type": "string" }
          }
        }
      }
    },
    "players": {
      "type": "object",
      "patternProperties": {
        "^(P1|P2)$": {
          "type": "object",
          "properties": {
            "lifebar": { "$ref": "#/definitions/ROIConfig" },
            "combo_counter": { "$ref": "#/definitions/ROIConfig" },
            "system_text_zone": { "$ref": "#/definitions/ROIConfig" }
          }
        }
      }
    },
    "obs_events": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["trigger", "condition", "actions"],
        "properties": {
          "trigger": { "type": "string" },
          "condition": { "type": "string" },
          "actions": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["type"],
              "properties": {
                "type": { "enum": ["toggle_source", "toggle_filter"] },
                "scene": { "type": "string" },
                "source": { "type": "string" },
                "filter": { "type": "string" },
                "state": { "type": "boolean" }
              }
            }
          }
        }
      }
    },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" }
  },
  "definitions": {
    "ROIConfig": {
      "type": "object",
      "required": ["roi", "direction", "segments", "target_color_hsv_range"],
      "properties": {
        "roi": {
          "type": "array",
          "items": [{ "type": "integer" }],
          "minItems": 4,
          "maxItems": 4
        },
        "direction": { "enum": ["RTL", "LTR"] },
        "segments": { "type": "integer", "minimum": 1 },
        "target_color_hsv_range": {
          "type": "array",
          "items": {
            "type": "array",
            "items": [{ "type": "integer" }],
            "minItems": 3,
            "maxItems": 3
          },
          "minItems": 2,
          "maxItems": 2
        }
      }
    }
  }
}
```

## File Naming Convention

`profiles/<sanitized-name>.json` where sanitization:
- Lowercase
- Replace non-alphanumeric chars (except `-`, `_`, `.`) with `-`
- Collapse consecutive `-` to single
- Strip leading/trailing `-`
