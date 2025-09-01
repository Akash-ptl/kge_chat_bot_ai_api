

from fastapi import APIRouter, HTTPException, Body, UploadFile, File
from app.db import app_content_collection, app_collection
import base64
def decrypt_api_key(enc_key: str) -> str:
	try:
		return base64.b64decode(enc_key.encode()).decode()
	except Exception:
		return enc_key
from app.utils.helpers import get_valid_api_key, safe_generate_embedding, build_doc_dict
from app.utils.helpers import extract_pdf_text_from_document
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
	api_key = await get_valid_api_key(app)

	extracted_text = await extract_pdf_text_from_document(document)
	if not extracted_text or not extracted_text.strip():
		raise HTTPException(status_code=400, detail="No text could be extracted from the PDF.")
	embedding = await safe_generate_embedding(extracted_text, api_key)
	doc = build_doc_dict(app_id, "document", document.dict(), embedding, extra={"extractedText": extracted_text[:10000]})
	await app_content_collection.insert_one(doc)
	return {"id": doc["_id"]}

 # GET /api/v1/admin/app/{app_id}/documents
@router.get("", response_model=List[dict])
async def list_documents(app_id: str):
	docs = await app_content_collection.find({"app_id": app_id, "contentType": "document"}).to_list(100)
	return [to_dict(d) for d in docs] if docs else []


# PUT /api/v1/admin/app/{app_id}/documents/{document_id}



@router.put("/{document_id}", response_model=dict)
async def update_document(app_id: str, document_id: str, document: DocumentContent = Body(...)):
	app = await app_collection.find_one({"_id": app_id})
	api_key = await get_valid_api_key(app)

	extracted_text = await extract_pdf_text_from_document(document)
	if not extracted_text or not extracted_text.strip():
		raise HTTPException(status_code=400, detail="No text could be extracted from the PDF.")

	embedding = await safe_generate_embedding(extracted_text, api_key)
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
