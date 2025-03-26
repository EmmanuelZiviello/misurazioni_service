from datetime import timedelta
from flask import request
from flask_jwt_extended import get_jwt, create_access_token, verify_jwt_in_request


ACCESS_EXPIRES = timedelta(minutes=20)



def refresh():
    try:
        verify_jwt_in_request(refresh=True)
        access_token = create_access_token(identity=request.json['id'])
        return {"esito": "success", "access_token": access_token}
    except Exception:
        return "JWT not valid", 400
    
def get_role(request):
    url = request.url
    if 'paziente\login' in url or 'paziente\password' in url or 'paziente' in url and request.method == 'POST':
        return 'patient'
    if 'admin\login' in url:
        return 'admin'
    if 'nutrizionista\login' in url:
        return 'dietitian'
    try:
        role = get_jwt()['role']
        return role
    except Exception:
        return None