from base import ChromaManager
from typing import Dict


class ChromaRetriever:
    """
    Wrapper for ChromaDB to work with BEIR evaluation framework.
    Converts ChromaDB query results to BEIR-compatible format.
    """
    
    def __init__(self, collection_name: str):
        self.manager = ChromaManager(collection_name=collection_name)
        self.connected = False
    
    async def connect(self):
        """Initialize the ChromaDB connection."""
        await self.manager.connect()
        self.connected = True
    
    async def disconnect(self):
        """Close the ChromaDB connection."""
        await self.manager.disconnect()
        self.connected = False
    
    async def retrieve(self, corpus: Dict[str, Dict[str, str]], queries: Dict[str, str], top_k: int = 10) -> Dict[str, Dict[str, float]]:
        """
        Retrieve documents for queries in BEIR format.
        
        Args:
            corpus: Dictionary of {doc_id: {"title": ..., "text": ...}}
            queries: Dictionary of {query_id: query_text}
            top_k: Number of results to retrieve per query
            
        Returns:
            Dictionary of {query_id: {doc_id: score, ...}}
            where score is the similarity score (converted from distance)
        """
        if not self.connected:
            raise RuntimeError("ChromaRetriever is not connected. Call connect() first.")
        
        results = {}
        query_ids = list(queries.keys())
        query_texts = [queries[qid] for qid in query_ids]
        
        # Query ChromaDB for all queries
        chroma_results = await self.manager.query(query_texts=query_texts, n_results=top_k)
        with open("chroma_debug.json", "w", encoding="utf-8") as debug_file:
            import json
            json.dump(chroma_results, debug_file, indent=2)
        
        # Convert ChromaDB results to BEIR format
        # ChromaDB returns results with indices corresponding to input queries
        for idx, query_id in enumerate(query_ids):
            results[query_id] = {}
            
            # Get the distances and metadatas for this query
            distances = chroma_results['distances'][idx]
            metadatas = chroma_results['metadatas'][idx]
            
            # Extract the actual document IDs from metadata (not ChromaDB UUIDs)
            for metadata, distance in zip(metadatas, distances):
                # The actual document ID is stored in metadata['_id']
                doc_id = metadata.get('_id', None)
                
                if doc_id:
                    # Convert distance to similarity score (higher is better)
                    # Using the formula: similarity = 1 / (1 + distance)
                    similarity_score = 1.0 / (1.0 + distance)
                    
                    results[query_id][doc_id] = similarity_score
        
        return results
    
    async def retrieve_with_metadata(self, queries: Dict[str, str], top_k: int = 10) -> Dict:
        """
        Retrieve documents with full metadata (for inspection/debugging).
        
        Args:
            queries: Dictionary of {query_id: query_text}
            top_k: Number of results to retrieve per query
            
        Returns:
            Dictionary with full ChromaDB response format
        """
        if not self.connected:
            raise RuntimeError("ChromaRetriever is not connected. Call connect() first.")
        
        query_ids = list(queries.keys())
        query_texts = [queries[qid] for qid in query_ids]
        
        chroma_results = await self.manager.query(query_texts=query_texts, n_results=top_k)
        
        # Add query_ids to results for easier interpretation
        return {
            'query_ids': query_ids,
            'chroma_results': chroma_results
        }
