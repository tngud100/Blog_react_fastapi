from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 데이터베이스 URL 설정
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:0000@localhost:3306/jaylog"

# 엔진 생성
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 세션 로컬 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 베이스 클래스 정의
DBase = declarative_base()

# 연결 테스트
def test_connection():
    try:
        # 엔진을 통해 연결을 시도
        with engine.connect() as connection:
            print("데이터베이스 연결 성공!")
    except Exception as e:
        print(f"데이터베이스 연결 실패: {e}")

# 연결 테스트 실행
test_connection()

