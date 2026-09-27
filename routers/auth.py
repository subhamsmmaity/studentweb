from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import bcrypt

from database import get_db, User

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/dashboard")
    return RedirectResponse("/login")


@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse(request, "signup.html")


@router.post("/signup")
def signup(request: Request, name: str = Form(...), email: str = Form(...),
           password: str = Form(...), db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return templates.TemplateResponse(request, "signup.html",
            {"error": "Email already registered"})

    hashed = hash_password(password)
    user = User(name=name, email=email, password_hash=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...),
          db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(request, "login.html",
            {"error": "Invalid email or password"})

    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse(request, "dashboard.html", {"user": user})