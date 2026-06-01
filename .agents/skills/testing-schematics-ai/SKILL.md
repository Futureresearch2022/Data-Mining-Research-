---
name: testing-schematics-ai
description: End-to-end test the schematics-ai pipeline (prompt -> DeepSeek/Gemini -> JSON -> SVG + DXF). Use when verifying CLI generation, SVG/DXF renderers, or the note-clipping fix.
---

# Testing schematics-ai

The package turns a natural-language prompt into a block-diagram schematic and renders it to SVG + DXF. Pipeline: `prompt -> ModelClient (deepseek|gemini) -> JSON -> Schematic -> render_svg / render_dxf`.

## Setup
- Use the project venv: `/home/ubuntu/Data-Mining-Research-/.venv` (`./.venv/bin/python`, `./.venv/bin/schematics-ai`).
- SDKs (`openai`, `google-genai`) are imported lazily, only when a client is instantiated, so offline render tests need no keys.

## Devin Secrets Needed
- `GEMINI_API_KEY` — Gemini live generation (`-p gemini`). Get one at https://aistudio.google.com/apikey.
- `DEEPSEEK_API_KEY` — DeepSeek live generation (`-p deepseek`). Note the account must be funded; an unfunded account returns HTTP 402 `Insufficient Balance` even with a valid key.

## Live CLI test (golden path)
```
./.venv/bin/schematics-ai "A single-stage gear reducer: motor, input shaft, gearbox, output shaft, coupling" -p gemini -o /tmp/test_gem -n gem
```
Pass criteria: exit 0; components >= 3; connections >= 2; both `gem.svg` and `gem.dxf` written.

Verify DXF entities with ezdxf (boxes=LWPOLYLINE or ELLIPSE, labels/title=TEXT, connectors=LINE):
```
./.venv/bin/python -c "import ezdxf,collections; d=ezdxf.readfile('/tmp/test_gem/gem.dxf'); print(collections.Counter(e.dxftype() for e in d.modelspace()))"
```

## Viewing SVG output in a browser
The renderer emits SVG with width/height in **millimetres**, so opening it directly often overflows the viewport (browser zoom via CDP may not visibly change it). Wrap it in a tiny HTML file with `<img src=... style="width:100%">` and open that instead so the whole diagram fits:
```html
<img src="file:///tmp/test_gem/gem.svg" style="width:100%;height:auto">
```

## Note-clipping regression
The SVG viewBox height must scale with the number of notes (`svg_renderer.py`). To prove it offline, render a schematic with 6 notes, parse the viewBox and all `class="note"` y values, and assert `max(note_y) <= viewBox_min_y + viewBox_height`. To show the bug visually, copy the SVG and shrink its viewBox/height to the old formula value (`max_y - min_y + 20`) — notes 4-6 get clipped at the bottom edge. `tests/test_renderers.py::test_svg_viewbox_covers_all_notes` covers this.

## Gotchas
- Default Gemini model can go stale: `gemini-1.5-flash` was removed (HTTP 404). If live calls 404, list models with `client.models.list()` and pick a current one (e.g. `gemini-2.5-flash`). Default lives in `clients/gemini_client.py` (`DEFAULT_MODEL`).
- Gemini free tier has per-minute quota; on HTTP 429 wait ~35s and retry.
- Offline render path (no key) can be exercised via `examples/render_sample.py`.

## Unit tests / lint
```
./.venv/bin/python -m pytest -q
./.venv/bin/ruff check .
```
