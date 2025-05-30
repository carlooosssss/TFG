from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    return serializer.dumps(email, salt='password-reset-salt')

def confirm_token(token, expiration=300): 
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=expiration
        )
    except:
        return False
    return email
