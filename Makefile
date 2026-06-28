.PHONY: install test web mcp lint clean

# Install runtime + dev dependencies into a local .venv
install:
	uv sync --all-extras

# Run the deterministic guardrail test suite (no LLM, no network)
test:
	uv run pytest -q

# Launch the course playground (agents-cli) — opens the chat UI on the triage_agent
playground:
	agents-cli playground

# Launch the ADK developer chat UI directly (equivalent, without agents-cli)
web:
	uv run adk web

# Run the clinical-kb MCP server standalone (for debugging)
mcp:
	uv run python mcp_server/server.py

# Lint
lint:
	uv run ruff check .

clean:
	rm -f audit_log.jsonl
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
