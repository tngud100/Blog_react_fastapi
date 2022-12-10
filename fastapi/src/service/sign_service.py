
import bcrypt
from datetime import datetime
from database.database import DBase
from dto import res_dto, sign_dto
from sqlalchemy.orm import Session

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from entity.user_entity import UserEntity


def sign_up(reqDTO: sign_dto.ReqSignUp, db: Session):
    userEntity: UserEntity = db.query(UserEntity).filter(
        UserEntity.id == reqDTO.id).first()
    if userEntity != None:
        resDTO = res_dto.ResDTO(
            code=1,
            message="이미 존재하는 아이디 입니다."
        )
        encodedResDTO = jsonable_encoder(resDTO)
        return JSONResponse(status_code=400, content=encodedResDTO)
    db_user = UserEntity(
        id=reqDTO.id,
        password=bcrypt.hashpw(
            reqDTO.password.encode("utf-8"), bcrypt.gensalt()),
        simple_desc=reqDTO.simpleDesc if reqDTO.simpleDesc else "한줄 소개가 없습니다.",
        profile_image='https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png',
        role="BLOGER",
        create_date=datetime.now(),
    )
    try:
        db.add(db_user)
        db.flush()
    except Exception as e:
        db.rollBack()
        print(e)
        resDTO = res_dto.ResDTO(
            code=99,
            message="서버 내부 에러 입니다.",
            content=e
        )
        encodedError = jsonable_encoder(resDTO)
        return JSONResponse(status_code=500, content=encodedError)
    finally:
        db.commit()

    db.refresh(db_user)
    resDTO = res_dto.ResDTO(
        code=0,
        message="성공",
        content=sign_dto.ResSignUp(
            idx=db_user.idx
        )
    )
    encodedResDTO = jsonable_encoder(resDTO)
    return JSONResponse(status_code=201, content=encodedResDTO)
