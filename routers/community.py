from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db, LostFound, ForumPost
from routers.auth import get_current_user

router = APIRouter(prefix="/community")
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
def community_home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")

    items = db.query(LostFound).all()
    posts = db.query(ForumPost).all()

    return templates.TemplateResponse(request, "community.html", {
        "user": user, "items": items, "posts": posts
    })


@router.post("/lostfound/add")
def add_lostfound(request: Request, title: str = Form(...), description: str = Form(...),
                   contact: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    db.add(LostFound(user_id=user.id, title=title, description=description, contact=contact))
    db.commit()
    return RedirectResponse("/community", status_code=303)


@router.post("/forum/add")
def add_forum_post(request: Request, subject: str = Form(...), question: str = Form(...),
                    db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    db.add(ForumPost(user_id=user.id, subject=subject, question=question))
    db.commit()
    return RedirectResponse("/community", status_code=303)