import os

# Admin parolini ENV orqali beramiz (disk/DBga yozilmaydi)
# Windows PowerShell:  $env:ADMIN_PASSWORD="12345"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # vaqtincha default
