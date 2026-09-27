from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db, Todo, Expense
from routers.auth import get_current_user

router = APIRouter(prefix="/productivity")
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
def productivity_home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")

    todos = db.query(Todo).filter(Todo.user_id == user.id).all()
    expenses = db.query(Expense).filter(Expense.user_id == user.id).all()
    total_spent = sum(e.amount for e in expenses)

    return templates.TemplateResponse(request, "productivity.html", {
        "user": user, "todos": todos,
        "expenses": expenses, "total_spent": total_spent
    })


@router.post("/todo/add")
def add_todo(request: Request, title: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    db.add(Todo(user_id=user.id, title=title))
    db.commit()
    return RedirectResponse("/productivity", status_code=303)


@router.get("/todo/{todo_id}/toggle")
def toggle_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    t = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user.id).first()
    if t:
        t.done = not t.done
        db.commit()
    return RedirectResponse("/productivity", status_code=303)


@router.post("/expense/add")
def add_expense(request: Request, category: str = Form(...), amount: float = Form(...),
                 db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    db.add(Expense(user_id=user.id, category=category, amount=amount))
    db.commit()
    return RedirectResponse("/productivity", status_code=303)