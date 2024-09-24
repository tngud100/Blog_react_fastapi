from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from dependencies import get_db
from fastapi import APIRouter, Depends, Query, UploadFile, File, Request
from typing import List
from service import image_service
from dto import image_dto


router = APIRouter(
    prefix="/api/v1/images",
    tags=["post"]
)

def delete_image( post_idx : int, db : Session) -> JSONResponse:
    return image_service.delete_image_by_postIdx(post_idx, db)

@router.delete("/exit/editorImage")
async def delete_editorImage(imagePaths: List[str] = Query(..., alias="imagePaths[]")) -> JSONResponse:
    return image_service.delete_image_by_path(imagePaths)

@router.post("/upload")
async def upload_image(
    request: Request,
    image: UploadFile = File(...),  # 파일 업로드를 위해 UploadFile 사용
    db: Session = Depends(get_db)
) -> JSONResponse:
    return image_service.upload_image(request, image, db)