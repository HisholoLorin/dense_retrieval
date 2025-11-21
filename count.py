from base import ChromaManager
import asyncio

NAGA_HILLS_COLLECTION_NAME = "1905_Naga_Hills_and_Manipur_by_Allen"
SCIFACT_COLLECTION_NAME = "scifact_collection"
SCIDOCS_COLLECTION_NAME = "scidocs_collection"

async def main():
    manager = ChromaManager(collection_name=SCIDOCS_COLLECTION_NAME)

    await manager.connect()
    
    await manager.check_current_doc_count()

    await manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())