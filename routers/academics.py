from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db, Subject, Assignment
from routers.auth import get_current_user

router = APIRouter(prefix="/academics")
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
def academics_home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")

    subjects = db.query(Subject).filter(Subject.user_id == user.id).all()
    assignments = db.query(Assignment).filter(Assignment.user_id == user.id).all()

    total_credits = sum(s.credit for s in subjects) or 1
    cgpa = sum(s.credit * (s.marks / 10) for s in subjects) / total_credits if subjects else 0

    return templates.TemplateResponse(request, "academics.html", {
        "user": user, "subjects": subjects,
        "assignments": assignments, "cgpa": round(cgpa, 2)
    })


@router.post("/subject/add")
def add_subject(request: Request, name: str = Form(...), credit: float = Form(...),
                 marks: float = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    db.add(Subject(user_id=user.id, name=name, credit=credit, marks=marks))
    db.commit()
    return RedirectResponse("/academics", status_code=303)


@router.post("/assignment/add")
def add_assignment(request: Request, title: str = Form(...), subject: str = Form(...),
                    due_date: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    db.add(Assignment(user_id=user.id, title=title, subject=subject, due_date=due_date))
    db.commit()
    return RedirectResponse("/academics", status_code=303)


@router.get("/assignment/{assignment_id}/done")
def mark_done(request: Request, assignment_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    a = db.query(Assignment).filter(Assignment.id == assignment_id, Assignment.user_id == user.id).first()
    if a:
        a.status = "done"
        db.commit()
    return RedirectResponse("/academics", status_code=303)