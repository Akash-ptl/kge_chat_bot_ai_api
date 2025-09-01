from fastapi import HTTPException

async def get_valid_api_key(app):
	if not app or not app.get("googleApiKey"):
		raise HTTPException(status_code=400, detail="App or Google API key not found")
	from app.routers.admin.urls import decrypt_api_key  # adjust import if needed
	return decrypt_api_key(app["googleApiKey"])

async def safe_generate_embedding(text, api_key):
	try:
		from app.services.embedding import generate_embedding
		return await generate_embedding(text, api_key)
	except Exception:
		raise HTTPException(status_code=500, detail="Embedding error")

def build_doc_dict(app_id, content_type, content, embedding, extra=None):
	import uuid
	doc = {
		"_id": str(uuid.uuid4()),
		"app_id": app_id,
		"contentType": content_type,
		"content": content,
		"embedding": embedding
	}
	if extra:
		doc.update(extra)
	return doc
