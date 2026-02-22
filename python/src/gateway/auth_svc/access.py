import os
import requests

def login(request):
    auth = request.authorization
    if not auth:
        return None, "missing credentials"

    basicAuth = (auth.username, auth.password)

    auth_svc = os.environ.get("AUTH_SVC_ADDRESS")
    if not auth_svc:
        return None, "AUTH_SVC_ADDRESS not set"

    try:
        response = requests.post(
            f"http://{auth_svc}/login",
            auth=basicAuth
        )
    except Exception:
        return None, "auth service unreachable"

    if response.status_code == 200:
        return response.text, None
    else:
        return None, response.text  # return error message only
