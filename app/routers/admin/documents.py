

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
import tempfile
import requests
from ...models.content import DocumentContent
from typing import List
import uuid

router = APIRouter(prefix="/api/v1/admin/app/{appId}/documents", tags=["Admin Documents"])

def to_dict(obj):
	if isinstance(obj, dict):
		return {k: to_dict(v) for k, v in obj.items()}
	if isinstance(obj, list):
		return [to_dict(i) for i in obj]
	# No ObjectId conversion needed; all IDs are strings
	return obj


# POST /api/v1/admin/app/{appId}/documents
@router.post("", response_model=dict)
async def create_document(appId: str, document: DocumentContent = Body(...)):
	app = await app_collection.find_one({"_id": appId})
	if not app or not app.get("googleApiKey"):
		raise HTTPException(status_code=400, detail="App or Google API key not found")
	api_key = decrypt_api_key(app["googleApiKey"])

	extracted_text = None
	if document.file:
		# file is base64-encoded bytes
		import base64
		file_bytes = base64.b64decode(document.file)
		with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as tmp:
			tmp.write(file_bytes)
			tmp.flush()
			try:
				reader = PyPDF2.PdfReader(tmp.name)
				extracted_text = " ".join([page.extract_text() or "" for page in reader.pages])
			except Exception as e:
				raise HTTPException(status_code=400, detail=f"Failed to extract PDF text: {e}")
	elif document.url:
		# Download PDF from URL
		try:
			resp = requests.get(document.url)
			resp.raise_for_status()
			with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as tmp:
				tmp.write(resp.content)
				tmp.flush()
				try:
					reader = PyPDF2.PdfReader(tmp.name)
					extracted_text = " ".join([page.extract_text() or "" for page in reader.pages])
				except Exception as e:
					raise HTTPException(status_code=400, detail=f"Failed to extract PDF text from URL: {e}")
		except Exception as e:
			raise HTTPException(status_code=400, detail=f"Failed to download PDF: {e}")
	else:
		raise HTTPException(status_code=400, detail="Either file or url must be provided.")

	if not extracted_text or not extracted_text.strip():
		raise HTTPException(status_code=400, detail="No text could be extracted from the PDF.")

	embedding = await generate_embedding(extracted_text, api_key)
	doc = {
		"_id": str(uuid.uuid4()),
		"appId": appId,
		"contentType": "document",
		"content": document.dict(),
		"embedding": embedding,
		"extractedText": extracted_text[:10000]  # Store up to 10k chars for reference
	}
	result = await app_content_collection.insert_one(doc)
	return {"id": doc["_id"]}

# GET /api/v1/admin/app/{appId}/documents
@router.get("", response_model=List[dict])
async def list_documents(appId: str):
	docs = await app_content_collection.find({"appId": appId, "contentType": "document"}).to_list(100)
	return [to_dict(d) for d in docs] if docs else []


# PUT /api/v1/admin/app/{appId}/documents/{documentId}
@router.put("/{documentId}", response_model=dict)
async def update_document(appId: str, documentId: str, document: DocumentContent = Body(...)):
	app = await app_collection.find_one({"_id": appId})
	if not app or not app.get("googleApiKey"):
		raise HTTPException(status_code=400, detail="App or Google API key not found")
	api_key = decrypt_api_key(app["googleApiKey"])

	extracted_text = None
	if document.file:
		import base64
		file_bytes = base64.b64decode(document.file)
		with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as tmp:
			tmp.write(file_bytes)
			tmp.flush()
			try:
				reader = PyPDF2.PdfReader(tmp.name)
				extracted_text = " ".join([page.extract_text() or "" for page in reader.pages])
			except Exception as e:
				raise HTTPException(status_code=400, detail=f"Failed to extract PDF text: {e}")
	elif document.url:
		try:
			resp = requests.get(document.url)
			resp.raise_for_status()
			with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as tmp:
				tmp.write(resp.content)
				tmp.flush()
				try:
					reader = PyPDF2.PdfReader(tmp.name)
					extracted_text = " ".join([page.extract_text() or "" for page in reader.pages])
				except Exception as e:
					raise HTTPException(status_code=400, detail=f"Failed to extract PDF text from URL: {e}")
		except Exception as e:
			raise HTTPException(status_code=400, detail=f"Failed to download PDF: {e}")
	else:
		raise HTTPException(status_code=400, detail="Either file or url must be provided.")

	if not extracted_text or not extracted_text.strip():
		raise HTTPException(status_code=400, detail="No text could be extracted from the PDF.")

	embedding = await generate_embedding(extracted_text, api_key)
	update_result = await app_content_collection.update_one(
		{"_id": documentId, "contentType": "document", "appId": appId},
		{"$set": {"content": document.dict(), "embedding": embedding, "extractedText": extracted_text[:10000]}}
	)
	if update_result.modified_count == 0:
		raise HTTPException(status_code=404, detail="Document not found or data unchanged")
	return {"message": "Document updated successfully"}

# DELETE /api/v1/admin/app/{appId}/documents/{documentId}
@router.delete("/{documentId}", response_model=dict)
async def delete_document(appId: str, documentId: str):
	# Remove the document and its embedding
	delete_result = await app_content_collection.delete_one({"_id": documentId, "contentType": "document", "appId": appId})
	if delete_result.deleted_count == 0:
		raise HTTPException(status_code=404, detail="Document not found")
	return {"message": "Document deleted successfully"}
