from fastapi import FastAPI, File, UploadFile, status, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import boto3
import os

from task import process_file_task

load_dotenv()

bucket = os.getenv("MINIO_BUCKET_NAME")

s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv("MINIO_ENDPOINT"),
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY")
)

app = FastAPI()

@app.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_file(file: UploadFile = File(...)):
    try:
        s3_client.upload_fileobj(
            file.file,
            bucket,
            file.filename,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )

        process_file_task.delay(file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar para o MinIO: {str(e)}"
        )
    finally:
        file.file.close()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "Arquivo recebido com sucesso. Processamento agendado"
    }

@app.get("/download/{filename}")
async def download_file(filename: str):
    try: 
        s3_response = s3_client.get_object(
            Bucket = bucket,
            Key = filename,
        )

        return StreamingResponse(
            s3_response['Body'].iter_chunks(),
            media_type=s3_response.get('ContentType', 'application/octet-stream'),
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado ou conversão ainda em andamento"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao encontrar arquivo no MinIO: {str(e)}"
        )