from pydantic import BaseModel, EmailStr

class FreezeRequest(BaseModel):
    email: EmailStr
    freeze: bool

class LockRequest(BaseModel):
    email: EmailStr
    lock_minutes: int  # masalan 60
