import os
import requests

def token(request):
    auth_svc = os.environ.get("AUTH_SVC_ADDRESS")

    if not auth_svc:
        return None, "AUTH_SVC_ADDRESS not set"

    try:
        response = requests.post(
            f"http://{auth_svc}/validate",
            headers=request.headers,
        )
    except Exception:
        return None, "auth service unreachable"

    if response.status_code != 200:
        return None, response.text  # return error MESSAGE, not status code

    return response.text, None
