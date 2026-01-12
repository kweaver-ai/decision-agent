# kweaver-data-retrieval

A library for Kweaver data retrieval.

## Installation

```bash
pip install kweaver-data-retrieval
```

## Usage

### Import Tools

```python
from data_retrieval.tools import TOOLS_MAPPING

# List available tools
print(TOOLS_MAPPING.keys())
```

### Knowledge Network Tools

```python
from data_retrieval.tools.knowledge_network_tools import KNOWLEDGE_NETWORK_TOOLS_MAPPING

# Available tools:
# - knowledge_rerank: Rerank search results
# - knowledge_retrieve: Retrieve from knowledge base
# - kn_search: Knowledge network search (v2)
# - kn_path_search: Relation path retrieval
# - cypher_query: Execute Cypher queries
```

### Start API Server

```python
from data_retrieval.tools.tool_api_router import DEFAULT_APP
import uvicorn

uvicorn.run(DEFAULT_APP, host="0.0.0.0", port=9100)
```

Or from command line:

```bash
uvicorn data_retrieval.tools.tool_api_router:DEFAULT_APP --host 0.0.0.0 --port 9100
```

## Documentation

- [GitHub Repository](https://github.com/kweaver-ai/decision-agent/tree/main/data-retrieval)
- [API Documentation](https://github.com/kweaver-ai/decision-agent/blob/main/data-retrieval/api.json)

## License

Apache License 2.0
