from data_retrieval.tools.knowledge_network_tools.tools.rerank_tool import KnowledgeNetworkRerankTool
from data_retrieval.tools.knowledge_network_tools.tools.retrieval_tool import KnowledgeNetworkRetrievalTool
from data_retrieval.tools.knowledge_network_tools.tools.relation_path_retrieval_tool import RelationPathRetrievalTool
from data_retrieval.tools.knowledge_network_tools.tools.cypher.cypher_query_tool import CypherQueryTool

KNOWLEDGE_NETWORK_TOOLS_MAPPING = {
    "knowledge_rerank": KnowledgeNetworkRerankTool,
    "kn_search": KnowledgeNetworkRetrievalTool,
    "kn_path_search": RelationPathRetrievalTool,
    "cypher_query": CypherQueryTool,
}
