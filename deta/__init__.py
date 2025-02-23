import os
import urllib.error
import urllib.request
import json

from .base import _Base
from .drive import _Drive


try:
    from detalib.app import App

    app = App()
except Exception:
    pass

__version__ = 0.8


def _get_project_key_id(project_key: str = None, project_id: str = None):
    project_key = project_key or os.getenv("DETA_PROJECT_KEY")
    assert project_key, "No project key defined"

    project_id = project_id
    if not project_id:
        project_id = project_key.split("_")[0]
    assert project_id != project_key, "Bad project key provided"
    return project_key, project_id


def Base(name: str):
    project_key, project_id = _get_project_key_id()
    return _Base(name, project_key, project_id)


def Drive(name: str):
    project_key, project_id = _get_project_key_id()
    return _Drive(name, project_key, project_id)


class Deta:
    def __init__(self, project_key: str = None, *, project_id: str = None):
        project_key, project_id = _get_project_key_id(project_key, project_id)
        self.project_key = project_key
        self.project_id = project_id

    def Base(self, name: str, host: str = None):
        return _Base(name, self.project_key, self.project_id, host)

    def Drive(self, name: str, host: str = None):
        return _Drive(
            name=name,
            project_key=self.project_key,
            project_id=self.project_id,
            host=host,
        )

    def send_email(self, to, subject, message, charset="UTF-8"):
        return send_email(to, subject, message, charset)


def send_email(to, subject, message, charset="UTF-8"):
    pid = os.getenv("AWS_LAMBDA_FUNCTION_NAME")
    url = os.getenv("DETA_MAILER_URL")
    api_key = os.getenv("DETA_PROJECT_KEY")
    endpoint = f"{url}/mail/{pid}"

    to = to if type(to) == list else [to]
    data = {
        "to": to,
        "subject": subject,
        "message": message,
        "charset": charset,
    }

    headers = {"X-API-Key": api_key}

    req = urllib.request.Request(endpoint, json.dumps(data).encode("utf-8"), headers)

    try:
        resp = urllib.request.urlopen(req)
        if resp.getcode() != 200:
            raise Exception(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise Exception(e.reason)
