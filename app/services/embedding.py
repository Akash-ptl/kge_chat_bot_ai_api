# Embedding service for Google Gemma
import httpx
import os

GEMMA_EMBEDDING_MODEL = os.getenv("GEMMA_EMBEDDING_MODEL", "embedding-001")

async def generate_embedding(text: str, api_key: str) -> list:
	"""
	Calls Google Gemma API to generate embedding for the given text.
	Returns a list of floats (the embedding vector).
	"""
	url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMMA_EMBEDDING_MODEL}:embedContent?key={api_key}"
	payload = {
		"content": {"parts": [{"text": text}]}
	}
	async with httpx.AsyncClient() as client:
		resp = await client.post(url, json=payload)
		try:
			resp.raise_for_status()
		except Exception as e:
			print("[Embedding API ERROR] Status:", resp.status_code)
			print("[Embedding API ERROR] Response:", resp.text)
			raise
		data = resp.json()
		# The actual path to the embedding vector may differ; adjust as needed
		return data["embedding"]["values"]
