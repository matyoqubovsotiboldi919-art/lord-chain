# Threat Model (summary)

## Main threats
- Brute force login -> user lockout
- OTP abuse -> OTP expiry + max tries
- Token theft -> single session sid check
- Admin brute force -> 3 fails -> 1 hour lock
- Data tampering -> chain verification endpoint (6.6)
- Race conditions -> SELECT FOR UPDATE + atomic transaction

## Residual risks
- In-memory sessions reset on restart (can be moved to DB later)
- Email OTP depends on SMTP provider security
