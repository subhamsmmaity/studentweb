from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db, CareerEntry
from routers.auth import get_current_user

router = APIRouter(prefix="/career")
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
def career_home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    entries = db.query(CareerEntry).filter(CareerEntry.user_id == user.id).all()
    return templates.TemplateResponse(request, "career.html", {"user": user, "entries": entries})


@router.post("/add")
def add_entry(request: Request, company: str = Form(...), role: str = Form(...),
              status: str = Form(...), notes: str = Form(""), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    db.add(CareerEntry(user_id=user.id, company=company, role=role, status=status, notes=notes))
    db.commit()
    return RedirectResponse("/career", status_code=303)