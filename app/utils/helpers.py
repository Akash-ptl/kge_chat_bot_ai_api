import aiofiles
import PyPDF2
import httpx
from fastapi import HTTPException

async def extract_pdf_text_from_document(document):
	import tempfile
	import os
	import base64
	if document.file:
		file_bytes = base64.b64decode(document.file)
		async with aiofiles.tempfile.NamedTemporaryFile('wb+', delete=True, suffix='.pdf') as tmp:
			await tmp.write(file_bytes)
			await tmp.flush()
			try:
				await tmp.seek(0)
				reader = PyPDF2.PdfReader(tmp.name)
				return " ".join([page.extract_text() or "" for page in reader.pages])
			except Exception:
				raise HTTPException(status_code=400, detail="Failed to extract PDF text")
	elif document.url:
		try:
			async with httpx.AsyncClient() as client:
				resp = await client.get(document.url)
				resp.raise_for_status()
				async with aiofiles.tempfile.NamedTemporaryFile('wb+', delete=True, suffix='.pdf') as tmp:
					await tmp.write(resp.content)
					await tmp.flush()
					try:
						await tmp.seek(0)
						reader = PyPDF2.PdfReader(tmp.name)
						return " ".join([page.extract_text() or "" for page in reader.pages])
					except Exception:
						raise HTTPException(status_code=400, detail="Failed to extract PDF text from URL")
		except Exception:
			raise HTTPException(status_code=400, detail="Failed to download PDF")
	else:
		raise HTTPException(status_code=400, detail="Either file or url must be provided.")
from fastapi import HTTPException

def get_valid_api_key(app):
	if not app or not app.get("googleApiKey"):
		raise HTTPException(status_code=400, detail="App or Google API key not found")
	from app.routers.admin.urls import decrypt_api_key  # adjust import if needed
	return decrypt_api_key(app["googleApiKey"])

async def safe_generate_embedding(text, api_key):
	try:
		from app.services.embedding import generate_embedding
		return await generate_embedding(text, api_key)
	except Exception as e:
		print(f"Embedding error details: {str(e)}")
		raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")

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
