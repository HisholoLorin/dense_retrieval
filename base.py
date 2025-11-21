import aiohttp
from chromadb import AsyncHttpClient
from chromadb.config import Settings
from chromadb.api.types import Documents, Metadatas, IDs


class ChromaManager:
    def __init__(self, collection_name: str):
        self.host = "http://127.0.0.1:7000"  # your Chroma server
        self.collection_name = collection_name
        self.auth_token = "When_a_man_walks_away_he_is_never_the_same_as_when_he_came"  # your auth token
        self.embed_url = "http://127.0.0.1:8000/embed"  # local embedding service
        self.client = None
        self.collection = None

    async def connect(self):
        """Initialize the async client and get/create a collection."""
        settings = Settings(
            chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
            chroma_client_auth_credentials=self.auth_token,
        )

        # ✅ must await the AsyncHttpClient creation
        self.client = await AsyncHttpClient(host=self.host, settings=settings)
        self.collection = await self.client.get_or_create_collection(name=self.collection_name)

    async def _get_embedding(self, text: str):
        """Fetch embedding asynchronously from /embed API."""
        async with aiohttp.ClientSession() as session:
            async with session.post(self.embed_url, json={"text": text}) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data.get("embedding") or data

    async def create(self, ids: IDs, documents: Documents, metadatas: Metadatas = None):
        """Add documents to the collection with auto embeddings."""
        embeddings = [await self._get_embedding(doc) for doc in documents]
        return await self.collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

    async def check_current_doc_count(self):
        collection = await self.client.get_collection(self.collection_name)
        count = await collection.count()
        print(f"📊 Current document count in ChromaDB collection '{self.collection_name}': {count}")


    async def query(self, query_texts: list[str], n_results: int = 3):
        """Search using auto-generated embeddings."""
        query_embeddings = [await self._get_embedding(text) for text in query_texts]
        return await self.collection.query(query_embeddings=query_embeddings, n_results=n_results)
    
    async def delete_collection(self):
        """Completely delete the collection."""
        await self.client.delete_collection(name=self.collection_name)
        print(f"🗑️ Collection '{self.collection_name}' deleted.")

    async def disconnect(self):
        """Close the client cleanly."""
        if self.client:
            self.client = None

