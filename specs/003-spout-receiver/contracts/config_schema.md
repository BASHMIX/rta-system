# Contract: Config Schema (spout section)

**Date**: 2026-05-17 | **Branch**: `003-spout-receiver`

## Location

`config.json` in the project root directory.

## Schema

```jsonc
{
  "spout": {
    "sender_name": "string",     // Required. Spout sender to connect to.
    "sample_points": [[int, int]],  // Required. At least one [x, y] coordinate.
    "target_fps": int            // Optional. Default 30. Range [1, 240].
  }
  // ... other sections (profiles, obs, etc.) may coexist
}
```

## Example

```json
{
  "spout": {
    "sender_name": "OBS",
    "sample_points": [[640, 360], [200, 150]],
    "target_fps": 60
  }
}
```

## Validation Rules

| Field | Rule |
|-------|------|
| `spout` | Must be present (top-level key) |
| `spout.sender_name` | Non-empty string |
| `spout.sample_points` | Array of [x, y] pairs; at least one; x >= 0, y >= 0 |
| `spout.target_fps` | Integer; 1–240 inclusive; default 30 if omitted |

## Loading Behavior

- Loaded once at startup by `SpoutConfig.from_file("config.json")`
- Missing fields raise `ConfigError` with a descriptive message
- Invalid types raise `ConfigError` (e.g., string instead of int for target_fps)
- Unknown keys under `spout` are silently ignored (forward-compat)

## Error Messages

| Violation | Error Message |
|-----------|---------------|
| Missing `spout` key | `"config.json missing required top-level key 'spout'"` |
| Empty sender name | `"spout.sender_name must be a non-empty string"` |
| No sample points | `"spout.sample_points must contain at least one [x, y] pair"` |
| Invalid point format | `"spout.sample_points[0]: expected [x, y] pair of integers"` |
| Negative coordinate | `"spout.sample_points[0]: x and y must be non-negative"` |
| target_fps out of range | `"spout.target_fps must be 1–240 (got {value})"` |
| File not found | `"config.json not found at {path}"` |
| JSON parse error | `"Failed to parse config.json: {details}"` |
