# Async File Processor (FastAPI + Celery + MinIO + Redis)

Este projeto é uma arquitetura de referência para o processamento assíncrono de arquivos. Ele resolve o problema comum de APIs que precisam receber arquivos, realizar processamentos pesados (como conversões, relatórios, extração de dados) e devolver o resultado ao usuário sem travar ou causar lentidão no servidor (Timeout).

## Tecnologias Utilizadas

*   **[FastAPI](https://fastapi.tiangolo.com/):** Framework web moderno e de alta performance para a criação da API.
*   **[Celery](https://docs.celeryq.dev/):** Gerenciador de filas de tarefas (Task Queue) para executar o processamento em background.
*   **[Redis](https://redis.io/):** Atua como *Message Broker*, intermediando a comunicação entre a API (FastAPI) e o Worker (Celery).
*   **[MinIO](https://min.io/) / Boto3:** Armazenamento de objetos (Object Storage) compatível com AWS S3 para guardar os arquivos originais e processados.
*   **[Docker](https://www.docker.com/):** Orquestração da infraestrutura local (Redis e MinIO).

## Arquitetura e Fluxo

1. O usuário faz o **Upload** de um arquivo via endpoint `POST /upload`.
2. A API salva o arquivo original diretamente no **MinIO (S3)**.
3. A API envia uma mensagem para o **Redis** dizendo: *"Processe esse arquivo"*, e responde imediatamente ao usuário (HTTP 202 Accepted).
4. O **Celery Worker** lê a mensagem no Redis, baixa o arquivo do MinIO, realiza o processamento em uma pasta temporária, e faz o upload do resultado de volta para o MinIO com o prefixo `processado_`.
5. O usuário faz o **Download** do arquivo final via endpoint `GET /download/processado_nome-do-arquivo.ext`.
