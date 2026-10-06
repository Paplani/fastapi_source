# /todos/ 로 들어오는 요청 처리
# /todos/ : 전체 조회
# /todos/1 + GET : 특정 todo 조회
# /todos/ + POST : 특정 todo 삽입
# todos/1 + 수정데이터 + PUT : 특정 todo 수정


from fastapi import APIRouter, HTTPException, status, Depends
from services.todo import create, select, update, delete
from schemas.todo import TodoCreate, TodoUpdate, TodoResponse, TodoPageResponse
from repository.models.todo import Todo
from repository.database import get_db
from sqlalchemy.orm import Session

# 화면단에서 받는 요청을 받아주기
# 사용자 요청/응답 시 사용할 모델은 schemas 폴더의 todo.py에서 씀
todo_router = APIRouter(prefix="/todos", tags=["Todos"])


@todo_router.post("/")
async def post_todo(data: TodoCreate, db: Session = Depends(get_db)) -> dict:

    # 서비스의 함수 호출
    # TodoCreate => Todo
    todo = Todo(title=data.title, completed=data.completed, important=data.important)
    new_todo = create(todo=todo, db=db)
    return {"message": f"Todo {new_todo.id} 삽입 성공"}


@todo_router.get("/", response_model=TodoPageResponse)
async def get_todos(
    db: Session = Depends(get_db),
    completed: bool | None = None,
    page: int = 1,
    size: int = 10,
) -> list[TodoResponse]:

    todos = select(completed, db=db, page=page, size=size)

    return todos


# /todos/1 + 수정데이터 + PUT : 특정 todo 수정
@todo_router.put("/{todo_id}")
async def put_todo(
    todo_id: int, update_todo: TodoUpdate, db: Session = Depends(get_db)
) -> dict:

    result = update(id=todo_id, data=update_todo, db=db)

    # return {"todo": "todo를 찾을 수 없습니다."}
    if result is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="todo를 찾을 수 없습니다."
        )

    return {"message": f"Todo {result} 수정 성공"}


@todo_router.delete("/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)) -> dict:

    result = delete(id=todo_id, db=db)

    if result is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="todo를 찾을 수 없습니다."
        )
    return {"message": f"Todo {result} 삭제 성공"}


# todos = [
#     {
#         "id": 1,
#         "title": "react 기초 알아보기",
#         "completed": True,
#         "important": True,
#     },
#     {
#         "id": 2,
#         "title": "컴포넌트 스타일링해 보기",
#         "completed": True,
#         "important": False,
#     },
#     {
#         "id": 3,
#         "title": "일정관리 앱 만들어보기",
#         "completed": False,
#         "important": False,
#     },
# ]

# # ** : 딕셔너리의 키를 함수/클래스 매개변수 이름으로 풀어서 전달
# # [TodoItem(), TodoItem(), TodoItem()....]
# todo_items = [TodoItem(**todo) for todo in todos]


# 전체 todo 가져올때
# @todo_router.get("/", response_model=Todo)
# async def get_todos() -> Todo:
#     return {"todos": todo_items}


# @todo_router.get("/{id}", response_model=TodoItem)
# async def get_todo(id: int) -> TodoItem:
#     for todo in todo_items:
#         if todo.id == id:
#             return todo
#     # return {"todo": "todo를 찾을 수 없습니다"}
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND, detail="todo를 찾을 수 없습니다."
#     )


# @todo_router.post(
#     "/",
# )
# async def post_todo(todo: TodoCreate):
#     todo_items.append(todo)

#     create()
#     return {"message": "success"}


# # 경로매개변수 : /todos/1
# # 쿼리매개변수 : /todos/?id=1


# # @todo_router.get("/get")
# # async def get_query_todo(id: int):
# #     for todo in todo_items:
# #         if todo.id == id:
# #             return {"todo": todo}
# #     return {"todo": "todo를 찾 ii을 수 없습니다"}


# # /todos/1 + 수정데이터 + PUT : 특정 todo 수정
# @todo_router.put("/{todo_id}")
# async def put_todo(todo_id: int, update_todo: TodoItem) -> dict:
#     for todo in todo_items:
#         if todo.id == todo_id:
#             todo.title = update_todo.title
#             todo.completed = update_todo.completed
#             todo.important = update_todo.important
#             return {"message": "success"}
#     # return {"todo": "todo를 찾을 수 없습니다."}
#     raise HTTPException(status.HTTP_404_NOT_FOUND, detail="todo를 찾을 수 없습니다.")


# @todo_router.delete("/{todo_id}")
# async def delete_todo(todo_id: int) -> dict:
#     for todo in todo_items:
#         if todo.id == todo_id:
#             todo_items.remove(todo)
#             return {"message": "success"}
#     # return {"todo": "todo를 찾을 수 없습니다."}
#     raise HTTPException(status.HTTP_404_NOT_FOUND, detail="todo를 찾을 수 없습니다.")
