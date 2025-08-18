
import boto3
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from botocore.exceptions import NoCredentialsError, ClientError
import magic
import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Configurações do S3 a partir de variáveis de ambiente
S3_BUCKET = os.getenv("S3_BUCKET")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    public: bool = Query(False, description="Se true, torna o arquivo publicamente acessível")
):
    if not all([S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION]):
        raise HTTPException(status_code=500, detail="Credenciais da AWS ou nome do bucket não configurados no servidor.")

    try:
        # Usando python-magic para detectar o tipo de conteúdo de forma mais segura
        mime_type = magic.from_buffer(file.file.read(2048), mime=True)
        file.file.seek(0)

        # Gerar nome único para evitar conflitos
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Configurar ExtraArgs baseado na opção public
        extra_args = {'ContentType': mime_type}
        if public:
            extra_args['ACL'] = 'public-read'

        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET,
            unique_filename,
            ExtraArgs=extra_args
        )
        
        # Gerar um ID único para o arquivo 
        file_id = f"file_{uuid.uuid4()}"
        
        if public:
            # URL pública direta
            file_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"
        else:
            # URL assinada válida por 24 horas para arquivos privados
            file_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': S3_BUCKET, 'Key': unique_filename},
                ExpiresIn=86400  # 24 horas
            )
        
        return {
            "message": "Arquivo enviado com sucesso!", 
            "url": file_url,
            "id": file_id,
            "filename": unique_filename,
            "original_name": file.filename,
            "public": public,
            "content_type": mime_type
        }

    except NoCredentialsError:
        raise HTTPException(status_code=403, detail="Credenciais da AWS não encontradas.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar o arquivo: {str(e)}")


@router.get("/signed-url/{filename}")
async def get_signed_url(
    filename: str,
    expires_in: int = Query(3600, description="Tempo de expiração em segundos (padrão: 1 hora)")
):
    """Gera uma URL assinada para acessar um arquivo privado"""
    if not all([S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION]):
        raise HTTPException(status_code=500, detail="Credenciais da AWS não configurados.")
    
    try:
        # Verificar se o arquivo existe
        s3_client.head_object(Bucket=S3_BUCKET, Key=filename)
        
        # Gerar URL assinada
        signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': filename},
            ExpiresIn=expires_in
        )
        
        return {
            "signed_url": signed_url,
            "expires_in": expires_in,
            "expires_at": (datetime.now() + timedelta(seconds=expires_in)).isoformat()
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        else:
            raise HTTPException(status_code=500, detail=f"Erro ao acessar arquivo: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
