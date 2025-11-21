from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModel
import torch

# ---------------------------
# Model setup
# ---------------------------
model_name = "jinaai/jina-embeddings-v3"
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"🚀 Loading model '{model_name}' on {device} ...")

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name, trust_remote_code=True).to(device)
model.eval()

print("✅ Model loaded successfully.")

# ---------------------------
# FastAPI setup
# ---------------------------
app = FastAPI(title="Embedding API", version="1.0.0")

class EmbedRequest(BaseModel):
    text: str

def embed_text(text: str):
    with torch.no_grad():
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text must be a non-empty string.")
        embedding = model.encode(text, task="text-matching")
        return embedding.tolist()

@app.get("/")
def root():
    return {"status": "ok", "message": "Embedding API is running 🚀"}

@app.get("/health")
def health_check():
    return {"device": device, "model_name": model_name, "status": "ready"}

@app.post("/embed")
def get_embedding(req: EmbedRequest):
    try:
        embedding = embed_text(req.text)
        return {"embedding": embedding}
    except Exception as e:
        return {"error": str(e)}
    
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)