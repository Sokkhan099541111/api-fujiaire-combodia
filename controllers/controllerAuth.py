# from fastapi import HTTPException
# from fastapi.security import OAuth2PasswordRequestForm
# from passlib.context import CryptContext
# from db import get_db_connection
# import jwt
# import datetime
# import os

# from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# hashed_password = pwd_context.hash("123456")
# print(hashed_password)

# SECRET_KEY = os.getenv("JWT_SECRET", "your_jwt_secret")
# ALGORITHM = "HS256"

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)

# def create_access_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# def register_user(email: str, password: str):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
#     if cursor.fetchone():
#         raise HTTPException(status_code=400, detail="email already exists")

#     hashed_pw = hash_password(password)
#     cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_pw))
#     conn.commit()
#     cursor.close()
#     conn.close()

#     return {"message": "User registered successfully"}

# def login_user(form_data: OAuth2PasswordRequestForm):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("SELECT * FROM users WHERE email = %s", (form_data.email,))
#     user = cursor.fetchone()

#     cursor.close()
#     conn.close()

#     if not user or not verify_password(form_data.password, user["password"]):
#         raise HTTPException(status_code=401, detail="Invalid email or password")

#     token = create_access_token({"sub": user["email"]})
#     return {"access_token": token, "token_type": "bearer"}


from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from db import get_db_connection
import jwt
import datetime
import os

# ---------------------------------------------------------------------
# PASSWORD HASHING
# ---------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain text password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------
# JWT CONFIG
# ---------------------------------------------------------------------
SECRET_KEY = os.getenv("JWT_SECRET", "your_jwt_secret")
ALGORITHM = "HS256"

def create_access_token(data: dict) -> str:
    """Create a JWT token with 1-hour expiration."""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------------------
# USER REGISTRATION
# ---------------------------------------------------------------------
def register_user(email: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for duplicate email
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hash password and insert
    hashed_pw = hash_password(password)
    cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_pw))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "User registered successfully"}


# ---------------------------------------------------------------------
# USER LOGIN
# ---------------------------------------------------------------------
def login_user(form_data: OAuth2PasswordRequestForm):
    """
    Authenticate user and return a JWT token.
    OAuth2PasswordRequestForm expects:
        username=<email> and password=<password>
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Use .username instead of .email
    cursor.execute("SELECT * FROM users WHERE email = %s", (form_data.username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create access token
    token = create_access_token({"sub": user["email"], "user_id": user["id"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user["id"],
        "email": user["email"],
    }
