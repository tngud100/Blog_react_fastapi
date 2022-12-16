from dependencies import get_db
from dto import sign_dto
from fastapi.responses import JSONResponse
from service import sign_service
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/api/v1/sign",
    tags=["sign"]
)

@router.post("/up")
async def sign_up(reqDTO: sign_dto.ReqSignUp, db: Session = Depends(get_db)) -> JSONResponse:
    return sign_service.sign_up(reqDTO, db)
