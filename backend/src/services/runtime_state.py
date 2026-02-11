# In-memory runtime state (server restart bo‘lsa tozalanadi)

# email -> {"code": "123456", "exp": epoch_seconds, "tries": 0}
OTP_STORE: dict[str, dict] = {}

# email -> session_id
ACTIVE_SESSIONS: dict[str, str] = {}
