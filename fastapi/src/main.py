import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from controller import post_controller, sign_controller, test_controller
from entity.like_entity import LikeEntity
from entity.post_entity import PostEntity
from entity.user_entity import UserEntity
from fastapi import FastAPI

from middleware.jwt_middleware import JwtMiddleware

app = FastAPI()

# cors 설정 미들웨어
origins = ["http://localhost:3000", "http://52.78.101.85:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(JwtMiddleware)

# app.include_router(test_controller.router)
app.include_router(sign_controller.router)
app.include_router(post_controller.router)


if __name__ == "__main__":
    # TODO 테스트
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    # TODO 배포
    # uvicorn.run("main:app", host="0.0.0.0", port=8000)
