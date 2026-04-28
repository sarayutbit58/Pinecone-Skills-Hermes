# Pinecone Skills Hermes

Semantic Skill Intelligence Layer for Hermes Agent using Pinecone.

## Objective

Hermes skill activation can be too dependent on skill names, keywords, or manual user selection. This project adds a semantic skill router so Hermes can discover and recommend the right skill automatically from the user's intent.

Core pain solved:

```text
User should not need to remember or manually choose skill names.
Hermes should search skills semantically, select relevant candidates, and load the right skill context.
```

## Architecture

```text
User Prompt
  ↓
Hermes Agent
  ↓
Pinecone Skills Hermes Plugin
  ├─ Skill Indexer
  ├─ Semantic Router
  ├─ Security Policy Engine
  └─ Decision Logic
       ↓
Pinecone Index: hermes-skills
```

## Main Capabilities

- Parse Hermes `SKILL.md` files.
- Extract semantic sections such as overview, when-to-use, procedure, and examples.
- Generate embeddings for skill sections.
- Upsert skill vectors to Pinecone.
- Search relevant skills from natural user intent.
- Filter candidates with a policy engine.
- Return `auto_load`, `suggest`, or `none` decisions.
- Keep Hermes core untouched first; integrate through plugin/tool layer.

## Repository Structure

```text
.
├── README.md
├── plugin.yaml
├── example_config.yaml
├── requirements.txt
├── docs/
│   └── design.md
└── src/
    ├── __init__.py
    ├── config.py
    ├── indexer.py
    ├── policies.py
    ├── router.py
    └── util.py
```

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Set environment variables:

```bash
export PINECONE_API_KEY="your-pinecone-key"
export OPENAI_API_KEY="your-openai-key"
```

Copy config:

```bash
cp example_config.yaml ~/.hermes/config/pinecone_skill_router.yaml
```

Install as Hermes plugin:

```bash
git clone https://github.com/sarayutbit58/Pinecone-Skills-Hermes.git ~/.hermes/plugins/pinecone-skills-hermes
```

## Registered Tools

### `semantic_skill_index`

Scans configured Hermes skill directories and indexes changed skills into Pinecone.

### `semantic_skill_search`

Searches relevant skills for a user query and returns a structured routing decision.

Example output:

```json
{
  "mode": "auto_load",
  "skills": [
    {
      "name": "pdf",
      "score": 0.87,
      "reason": "Matched section 'when_to_use' with similarity 0.87."
    }
  ]
}
```

## Security Defaults

This project is secure-by-default:

- Community skills are disabled by default.
- Dangerous capabilities can be blocked.
- Skill metadata is filtered before routing.
- Pinecone is used for recall, not execution.
- Hermes remains the executor.

## Current Status

MVP scaffold. The design and code are structured for iterative hardening.

Next implementation priorities:

1. Update Pinecone SDK calls to match the exact installed Pinecone client version.
2. Add MCP transport option for Pinecone.
3. Add unit tests with local mock embeddings.
4. Add reranker and feedback telemetry later.
