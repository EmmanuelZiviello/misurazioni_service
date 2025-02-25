import os
secret_key = os.environ.get('SECRET_KEY', b"\xf2\n\xdf\x07#\xd6J/ \x88\xa0\xb4'\x0f\xc7\x15")

def get_key():
    return os.environ.get('ENCRYPTION_KEY', 'Bcsoft!1')