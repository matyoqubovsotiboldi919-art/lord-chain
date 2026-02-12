import time

# 3 xato urinishdan keyin 1 soat blok
ADMIN_MAX_FAILS = 3
ADMIN_LOCK_SECONDS = 60 * 60  # 1 hour

# Admin session timeout: 30 min (aktivlik bo‘lmasa)
ADMIN_SESSION_TIMEOUT_SECONDS = 30 * 60

# --- state (RAM) ---
ADMIN_FAILED_COUNT = 0
ADMIN_LOCKED_UNTIL = 0  # epoch seconds, 0 -> not locked

# 5.6: SINGLE ADMIN SESSION
# token -> {"exp": epoch_seconds, "last": epoch_seconds}
ADMIN_SESSIONS: dict[str, dict] = {}
