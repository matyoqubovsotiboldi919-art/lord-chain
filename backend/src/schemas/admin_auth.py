from pydantic import BaseModel

class AdminLoginRequest(BaseModel):
    password: str

class AdminTokenOut(BaseModel):
    admin_token: str
    expires_in_seconds: int
