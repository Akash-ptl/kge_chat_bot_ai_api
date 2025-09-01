# Embedding service for Google Gemma

import httpx
import os
from app.config import settings

GEMMA_EMBEDDING_MODEL = os.getenv("GEMMA_EMBEDDING_MODEL", "embedding-001")

async def generate_embedding(text: str, api_key: str = None) -> list:
	"""
	Calls Google Gemma API to generate embedding for the given text.
	Returns a list of floats (the embedding vector).
	"""
	if api_key is None:
		api_key = settings.GOOGLE_API_KEY
	url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMMA_EMBEDDING_MODEL}:embedContent?key={api_key}"
	payload = {
		"content": {"parts": [{"text": text}]}
	}
	async with httpx.AsyncClient() as client:
		resp = await client.post(url, json=payload)
		try:
			resp.raise_for_status()
		except Exception:
			print("[Embedding API ERROR] Status:", resp.status_code)
			print("[Embedding API ERROR] Response:", resp.text)
			raise
		data = resp.json()
		# The actual path to the embedding vector may differ; adjust as needed
		return data["embedding"]["values"]
