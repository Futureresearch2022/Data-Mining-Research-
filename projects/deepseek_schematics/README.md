# DeepSeek schematics project

Generates technical schematics from natural-language prompts using the DeepSeek
chat API and renders them to SVG + DXF.

## Setup

```bash
pip install -e ".[deepseek]"
export DEEPSEEK_API_KEY=sk-...
```

## Run

```bash
python projects/deepseek_schematics/generate.py "single-stage gear reducer"
```

Output drawings are written to `projects/deepseek_schematics/output/`.
