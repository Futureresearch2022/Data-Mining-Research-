# Gemini schematics project

Generates technical schematics from natural-language prompts using the Google
Gemini API and renders them to SVG + DXF.

## Setup

```bash
pip install -e ".[gemini]"
export GEMINI_API_KEY=...
```

## Run

```bash
python projects/gemini_schematics/generate.py "low-pass RC filter"
```

Output drawings are written to `projects/gemini_schematics/output/`.
