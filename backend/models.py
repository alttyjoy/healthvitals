from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class EntryData(BaseModel):
    vital_key: str
    date: str
    value: float
    value2: Optional[float] = None
    notes: Optional[str] = None

class BulkEntryRequest(BaseModel):
    entries: List[EntryData]

class ReminderRequest(BaseModel):
    vital_keys: List[str] = []
    time: str = "08:00"
    frequency: str = "daily"
    enabled: bool = True

class ExportRequest(BaseModel):
    vital_keys: List[str]
    start_date: str
    end_date: str
    format: str = "csv"

class SharedReportRequest(BaseModel):
    vital_keys: List[str]
    start_date: str
    end_date: str
    expires_days: int = 7
    password: Optional[str] = None

class SharedReportAccessRequest(BaseModel):
    password: Optional[str] = None

class RazorpayOrderRequest(BaseModel):
    plan_key: str
    billing_cycle: str = "monthly"
    coupon_code: str = ""

class RazorpayVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    plan_key: str
    coupon_code: str = ""

class VitalToggleRequest(BaseModel):
    vital_key: str
    enabled: bool

class PlanChangeRequest(BaseModel):
    plan_key: str

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str

class PayUInitRequest(BaseModel):
    plan_key: str
    billing_cycle: str = "monthly"
    coupon_code: str = ""

class BlogPostRequest(BaseModel):
    title: str
    slug: str
    content: str
    excerpt: Optional[str] = ""
    published: bool = True
    tags: List[str] = []

class SmtpSettingsRequest(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    smtp_from_name: Optional[str] = None
    smtp_use_tls: Optional[bool] = True

class ContentPageRequest(BaseModel):
    key: str
    title: str
    content: str
    page_type: str = "legal"
    published: bool = True

class CouponRequest(BaseModel):
    code: str
    discount_percent: float
    max_uses: int = 0
    valid_plans: List[str] = []
    expires_at: Optional[str] = None
    active: bool = True
