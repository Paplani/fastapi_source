from pydantic import BaseModel
from datetime import datetime

# 타입 점검 (pydantic)

class CommentCreate(BaseModel):
    body:str
    board_id:int
# get_current_user 함수로 user_id 가져옴

class CommentUpdate(BaseModel):
    body:str | None = None


    
