

from fastapi import APIRouter, HTTPException, Body, UploadFile, File
from app.db import app_content_collection, app_collection
import base64
def decrypt_api_key(enc_key: str) -> str:
	try:
		return base64.b64decode(enc_key.encode()).decode()
	except Exception:
		return enc_key
from app.services.embedding import generate_embedding
import PyPDF2
import aiofiles
import httpx
from ...models.content import DocumentContent
from typing import List
import uuid

router = APIRouter(prefix="/api/v1/admin/app/{app_id}/documents", tags=["Admin Documents"])

def to_dict(obj):
	if isinstance(obj, dict):
		return {k: to_dict(v) for k, v in obj.items()}
	if isinstance(obj, list):
		return [to_dict(i) for i in obj]
	# No ObjectId conversion needed; all IDs are strings
	return obj


 # POST /api/v1/admin/app/{app_id}/documents
@router.post("", response_model=dict)
async def create_document(app_id: str, document: DocumentContent = Body(...)):
	app = await app_collection.find_one({"_id": app_id})
	if not app or not app.get("googleApiKey"):
		raise HTTPException(status_code=400, detail="App or Google API key not found")
	api_key = decrypt_api_key(app["googleApiKey"])

	extracted_text = None
	import tempfile
	import os
	if document.file:
		import base64
		file_bytes = base64.b64decode(document.file)
		async with aiofiles.tempfile.NamedTemporaryFile('wb+', delete=True, suffix='.pdf') as tmp:
			await tmp.write(file_bytes)
			await tmp.flush()
			try:
				await tmp.seek(0)
				reader = PyPDF2.PdfReader(tmp.name)
				extracted_text = " ".join([page.extract_text() or "" for page in reader.pages])
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
						extracted_text = " ".join([page.extract_text() or "" for page in reader.pages])
					except Exception:
						raise HTTPException(status_code=400, detail="Failed to extract PDF text from URL")
		except Exception:
			raise HTTPException(status_code=400, detail="Failed to download PDF")
	else:
		raise HTTPException(status_code=400, detail="Either file or url must be provided.")

	if not extracted_text or not extracted_text.strip():
		raise HTTPException(status_code=400, detail="No text could be extracted from the PDF.")

	embedding = await generate_embedding(extracted_text, api_key)
	doc = {
		"_id": str(uuid.uuid4()),
		"app_id": app_id,
		"contentType": "document",
		"content": document.dict(),
		"embedding": embedding,
		"extractedText": extracted_text[:10000]  # Store up to 10k chars for reference
	}
	await app_content_collection.insert_one(doc)
	return {"id": doc["_id"]}

 # GET /api/v1/admin/app/{app_id}/documents
@router.get("", response_model=List[dict])
async def list_documents(app_id: str):
	docs = await app_content_collection.find({"app_id": app_id, "contentType": "document"}).to_list(100)
	return [to_dict(d) for d in docs] if docs else []


# PUT /api/v1/admin/app/{app_id}/documents/{document_id}

async def extract_pdf_text(document: DocumentContent) -> str:
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


@router.put("/{document_id}", response_model=dict)
async def update_document(app_id: str, document_id: str, document: DocumentContent = Body(...)):
	app = await app_collection.find_one({"_id": app_id})
	if not app or not app.get("googleApiKey"):
		raise HTTPException(status_code=400, detail="App or Google API key not found")
	api_key = decrypt_api_key(app["googleApiKey"])

	extracted_text = await extract_pdf_text(document)
	if not extracted_text or not extracted_text.strip():
		raise HTTPException(status_code=400, detail="No text could be extracted from the PDF.")

	embedding = await generate_embedding(extracted_text, api_key)
	update_result = await app_content_collection.update_one(
			   {"_id": document_id, "contentType": "document", "app_id": app_id},
		{"$set": {"content": document.dict(), "embedding": embedding, "extractedText": extracted_text[:10000]}}
	)
	if update_result.modified_count == 0:
		raise HTTPException(status_code=404, detail="Document not found or data unchanged")
	return {"message": "Document updated successfully"}

# DELETE /api/v1/admin/app/{app_id}/documents/{document_id}
@router.delete("/{document_id}", response_model=dict)
async def delete_document(app_id: str, document_id: str):
	# Remove the document and its embedding
	delete_result = await app_content_collection.delete_one({"_id": document_id, "contentType": "document", "app_id": app_id})
	if delete_result.deleted_count == 0:
		raise HTTPException(status_code=404, detail="Document not found")
	return {"message": "Document deleted successfully"}
