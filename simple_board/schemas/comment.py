from pydantic import BaseModel
from datetime import datetime

# 타입 점검 (pydantic)

class CommentCreate(BaseModel):
    body:str
    user_id:int
    board_id:int


class CommentUpdate(BaseModel):
    body:str | None = None


    
