from beir import util, LoggingHandler
from beir.datasets.data_loader import GenericDataLoader
from beir.retrieval.evaluation import EvaluateRetrieval
from chroma_retriever import ChromaRetriever
import asyncio

SCIFACT_COLLECTION_NAME = "scifact_collection"
SCIFACT_DATA_PATH = r"D:\project\dense_retrieval_rag\datasets\scifact"

SCIDOCS_COLLECTION_NAME = "scidocs_collection"
SCIDOCS_DATA_PATH = r"D:\project\dense_retrieval_rag\datasets\scidocs"


async def evaluate_chroma_retriever():
    """Evaluate ChromaDB retriever using BEIR framework."""
    # Load dataset
    corpus, queries, qrels = GenericDataLoader(data_folder=SCIDOCS_DATA_PATH).load(split="test")
    
    print(f"📊 Loaded {len(corpus)} documents, {len(queries)} queries, {len(qrels)} qrels")
    
    # Initialize ChromaDB retriever
    retriever = ChromaRetriever(collection_name=SCIDOCS_COLLECTION_NAME)
    await retriever.connect()
    
    try:
        # Retrieve documents
        print("🔍 Retrieving documents from ChromaDB...")
        results = await retriever.retrieve(corpus=corpus, queries=queries, top_k=10)
        
        # Evaluate using BEIR
        print("📈 Evaluating results...")
        evaluator = EvaluateRetrieval()
        ndcg, _map, recall, precision = evaluator.evaluate(qrels, results, k_values=[1, 3, 5, 10])
        
        print("\n" + "="*50)
        print("EVALUATION RESULTS")
        print("="*50)
        print("\nNDCG@k:")
        for k, v in ndcg.items():
            print(f"  {k}: {v:.4f}")
        
        print("\nMAP@k:")
        for k, v in _map.items():
            print(f"  {k}: {v:.4f}")
        
        print("\nRecall@k:")
        for k, v in recall.items():
            print(f"  {k}: {v:.4f}")
        
        print("\nPrecision@k:")
        for k, v in precision.items():
            print(f"  {k}: {v:.4f}")
        print("="*50)
        
    finally:
        await retriever.disconnect()


if __name__ == "__main__":
    # Evaluate ChromaDB retriever
    asyncio.run(evaluate_chroma_retriever())
