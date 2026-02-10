from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models.user import User
from app.models.password_reset import PasswordReset
from app.schemas.user import SignupSchema, LoginSchema, VerifyEmailSchema,ForgotPasswordSchema,ResetPasswordSchema,ResendOTPSchema
from app.security.jwt import create_access_token
from app.utils.otp import generate_otp
from app.utils.email import send_otp_email

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================
# SIGNUP
# =========================
from app.models.pending_user import PendingUser

@router.post("/signup")
def signup(data: SignupSchema):
    db = SessionLocal()
    try:
        email = data.email.strip().lower()

        # ❌ already verified user → block
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(400, "Account already exists")

        # password check
        password_bytes = data.password.encode("utf-8")
        if len(password_bytes) < 8 or len(password_bytes) > 72:
            raise HTTPException(400, "Password must be 8–72 bytes")

        hashed_password = pwd_context.hash(data.password)
        otp = generate_otp()

        # 🔑 CHECK pending_users
        pending = db.query(PendingUser).filter(PendingUser.email == email).first()

        if pending:
            # 🔁 overwrite OTP (email/phone issue case)
            pending.otp_code = otp
            pending.otp_expires_at = datetime.utcnow() + timedelta(minutes=5)
            pending.password_hash = hashed_password
        else:
            # 🆕 first-time signup
            pending = PendingUser(
                first_name=data.first_name,
                middle_name=data.middle_name,
                last_name=data.last_name,
                email=email,
                password_hash=hashed_password,
                otp_code=otp,
                otp_expires_at=datetime.utcnow() + timedelta(minutes=5)
            )
            db.add(pending)

        db.commit()

        # 📧 try sending OTP (user-side gmail issue allowed)
        try:
            send_otp_email(email, otp)
        except Exception:
            pass  # pending user me rehne do

        return { "message": "OTP sent to email. Please verify." }

    finally:
        db.close()


# =========================
# VERIFY EMAIL (OTP)
# =========================
@router.post("/verify-email")
def verify_email(data: VerifyEmailSchema):
    db = SessionLocal()
    try:
        email = data.email.strip().lower()

        pending = db.query(PendingUser).filter(
            PendingUser.email == email,
            PendingUser.otp_code == data.otp,
            PendingUser.otp_expires_at > datetime.utcnow()
        ).first()

        if not pending:
            raise HTTPException(400, "Invalid OTP or user not found")

        # ✅ move to users table
        user = User(
            first_name=pending.first_name,
            middle_name=pending.middle_name,
            last_name=pending.last_name,
            email=pending.email,
            password_hash=pending.password_hash,
            is_email_verified=True
        )

        db.add(user)
        db.delete(pending)
        db.commit()

        return { "message": "Email verified successfully. Account activated." }

    finally:
        db.close()


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(data: LoginSchema):
    db = SessionLocal()
    try:
        email = data.email.strip().lower()

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(400, "Account not found. Please sign up.")

        if not pwd_context.verify(data.password, user.password_hash):
            raise HTTPException(400, "Incorrect password")

        token = create_access_token(user.id)

        return {
            "message": "Login successful",
            "token": token
        }

    finally:
        db.close()







@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordSchema):
    db = SessionLocal()
    try:
        email = data.email.strip().lower()

        user = db.query(User).filter(User.email == email).first()
        if not user:
            # security: same message even if user not found
            return { "message": "If account exists, OTP has been sent" }

        otp = generate_otp()

        otp_entry = PasswordReset(
            user_id=user.id,
            otp_code=otp,
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )
        db.add(otp_entry)
        db.commit()

        send_otp_email(user.email, otp)

        return { "message": "OTP sent to email" }

    finally:
        db.close()







@router.post("/reset-password")
def reset_password(data: ResetPasswordSchema):
    db = SessionLocal()
    try:
        email = data.email.strip().lower()

        if data.new_password != data.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        password_bytes = data.new_password.encode("utf-8")
        if len(password_bytes) < 8 or len(password_bytes) > 72:
            raise HTTPException(
                status_code=400,
                detail="Password must be 8–72 bytes (no emojis)"
            )

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=400, detail="Invalid request")

        otp_record = (
            db.query(PasswordReset)
            .filter(
                PasswordReset.user_id == user.id,
                PasswordReset.otp_code == data.otp,
                PasswordReset.is_used == False,
                PasswordReset.expires_at > datetime.utcnow()
            )
            .first()
        )

        if not otp_record:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")

        user.password_hash = pwd_context.hash(data.new_password)
        otp_record.is_used = True

        db.commit()

        return { "message": "Password reset successful" }

    finally:
        db.close()




@router.post("/resend-otp")
def resend_otp(data: ResendOTPSchema):
    db = SessionLocal()
    try:
        email = data.email.strip().lower()

        user = db.query(User).filter(User.email == email).first()
        if not user:
            # security: same response
            return { "message": "If account exists, OTP has been sent" }

        # ⏱️ COOLDOWN CHECK (30 seconds)
        last_otp = (
            db.query(PasswordReset)
            .filter(
                PasswordReset.user_id == user.id,
                PasswordReset.created_at > datetime.utcnow() - timedelta(seconds=30)
            )
            .first()
        )

        if last_otp:
            raise HTTPException(
                status_code=429,
                detail="Please wait 30 seconds before requesting another OTP"
            )

        # ❌ expire all old OTPs
        db.query(PasswordReset).filter(
            PasswordReset.user_id == user.id,
            PasswordReset.is_used == False
        ).update({ "is_used": True })

        # 🔢 generate new OTP
        otp = generate_otp()
        otp_entry = PasswordReset(
            user_id=user.id,
            otp_code=otp,
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )

        db.add(otp_entry)
        db.commit()

        # 📧 send email
        send_otp_email(user.email, otp)

        return { "message": "OTP resent to email" }

    finally:
        db.close()