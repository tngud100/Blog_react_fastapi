
from pydantic import BaseModel
from fastapi import File, UploadFile

class infoImage(BaseModel):
    post_idx: int
    user_idx: int
    path: str
    name: str
    type: str
    size: int

class reqImage(BaseModel):
    image: UploadFile = File(...)

class resImage(BaseModel):
    class Config:
        from_attributes = True

    @staticmethod
    def toDTO(image_entity: reqImage):
        return resImage(
            post_idx=image_entity.post_idx,
            user_idx=image_entity.user_idx,
            path=image_entity.path,
            name=image_entity.name,
            type=image_entity.type,
            size=image_entity.size
        )


