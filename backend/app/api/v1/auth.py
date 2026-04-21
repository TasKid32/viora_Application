"""
Authentication API Routes — Thin controllers delegating to AuthService.
Enhanced with a professional Web UI for Password Resets.
Features: Branded Logo with Glow, Password Visibility Toggle, and Soft UI Design.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.schemas.auth_schemas import UserRegister, UserLogin
from app.services.auth_service import register_user, login_user
from app.core.security import (
    get_password_hash, create_password_reset_token, verify_password_reset_token,
    decode_token, create_access_token, create_refresh_token
)
from app.core.logging import get_logger
from app.services.email_service import email_service

router = APIRouter()
logger = get_logger(__name__)

# --- Registration Endpoint ---
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        return register_user(
            db=db,
            full_name=user_data.full_name,
            email=user_data.email,
            password=user_data.password,
            confirm_password=user_data.confirm_password,
        )
    except HTTPException: raise
    except Exception:
        logger.exception("Unexpected error during registration")
        raise HTTPException(status_code=500, detail="Registration failed")

# --- Login Endpoint ---
@router.post("/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    try:
        return login_user(db=db, email=credentials.email, password=credentials.password)
    except HTTPException: raise
    except Exception:
        logger.exception("Unexpected error during login")
        raise HTTPException(status_code=500, detail="Login failed")

# --- Forgot Password Request ---
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if user:
        token = create_password_reset_token(body.email)
        sent = email_service.send_password_reset(body.email, token)
        if sent: logger.info("Password reset email sent to: %s", body.email)
    return {"success": True, "message": "If this email is registered, a link will be sent."}

# --- 1. GET: Reset Password Web Page (UI with Logo Glow & Eye Icon) ---
@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(token: str):
    return f"""
    <html>
        <head>
            <title>Viora - Reset Password</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
                .card {{ background: white; padding: 35px; border-radius: 30px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); width: 90%; max-width: 380px; text-align: center; position: relative; }}
                
                /* Logo and Glow Effect */
                .logo-wrapper {{ position: relative; display: inline-block; margin-bottom: 15px; }}
                .logo-glow {{ 
                    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                    width: 110px; height: 110px; 
                    background: radial-gradient(circle, rgba(118, 75, 162, 0.3) 0%, rgba(255, 255, 255, 0) 70%); 
                    border-radius: 50%; z-index: 1; 
                }}
                .logo {{ width: 85px; height: 85px; position: relative; z-index: 2; border-radius: 50%; object-fit: contain; }}
                
                h2 {{ color: #764ba2; margin: 10px 0; font-weight: 700; letter-spacing: -0.5px; }}
                p {{ color: #777; font-size: 14px; margin-bottom: 25px; }}
                
                .input-group {{ position: relative; margin-bottom: 20px; text-align: left; }}
                input {{ 
                    width: 100%; padding: 14px 45px 14px 15px; border: 2px solid #f0f0f0; 
                    border-radius: 15px; box-sizing: border-box; outline: none; transition: 0.3s; font-size: 16px; 
                }}
                input:focus {{ border-color: #764ba2; background-color: #fdfbff; }}
                
                .toggle-password {{ 
                    position: absolute; right: 15px; top: 50%; transform: translateY(-50%); 
                    cursor: pointer; color: #bbb; font-size: 18px; transition: 0.3s;
                }}
                .toggle-password:hover {{ color: #764ba2; }}
                
                button {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; border: none; padding: 16px; width: 100%; border-radius: 15px; 
                    cursor: pointer; font-weight: bold; font-size: 16px; margin-top: 10px; 
                    transition: 0.3s; box-shadow: 0 8px 20px rgba(118, 75, 162, 0.3); 
                }}
                button:hover {{ transform: translateY(-2px); box-shadow: 0 12px 25px rgba(118, 75, 162, 0.4); }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="logo-wrapper">
                    <div class="logo-glow"></div>
                    <img src="/static/logo.png" class="logo" alt="Viora Logo">
                </div>
                <h2>Viora</h2>
                <p>Reset your account password</p>
                <form action="/api/auth/reset-password-web" method="post">
                    <input type="hidden" name="token" value="{token}">
                    <div class="input-group">
                        <input type="password" id="new_pass" name="new_password" placeholder="New Password" required minlength="8">
                        <i class="fas fa-eye toggle-password" onclick="toggle('new_pass', this)"></i>
                    </div>
                    <div class="input-group">
                        <input type="password" id="conf_pass" name="confirm_password" placeholder="Confirm Password" required minlength="8">
                        <i class="fas fa-eye toggle-password" onclick="toggle('conf_pass', this)"></i>
                    </div>
                    <button type="submit">Update Password</button>
                </form>
            </div>
            <script>
                function toggle(id, el) {{
                    const input = document.getElementById(id);
                    if (input.type === "password") {{
                        input.type = "text";
                        el.classList.replace("fa-eye", "fa-eye-slash");
                    }} else {{
                        input.type = "password";
                        el.classList.replace("fa-eye-slash", "fa-eye");
                    }}
                }}
            </script>
        </body>
    </html>
    """

# --- 2. POST: Handle Web Password Reset Submission (Branded Success Page) ---
@router.post("/reset-password-web")
async def reset_password_web(
    token: str = Form(...), 
    new_password: str = Form(...), 
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    if new_password != confirm_password:
        return HTMLResponse("<h3 style='color:red; text-align:center; font-family:sans-serif;'>Passwords do not match!</h3>", status_code=400)
    
    email = verify_password_reset_token(token)
    if not email:
        return HTMLResponse("<h3 style='color:red; text-align:center; font-family:sans-serif;'>Link expired or invalid!</h3>", status_code=400)

    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        user.password_hash = get_password_hash(new_password)
        db.commit()
        email_service.send_password_changed_notification(email)
        
        return HTMLResponse(f"""
            <html>
                <head>
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
                        .card {{ background: white; padding: 45px; border-radius: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); width: 90%; max-width: 400px; text-align: center; }}
                        .icon {{ font-size: 70px; margin-bottom: 20px; display: inline-block; background: #f0fdf4; border-radius: 50%; width: 100px; height: 100px; line-height: 100px; }}
                        h2 {{ color: #764ba2; margin-bottom: 10px; font-weight: bold; }}
                        p {{ color: #666; line-height: 1.6; font-size: 16px; }}
                    </style>
                </head>
                <body>
                    <div class="card">
                        <div class="icon">✅</div>
                        <h2>Success!</h2>
                        <p>Your password has been updated.<br>You can now return to <b>Viora</b> app and login.</p>
                    </div>
                </body>
            </html>
        """)
    return HTMLResponse("User not found", status_code=404)

# --- 3. POST: Standard API Reset Password (JSON for Mobile App) ---
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    email = verify_password_reset_token(body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    if body.new_password != body.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = get_password_hash(body.new_password)
    db.commit()
    email_service.send_password_changed_notification(email)
    return {"success": True, "message": "Password has been reset successfully."}

# --- Token Refresh Endpoint ---
class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
async def refresh_token(body: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token, expected_type="refresh")
    if not payload: raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("user_id")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: raise HTTPException(status_code=401, detail="User not found")
    
    token_data = {"sub": user.email, "user_id": user_id}
    return {{
        "access_token": create_access_token(data=token_data),
        "refresh_token": create_refresh_token(data=token_data),
    }}