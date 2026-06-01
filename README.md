# Data Mining Research — Schematics AI

Generate technical schematics and drafting drawings from natural-language prompts
using **DeepSeek** and **Google Gemini**, rendered to **SVG** and **DXF**.

Give the model a description of a system ("a single-stage gear reducer", "a
low-pass RC filter") and it returns a structured block-diagram schematic that is
rendered to a web-viewable SVG and a CAD-ready DXF.

## How it works

```
prompt ─▶ ModelClient (DeepSeek | Gemini) ─▶ JSON ─▶ Schematic ─▶ SVG + DXF
```

- **Clients** (`schematics_ai.clients`) ask DeepSeek/Gemini for a schematic as
  strict JSON.
- **Schema** (`schematics_ai.schema.Schematic`) validates that JSON: labelled
  `components` on a millimetre canvas plus `connections` between them.
- **Renderers** (`schematics_ai.drawing`) turn a `Schematic` into SVG and DXF.

The pipeline is provider-agnostic — any object implementing `ModelClient`
(including a test double) works with `SchematicGenerator`.

## Layout

```
src/schematics_ai/
  schema.py            # Schematic / Component / Connection data model
  prompts.py           # shared system + user prompts
  clients/             # DeepSeek and Gemini API wrappers
  drawing/             # svg_renderer.py, dxf_renderer.py
  generator.py         # prompt -> schematic -> files
  cli.py               # `schematics-ai` command
projects/
  deepseek_schematics/ # runnable DeepSeek example
  gemini_schematics/   # runnable Gemini example
examples/
  sample_schematic.json
  render_sample.py     # offline render demo (no API key)
tests/
```

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"          # everything incl. both SDKs + test tools
# or only what you need:
pip install -e ".[deepseek]"
pip install -e ".[gemini]"
```

## API keys

```bash
cp .env.example .env             # then edit
export DEEPSEEK_API_KEY=sk-...
export GEMINI_API_KEY=...
```

## Usage

CLI:

```bash
schematics-ai "single-stage gear reducer" --provider deepseek -o output
schematics-ai "low-pass RC filter" --provider gemini -o output
```

Python:

```python
from schematics_ai import SchematicGenerator
from schematics_ai.clients import GeminiClient

generator = SchematicGenerator(GeminiClient())
schematic, files = generator.generate_and_render(
    "three-phase motor starter", output_dir="output"
)
print(files["svg"], files["dxf"])
```

Offline render (no API key — verifies the drawing pipeline):

```bash
python examples/render_sample.py
```

## Develop

```bash
ruff check .
pytest
```
