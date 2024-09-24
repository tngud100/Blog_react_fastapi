
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.database import DBase
from sqlalchemy.schema import PrimaryKeyConstraint

class ImageEntity(DBase):
  __tablename__ = "Image"

  idx = Column(Integer, primary_key=True, index=True)
  post_idx = Column(Integer, ForeignKey("Post.idx"))
  path = Column(String)  
  name = Column(String)

  post_entity = relationship("PostEntity", back_populates="image_entity_list")
