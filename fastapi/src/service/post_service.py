import time
from datetime import datetime

import bcrypt
import jwt
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from config import constants
from dto import post_dto, sign_dto
from entity.post_entity import PostEntity
from entity.user_entity import UserEntity
from fastapi import Request
from util import functions

AUTHORIZATION_ERROR = {"code": 1, "message": "인증되지 않은 사용자입니다."}
ID_ERROR = {"code": 2, "message": "계정에 문제가 있습니다."}
POST_NOT_EXIST_ERROR = {"code": 3, "message": "해당 글이 없습니다."}
CANT_DELETE_OTHERS_POST_ERROR = {"code": 4, "message": "삭제 권한이 없습니다."}
CANT_UPDATE_OTHERS_POST_ERROR = {"code": 5, "message": "수정 권한이 없습니다."}
INTERNAL_SERVER_ERROR = {"code": 99, "message": "서버 내부 에러입니다."}


def delete_post(request: Request, post_idx: int, db: Session) -> JSONResponse:
    if not request.state.user:
        return functions.res_generator(status_code=401, error_dict=AUTHORIZATION_ERROR)

    auth_user: sign_dto.AccessJwt = request.state.user

    # 실제 데이터 삭제시에는 아래와 같이 한다.
    # 글 지운다 -> 글과 연관된 테이블의 데이터 삭제
    # 1. 좋아요 테이블에서 데이터 삭제
    # 2. 글 삭제

    # 여기서는 update 방식으로 글 삭제 진행
    post_entity: PostEntity = db.query(PostEntity).filter(
        PostEntity.idx == post_idx).filter(
            PostEntity.delete_date == None).first()

    if (post_entity == None):
        return functions.res_generator(400, POST_NOT_EXIST_ERROR)

    if (post_entity.user_idx != auth_user.idx):
        return functions.res_generator(400, CANT_DELETE_OTHERS_POST_ERROR)

    try:
        post_entity.delete_date = datetime.now()
        db.flush()
    except Exception as e:
        db.rollback()
        print(e)
        return functions.res_generator(status_code=500, error_dict=INTERNAL_SERVER_ERROR, content=e)
    finally:
        db.commit()

    return functions.res_generator()


def get_post(request: Request, post_idx: int, update: bool, db: Session) -> JSONResponse:
    auth_user: sign_dto.AccessJwt | None = request.state.user

    # update가 true면 ResSetUpdatePost / false면 ResDetailPost

    if update:
        # auth_user == None
        if not auth_user:
            return functions.res_generator(401, AUTHORIZATION_ERROR)

        post_entity: PostEntity = db.query(PostEntity).filter(
            PostEntity.idx == post_idx).filter(
            PostEntity.delete_date == None).first()

        if post_entity == None:
            return functions.res_generator(400, POST_NOT_EXIST_ERROR)

        if (post_entity.user_idx != auth_user.idx):
            return functions.res_generator(400, CANT_UPDATE_OTHERS_POST_ERROR)

        return functions.res_generator(content=post_dto.ResSetUpdatePost.toDTO(post_entity))
    else:
        post_entity: PostEntity = db.query(PostEntity).filter(
            PostEntity.idx == post_idx).filter(
            PostEntity.delete_date == None).first()

        if post_entity == None:
            return functions.res_generator(400, POST_NOT_EXIST_ERROR)

        return functions.res_generator(content=post_dto.ResDetailPost.toDTO(post_entity, auth_user))


def get_posts(db: Session):
    post_entity_list: list[PostEntity] = db.query(
        PostEntity).filter(PostEntity.delete_date == None).order_by(
            PostEntity.create_date.desc()).all()

    res_main_post_list = list(
        map(post_dto.ResMainPost.toDTO, post_entity_list))

    return functions.res_generator(content=res_main_post_list)


def insert_post(request: Request, req_dto: post_dto.ReqInsertPost, db: Session) -> JSONResponse:
    if not request.state.user:
        return functions.res_generator(status_code=401, error_dict=AUTHORIZATION_ERROR)

    auth_user: sign_dto.AccessJwt = request.state.user

    user_entity: UserEntity = db.query(UserEntity).filter(
        UserEntity.idx == auth_user.idx).filter(
            UserEntity.delete_date == None).first()

    if (user_entity == None):
        return functions.res_generator(400, ID_ERROR)

    new_post = PostEntity(
        title=req_dto.title,
        content=req_dto.content,
        summary=req_dto.summary,
        thumbnail=req_dto.thumbnail,
        user_idx=user_entity.idx
    )

    try:
        db.add(new_post)
        db.flush()
    except Exception as e:
        db.rollback()
        print(e)
        return functions.res_generator(status_code=500, error_dict=INTERNAL_SERVER_ERROR, content=e)
    finally:
        db.commit()

    db.refresh(new_post)

    return functions.res_generator(status_code=201, content=post_dto.ResInsertPost(idx=new_post.idx))
