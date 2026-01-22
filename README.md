# Diagramm

Pipeline for transforming natural language descriptions into structured diagram models and then rendering them into multiple formats. The core idea is **LLM = semantic parser**, everything else is deterministic code.

## Architecture

```
Text
  ↓
[LLM Analyzer]
  ↓
Formal model (JSON / AST)
  ↓
Validator + Normalizer
  ↓
Diagram generators
  ↓
Render (SVG / PNG / web)
```

## Key principles

- LLM returns **only strict JSON** that conforms to the schema.
- The LLM **never draws** diagrams directly.
- Validation and normalization are mandatory.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Validate a JSON model:

```bash
diagramm validate examples/activity.json
```

Generate Mermaid output:

```bash
diagramm generate examples/activity.json --format mermaid
```

Generate Mermaid output into a file:

```bash
diagramm generate examples/activity.json --format mermaid --output out.mmd
```

Normalize and re-emit JSON:

```bash
diagramm normalize examples/activity.json
```

Print the JSON schema:

```bash
diagramm schema
```

Classify text into a diagram type:

```bash
echo "Клиент оформляет заказ. Если товар есть..." | diagramm classify
```

## How to run locally

1. Create a virtual environment and install the package:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```

2. Validate the example model:

   ```bash
   diagramm validate examples/activity.json
   ```

3. Render Mermaid and PlantUML outputs:

   ```bash
   diagramm generate examples/activity.json --format mermaid --output out.mmd
   diagramm generate examples/activity.json --format plantuml --output out.puml
   ```

4. Render diagrams (optional):

   - Mermaid: `npx @mermaid-js/mermaid-cli -i out.mmd -o out.svg`
   - PlantUML: `java -jar plantuml.jar out.puml`

5. Run the test suite:

   ```bash
   pytest
   ```

## Repository layout

- `src/diagramm/model.py` — internal AST types.
- `src/diagramm/schema.py` — JSON schema for LLM output.
- `src/diagramm/validator.py` — consistency checks.
- `src/diagramm/normalizer.py` — normalization for downstream generators.
- `src/diagramm/generators/` — renderers (Mermaid, PlantUML, JSON).
- `src/diagramm/llm_prompt.py` — system prompt template.
- `examples/` — sample inputs.

## Formats

The generators focus on text outputs (Mermaid, PlantUML, JSON). For SVG/PNG/web rendering, use existing external renderers in the next stage.
