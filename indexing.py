import json, uuid, asyncio
from base import ChromaManager

SCIFACT_COLLECTION_NAME = "scifact_collection"
SCIFACT_COLLECTION_PATH = r"D:\project\dense_retrieval_rag\datasets\scifact\corpus.jsonl"

SCIDOCS_COLLECTION_NAME = "scidocs_collection"
SCIDOCS_COLLECTION_PATH = r"/home/product/datasets/scidocs/corpus.jsonl"


class Document:
    def __init__(self, doc: dict):
        self.ids = [str(uuid.uuid4())]
        self.documents = [doc.get("text", "")]
        self.meta_datas = [{"_id": doc.get("_id", ""), "title": doc.get("title", ""), "metadata": json.dumps(doc.get("metadata", {}))}]


async def load_corpus_and_index(path, manager):
    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            doc = json.loads(line)
            if doc.get("text", None):
                document = Document(doc)

                await manager.create(
                    ids=document.ids,
                    documents=document.documents,
                    metadatas=document.meta_datas,
                )
                count += 1
                print(f"Indexed document ID: {document.ids[0]}, counter: {count}")


async def main():
    manager = ChromaManager(collection_name=SCIFACT_COLLECTION_NAME)

    await manager.connect()
    
    # await manager.delete_collection()
    await load_corpus_and_index(SCIFACT_COLLECTION_PATH, manager)

    await manager.disconnect()


# if __name__ == "__main__":
#     asyncio.run(main())



# async def load_corpus_and_index(path, manager):
#     count = 0
#     with open(path, "r", encoding="utf-8") as f:
#         for line in f:
#             line = line.strip()
#             if not line:
#                 continue

#             if count >= 11313:
#                 doc = json.loads(line)
#                 if doc.get("text", None):
#                     document = Document(doc)

#                     await manager.create(
#                         ids=document.ids,
#                         documents=document.documents,
#                         metadatas=document.meta_datas,
#                     )
#             count += 1
#             print(f"Counter: {count}")