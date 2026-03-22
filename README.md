# GPT Researcher MCP Server

MCP server para GPT Researcher con descubrimiento automático de puerto.

## Puertos Oficiales

Según la documentación oficial, GPT Researcher se ejecuta en:
- **Backend API**: puerto `8000` (FastAPI)
- Frontend: puerto `3000` (Next.js)

## Quick Start

```bash
cd mcp-gpt-researcher
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
python3 server.py
```

## Lógica de Descubrimiento

1. **Primero**: Busca en puerto `8000` (oficial)
2. **Si no encuentra**: Escanea puertos alternativos (8001, 8080, 10305, 3000, 5000)
3. **Si sigue sin encontrar**: Pide al usuario el puerto por consola
4. **Fallback**: Usa `http://localhost:8000` si el usuario no responde

## Configuración Manual

Si prefieres configurar manualmente, usa la variable de entorno:
```bash
export GPT_RESEARCHER_BASE_URL=http://localhost:8000
```

O crea un archivo `.env` en la raíz del proyecto.

## Herramientas

### gptr_deep_research
- **query** (string): Consulta de investigación
- **report_type** (string): "research_report", "resource_report", o "outline_report"

### gptr_quick_search
- **query** (string): Consulta rápida

## Claude Desktop

```json
{
  "mcpServers": {
    "gpt-researcher": {
      "command": "uv",
      "args": ["--directory", "/Users/simba/Code/MCP-servers/mcp-gpt-researcher", "run", "python3", "server.py"]
    }
  }
}
```

## MCP Server

- Puerto: 8080
- SSE: /sse
- HTTP: /mcp