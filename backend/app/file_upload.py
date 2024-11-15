from fastapi import UploadFile
from fastapi import APIRouter, UploadFile, HTTPException, status, Depends
from typing import Annotated
from sqlalchemy.orm import Session
import boto3
from urllib.parse import unquote
import os
from dotenv import load_dotenv
import logging
import uuid

from .unstructured_parser import create_embeddings_and_index, parse_document
from .models import Files, Documents, DocumentMetadata
from .database import SessionLocal
from .auth import get_current_user
from .unstructured_parser import parse_document

# Load environment variables
load_dotenv()

# AWS S3 configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
OPEN_API_KEY = os.getenv("OPENAI_API_KEY")

# Boto3 S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

router = APIRouter(
    prefix="/files",
    tags=["file_upload"]
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_file(file: UploadFile, db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    try:
        logger.info("Starting file upload process...")
        logger.info(
            f"Received file: {file.filename}, content type: {file.content_type}")

        # Read the file contents into bytes before uploading
        file_contents = await file.read()
        file_size = len(file_contents)

        if file_size == 0:
            logger.error("Uploaded file is empty.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

        logger.info(f"File contents size: {file_size} bytes")

        # Create a user-specific directory (e.g., based on user ID)
        # Temporary directory inside the app folder
        user_dir = f"app/tmp/{user['id']}/"
        os.makedirs(user_dir, exist_ok=True)

        # Save the file locally in the user-specific folder
        local_file_path = os.path.join(
            user_dir, f"{uuid.uuid4()}_{file.filename}")
        with open(local_file_path, "wb") as f:
            f.write(file_contents)

        # Upload the file to S3
        file_key = f"{user['id']}/{uuid.uuid4()}_{file.filename}"
        response = s3_client.put_object(
            Bucket=S3_BUCKET_NAME, Key=file_key, Body=file_contents)
        logger.info(f"Response from S3: {response}")

        # Generate the file URL from S3
        file_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_key}"
        logger.info(f"File URL: {file_url}")

        # Save file metadata to DB
        file_metadata = Files(file_name=file.filename,
                              file_url=file_url, user_id=user["id"])
        db.add(file_metadata)
        db.commit()
        logger.info("File metadata saved to database.")

        # Parse the document using unstructured.io and generate embeddings
        parsed_data = parse_document(local_file_path, file.content_type)
        logger.info(f"Parsed document data: {parsed_data}")

        # Save parsed metadata to DB
        new_document = Documents(
            owner_id=user["id"], document_name=file.filename, document_type=file.content_type, s3_url=file_url)
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        if parsed_data['metadata']:
            for key, value in parsed_data['metadata'].items():
                if key and value:  # Ensure metadata key-value pairs are valid
                    new_metadata = DocumentMetadata(
                        document_id=new_document.id,
                        metadata_key=key,
                        metadata_value=str(value)  # Ensure value is a string
                    )
                    db.add(new_metadata)
            db.commit()

        # Now, generate and index vector embeddings
        vector_store = create_embeddings_and_index(
            local_file_path, openai_api_key=OPEN_API_KEY)
        logger.info("Vector embeddings generated and indexed successfully.")

        user_dir = f"app/tmp/{user['id']}/"
        os.makedirs(user_dir, exist_ok=True)
        vector_store_path = os.path.join(
            user_dir, f"{uuid.uuid4()}_vector_store")
        vector_store = create_embeddings_and_index(local_file_path)

        vector_store.save_to_disk(vector_store_path)
        logger.info(f"Vector store saved at {vector_store_path}")

        return {"file_url": file_url, "message": "File uploaded, metadata saved, and embeddings indexed successfully"}

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred")


@router.get("/download/{file_name}", status_code=status.HTTP_200_OK)
async def get_file_url(file_name: str, db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    logger.info(f"Generating pre-signed URL for file: {file_name}")

    # Verify the file exists in the database
    file_record = db.query(Files).filter(
        Files.file_name == file_name, Files.user_id == user["id"]).first()
    if not file_record:
        logger.error(f"File not found in database: {file_name}")
        raise HTTPException(
            status_code=404, detail="File not found in database")

    try:
        # Generate the full S3 key for the file
        file_key = f"{user['id']}/{file_name}"

        # Generate a pre-signed URL for downloading the file
        file_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': file_key},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        logger.info(f"Pre-signed URL generated: {file_url}")

        return {"file_url": file_url}

    except s3_client.exceptions.NoSuchKey:
        logger.error(f"No such key: {file_key}")
        raise HTTPException(status_code=404, detail="File not found in S3")
    except Exception as e:
        logger.error(f"Error generating pre-signed URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/list", status_code=status.HTTP_200_OK)
async def list_user_files(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    try:
        files = db.query(Files).filter(Files.user_id == user["id"]).all()
        file_list = [{"file_name": file.file_name,
                      "file_url": file.file_url,
                      "s3_key": f"{user['id']}/{file.file_name}"} for file in files]
        return {"files": file_list}

    except Exception as e:
        logger.error(f"Error fetching files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/delete/{file_name}", status_code=status.HTTP_200_OK)
async def delete_file(file_name: str, db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    decoded_file_name = unquote(file_name)
    logger.info(
        f"User {user['id']} attempting to delete file: {decoded_file_name}")

    # Find the file record in the files table
    file_record = db.query(Files).filter(
        Files.file_name == decoded_file_name, Files.user_id == user["id"]).first()
    if not file_record:
        logger.error(
            f"File not found or does not belong to user: {decoded_file_name}")
        raise HTTPException(
            status_code=404, detail="File not found or you do not have permission to delete this file")

    try:
        # Generate the full S3 key for the file
        file_key = f"{user['id']}/{file_record.file_name}"
        logger.info(f"Deleting key: {file_key}")

        # Delete the file from S3
        response = s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=file_key)
        logger.info(f"Response from S3: {response}")

        # Check if the S3 deletion was successful
        if response['ResponseMetadata']['HTTPStatusCode'] == 204:
            logger.info(f"File {file_key} successfully deleted from S3.")
        else:
            logger.warning(
                f"Failed to delete file {file_key} from S3. Response: {response}")
            raise HTTPException(
                status_code=500, detail="Failed to delete file from S3")

        # Delete the file record from the files table
        db.delete(file_record)
        db.commit()
        logger.info("File metadata deleted from files table.")

        # Delete the document record from the documents table
        document_record = db.query(Documents).filter(
            Documents.document_name == decoded_file_name, Documents.owner_id == user["id"]).first()
        if document_record:
            db.delete(document_record)
            db.commit()
            logger.info("Document metadata deleted from documents table.")

        return {"message": "File and document metadata deleted successfully"}

    except s3_client.exceptions.NoSuchKey:
        logger.error(f"No such key: {file_key}")
        raise HTTPException(status_code=404, detail="File not found in S3")
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        logger.exception(e)  # Add this to log the full stack trace
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
