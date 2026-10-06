from fastapi import APIRouter, HTTPException, status
from schemas.task import Task, TaskCreate, TaskResponse, TaskPageResponse, TaskUpdate
from exceptions.task import TaskNotFoundException
from sqlalchemy.orm import Session
from repository.database import get_db
from fastapi import Depends
from services.task import create, select, update, delete


task_router = APIRouter(tags=["Tasks"])


# 조회
@task_router.get("", response_model=TaskPageResponse)
async def get_tasks(db: Session = Depends(get_db), page: int = 1, size: int = 10):
    tasks = select(page=page, size=size, db=db)
    return tasks


# Depends : 주입
# 하나 추가
@task_router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def post_task(data: TaskCreate, db: Session = Depends(get_db)):
    task = create(data=data, db=db)
    return {"message": f"Task {task.id} 삽입 성공"}


# # 하나만 조회
# @task_router.get("", response_model=Task)
# async def get_task(id: int):
#     for task in tasks:
#         if task.id == id:
#             return task
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND, detail="찾는 task가 없습니다."
#     )


# 하나만 수정
@task_router.put("/{id}", response_model=dict)
async def put_task(
    id: int,
    update_task: TaskUpdate,
    db: Session = Depends(get_db),
):

    try:
        task = update(db=db, data=update_task, id=id)

    except TaskNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="task를 찾을 수 없습니다."
        )
    return {"message": f"Task {task.id} 수정완료"}


# 하나 삭제
@task_router.delete("/{id}", response_model=dict)
async def delete_task(id: int, db: Session = Depends(get_db)):
    try:
        id = delete(db=db, id=id)
    except TaskNotFoundException:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="task를 찾을 수 없습니다."
        )
    return {"message": f"Task {id} 삭제완료"}
