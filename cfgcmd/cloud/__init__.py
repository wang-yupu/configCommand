#
import requests
from enum import Enum
import json


class applyResult(Enum):
    SUCCESS = 0
    EXPIRE = 1
    UNREADY = 2
    RATELIMIT = 3


class requestsResult(Enum):
    SUCCESS = 0
    HTTPERROR = 1
    TIMEOUT = 2
    UNKNOWN = 3
    RATELIMIT = 4


def wrapRequests(method, *args, **kwargs) -> tuple[requests.Response | None, requestsResult]:
    try:
        response = method(*args, **kwargs)
        if response.status_code == 429:
            return None, requestsResult.RATELIMIT
        return response, requestsResult.SUCCESS
    except requests.exceptions.HTTPError | requests.exceptions.ConnectionError | requests.exceptions.TooManyRedirects:
        return None, requestsResult.HTTPERROR
    except requests.exceptions.ConnectTimeout:
        return None, requestsResult.TIMEOUT


class CloudSession:
    def __init__(self, name, content, author, server, pluginVersion):
        self.sessionReady = False
        self.sessionNotReadyReason = None
        self.sessionID = ""

        # 准备数据
        data = json.dumps({
            "name": name,
            "content": content,
            "author": author,
            "server": server
        })

        self.headers = {
            "user-agent": f"cfgcmd MCDR plugin {pluginVersion} (MCDR plugin)",
            "Content-Type": "application/json"
        }

        response, status = wrapRequests(requests.post, "https://e1.yupu.dev/obj/create",
                                        data=data, headers=self.headers)
        print(response.content)
        if status != requestsResult.SUCCESS:
            self.sessionNotReadyReason = status
            return

        resp = response.json()
        # 判断结果
        if response.status_code != 400 and response.status_code != 500 and resp['success']:
            self.sessionReady = True
            self.sessionID = resp['objectID']

    def getEditorURL(self):
        if self.checkReady():
            return f"https://cfgcmd.wangyupu.com/editor/{self.sessionID}"
        return False

    def applyChanges(self) -> tuple[str, applyResult]:
        if self.checkReady():
            response, status = wrapRequests(
                requests.get, f"https://e1.yupu.dev/obj/read/{self.sessionID}", headers=self.headers)
            if response.status_code == 404:
                return "", applyResult.EXPIRE
            elif status != requestsResult.SUCCESS:
                return "", applyResult.RATELIMIT
            else:
                data = response.json()
                content = data.get('content')
                if content.strip() == "内容丢失，请再打开一个新的编辑器会话":
                    return "", applyResult.EXPIRE
                return content, applyResult.SUCCESS

        return "", applyResult.UNREADY

    def checkReady(self):
        if self.sessionReady and self.sessionID:
            return True

        return False

    def deleteSession(self):
        if self.checkReady():
            wrapRequests(requests.delete, f"https://e1.yupu.dev/obj/delete/{self.sessionID}", headers=self.headers)
            self.sessionReady = False
