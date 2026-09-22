from celery import Celery
from dotenv import load_dotenv
import boto3
import os
import tempfile

load_dotenv()
redis_url = os.getenv("REDIS_URL")
s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv("MINIO_ENDPOINT"),
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY")
)

app = Celery("tasks", broker=redis_url)

@app.task
def process_file_task(filename: str):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_original = os.path.join(tmpdir, filename)
            caminho_processado = os.path.join(tmpdir, f"processado_{filename}")

            print("f[{filename}] Baixando o arquivo...")
            s3_client.download_file(
                Bucket=os.getenv("MINIO_BUCKET_NAME"),
                Key=filename,
                Filename=caminho_original
            )

            print(f"[{filename}] Processando...")
            with open(caminho_processado, 'w') as file:
                file.write(f"O arquivo {filename} foi processado pelo Celery!")

            print(f"[{filename}] Enviando reultado de volta...")
            s3_client.upload_file(
                Filename=caminho_processado,
                Bucket=os.getenv("MINIO_BUCKET_NAME"),
                Key=f"processado_{filename}"
            )

            print(f"[{filename}] Fluxo conclupido com sucesso!")
    except Exception as e:
        print(f"Erro ao processar arquivo: {e}")
