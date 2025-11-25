# MCP-GPT-Researcher

A Model Context Protocol server that gives AI assistants the ability to conduct systematic, multi-source research on any topic. This is not a search tool — it's a research infrastructure.

## What is GPT Researcher?

GPT Researcher is an autonomous research agent that doesn't just find information — it investigates. It spawns multiple agents to explore different angles of a question, validates sources across the web, and synthesizes findings into comprehensive reports with proper citations.

- **Source**: [github.com/assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher)
- **Architecture**: Multi-agent system with planner and crawler agents
- **Output**: Detailed reports with sourced claims, not vibes

The official project describes itself as "an autonomous agent for comprehensive online research."

## What does this MCP server do?

It exposes GPT Researcher's capabilities through the Model Context Protocol. Your AI assistant becomes a research lead that can delegate deep investigation tasks, receive structured reports, and build on previous research.

### Available Operations

| Operation | Description | Latency |
|-----------|-------------|---------|
| `deep_research` | Full comprehensive research report | 3-5 min |
| `quick_research` | Rapid assessment with sources | 30-60 sec |

## Installation

### Prerequisites

1. **GPT Researcher running** somewhere

For installation, see the [official deployment guide](https://github.com/assafelovic/gpt-researcher?tab=readme-ov-file#-getting-started).

2. **Python environment**

```bash
git clone https://github.com/assafelovic/mcp-gpt-researcher.git
cd mcp-gpt-researcher
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. **Configuration**

```bash
cp .env.example .env
```

Set `GPT_RESEARCHER_BASE_URL` to your GPT Researcher instance.

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `GPT_RESEARCHER_BASE_URL` | (required) | GPT Researcher API endpoint |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

## Integration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gpt-researcher": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/server.py"],
      "env": {
        "GPT_RESEARCHER_BASE_URL": "http://localhost:YOUR_PORT"
      }
    }
  }
}
```

### OpenCode / Cursor

Consult your IDE's MCP configuration documentation for the appropriate configuration format.

## Usage

This MCP server exposes two primary tools:

### `deep_research`

For when you need the full picture. Generates comprehensive research reports with:
- Systematic source gathering
- Cross-validation of claims
- Structured findings
- Full citations

**Parameters:**
- `query`: Research question
- `report_type`: `research_report` (recommended), `resource_report`, or `outline_report`

### `quick_research`

For rapid assessment. Returns preliminary findings with key sources, suitable for:
- Initial fact-checking
- Direction setting
- Stakeholder summaries

## Research Workflow Example

```
1. quick_research: "What are the main approaches to fusion energy?"
2. [Review findings, identify knowledge gaps]
3. deep_research: "Detailed analysis of tokamak vs stellarator approaches"
4. deep_research: "Recent breakthroughs in high-temperature superconducting magnets"
5. [Synthesize into comprehensive report]
```

## Limitations

- Research operations take 3-5 minutes for comprehensive reports
- Rate limiting depends on underlying GPT Researcher deployment
- Network conditions affect source validation quality

## Troubleshooting

**API unreachable**
- Verify GPT Researcher is running at `GPT_RESEARCHER_BASE_URL`
- Check firewall rules
- Confirm port accessibility

**Timeout errors**
- Increase client timeout for long-running research
- Consider `quick_research` for time-sensitive queries

**Authentication errors**
- Some GPT Researcher deployments require API keys
- Set `OPENAI_API_KEY` in GPT Researcher's environment

## Contributing

Issues and pull requests welcome. Please include reproduction steps and expected vs actual behavior.

## License

MIT
