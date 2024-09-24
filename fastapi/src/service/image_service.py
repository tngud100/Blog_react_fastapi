import os
from fastapi import UploadFile
import shutil
import time
import re

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from dto import post_dto, sign_dto, image_dto
from entity.user_entity import UserEntity
from entity.image_entity import ImageEntity
from util import functions
from config.constants import URL_PATH

AUTHORIZATION_ERROR = {"code": 1, "message": "인증되지 않은 사용자입니다."}
ID_ERROR = {"code": 2, "message": "계정에 문제가 있습니다."}

IMAGE_NAME_ERROR = {"code": 50, "message": "이미지의 이름에 '.'와 '/'(이)가 있으면 등록 할 수 없습니다."}

IMAGE_TYPE_ERROR = {"code": 51, "message": "SVG, PNG, JPG, JPEG 파일만 업로드 가능합니다."}
IMAGE_NOT_EXIST_ERROR = {"code": 52, "message": "해당 게시글에 이미지가 존재하지 않습니다."}

INTERNAL_SERVER_ERROR = {"code": 99, "message": "서버 내부 에러입니다."}

def save_image(image: UploadFile, image_file_name: str) -> str:
    # 파일 저장 경로 설정 (static/images/ 폴더)

    upload_dir = "static/images"
    
    # 파일 경로 설정
    file_path = os.path.join(upload_dir, image_file_name)
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 파일을 바이너리로 저장
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    return f'{URL_PATH}{file_path}'  # 저장된 파일 경로 반환 


def upload_image(request: Request, image: UploadFile, db: Session) -> JSONResponse:
    if not request.state.user:
        return functions.res_generator(status_code=401, error_dict=AUTHORIZATION_ERROR)

    auth_user: sign_dto.AccessJwt = request.state.user

    user_entity: UserEntity = db.query(UserEntity).filter(
        UserEntity.idx == auth_user.idx).filter(
            UserEntity.delete_date == None).first()

    if user_entity is None:
        return functions.res_generator(status_code=402, error_dict=ID_ERROR)

    # 이미지는 svg, png, jpg, jpeg만 허용
    if not image.content_type in ["image/svg+xml", "image/png", "image/jpg", "image/jpeg"]:
        return functions.res_generator(status_code=451, error_dict=IMAGE_TYPE_ERROR)


    filename, file_extension = os.path.splitext(image.filename)

    if re.search(r'[./]', filename):
        return functions.res_generator(status_code=450, error_dict=IMAGE_NAME_ERROR)

    filename = re.sub(r'\s+', '_', filename)  # 공백을 밑줄로 대체
    
    image_file_name = f"{filename}_{int(time.time())}{file_extension}"

    # 이미지 파일 저장
    image_file_path = save_image(image, image_file_name)
    content = {
        "filename": image.filename,
        "url": image_file_path
    }

    return functions.res_generator(status_code=201, content=content)

def insert_image_db(imageList: list[str], post_idx, db: Session) -> JSONResponse:
    # 이미지 리스트가 있을 경우 처리
    for image in imageList:
        new_image_post = ImageEntity(
            post_idx=post_idx,  # 새로 생성된 post의 idx 사용
            path = image.split(URL_PATH)[1],  # 파일 경로 추출
            name = image.split("\\")[-1].split('_')[0]  # 파일 이름 추출,
        )
        db.add(new_image_post)
        db.flush()

def delete_image_by_path(image_paths: list[str]) -> JSONResponse:
    for image_path in image_paths:
        print(image_path)
        image_path = os.path.abspath(image_path)
        if os.path.exists(image_path):
            os.remove(image_path)
        else:
            return functions.res_generator(452, IMAGE_NOT_EXIST_ERROR)

def delete_image_by_postIdx(post_idx: int, db: Session) -> JSONResponse:
    image_entity_list = db.query(ImageEntity).filter(
        ImageEntity.post_idx == post_idx).all()
    
    if not image_entity_list:
        return functions.res_generator(452, IMAGE_NOT_EXIST_ERROR)
    
    for image_entity in image_entity_list:
        image_path = os.path.abspath(image_entity.path)

        if os.path.exists(image_path):
            os.remove(image_path)
        else:
            return functions.res_generator(452, IMAGE_NOT_EXIST_ERROR)

        db.delete(image_entity)

   
