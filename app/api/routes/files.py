from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.schemas.file_schema import FileUploadResponse, FileListResponse, FileRead
from app.services.file_service import FileService
from app.services.minio_service import MinioService
from app.core.exceptions import AppError
from io import BytesIO

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Загрузить новый файл.
    
    - Поддерживаются файлы любого расширения
    - Размер ограничен вашей конфигурацией сервера
    - Файл будет доступен через endpoint `/files/{file_id}/download`
    """
    try:
        # Читаем содержимое файла
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )

        # Создаем сервисы
        minio_service = MinioService()
        file_service = FileService(db, minio_service)

        # Загружаем файл
        uploaded_file = file_service.upload_file(
            file_data=file_content,
            file_name=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
            user_id=current_user.id,
        )

        return uploaded_file

    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/my/files", response_model=list[FileListResponse])
def list_user_files(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Получить список загруженных мной файлов.
    
    - Возвращает только файлы текущего пользователя
    - Поддерживает пагинацию через параметры skip и limit
    """
    try:
        minio_service = MinioService()
        file_service = FileService(db, minio_service)
        return file_service.list_user_files(current_user.id, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list user files: {str(e)}"
        )


@router.get("/", response_model=list[FileListResponse])
def list_all_files(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Получить список всех загруженных файлов.
    
    - Возвращает информацию обо всех файлах в системе
    - Поддерживает пагинацию через параметры skip и limit
    """
    try:
        minio_service = MinioService()
        file_service = FileService(db, minio_service)
        return file_service.list_all_files(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )


@router.get("/{file_id}", response_model=FileRead)
def get_file_info(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Получить информацию о файле по ID.
    
    Возвращает метаданные: имя, размер, тип контента, URL доступа.
    """
    try:
        minio_service = MinioService()
        file_service = FileService(db, minio_service)
        return file_service.get_file(file_id)
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/{file_id}/download")
async def download_file(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Скачать файл.
    
    Возвращает файл в виде потока данных.
    """
    try:
        minio_service = MinioService()
        file_service = FileService(db, minio_service)
        
        file_data, file_name, content_type = file_service.download_file(file_id)
        
        return StreamingResponse(
            BytesIO(file_data),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File download failed: {str(e)}"
        )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Удалить файл.
    
    - Может удалить файл только пользователь, загрузивший его, или администратор
    - Файл будет помечен как удаленный (мягкое удаление)
    """
    try:
        minio_service = MinioService()
        file_service = FileService(db, minio_service)
        file_service.delete_file(file_id, current_user.id)
        return None
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File deletion failed: {str(e)}"
        )
