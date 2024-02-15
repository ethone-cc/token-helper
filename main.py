import os
import re
import json
import base64
import httpx
import ctypes
import sys
import threading
import pyclip
import time
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES
from flask import Flask, request, jsonify, render_template
import webview
from windowfix import setup_all_windows_borderless
from typing import Dict, Optional, Union, List
import httpx
import time
import base64
import re
import os
import json
import ctypes
import sys
import threading
import webview
from Crypto.Cipher import AES
from Crypto.Cipher._mode_gcm import GcmMode
from Crypto.Util import Padding
from flask import Flask, render_template, request, jsonify
import pyclip


class Discord:
    def __init__(self):
        self.roaming_path: str = os.getenv("APPDATA")
        self.appdata_path: str = os.getenv("LOCALAPPDATA")
        self.local_storage_paths: Dict[str, str] = {
            "discord": self.roaming_path + "\\discord\\Local Storage\\leveldb\\",
            "discordcanary": self.roaming_path + "\\discordcanary\\Local Storage\\leveldb\\",
            "lightcord": self.roaming_path + "\\Lightcord\\Local Storage\\leveldb\\",
            "discordptb": self.roaming_path + "\\discordptb\\Local Storage\\leveldb\\",
            "opera": self.roaming_path + "\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\",
            "operagx": self.roaming_path + "\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\",
            "firefox": self.roaming_path + "\\Mozilla\\Firefox\\Profiles",
            "amigo": self.appdata_path + "\\Amigo\\User Data\\Local Storage\\leveldb\\",
            "torch": self.appdata_path + "\\Torch\\User Data\\Local Storage\\leveldb\\",
            "kometa": self.appdata_path + "\\Kometa\\User Data\\Local Storage\\leveldb\\",
            "orbitum": self.appdata_path + "\\Orbitum\\User Data\\Local Storage\\leveldb\\",
            "centbrowser": self.appdata_path + "\\CentBrowser\\User Data\\Local Storage\\leveldb\\",
            "7star": self.appdata_path + "\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\",
            "sputnik": self.appdata_path + "\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\",
            "vivaldi": self.appdata_path + "\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\",
            "chromesxs": self.appdata_path + "\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\",
            "chrome": self.appdata_path + "\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\",
            "epicprivacybrowser": self.appdata_path + "\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\",
            "microsoftedge": self.appdata_path + "\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\",
            "uran": self.appdata_path + "\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\",
            "yandex": self.appdata_path + "\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\",
            "brave": self.appdata_path + "\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\",
            "iridium": self.appdata_path + "\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\"
        }

    def validate_token(self, token: str) -> Optional[Dict[str, Union[str, bool]]]:
        for _ in range(3):
            try:
                url: str = "https://discord.com/api/v9/users/@me"
                headers: Dict[str, str] = {"Authorization": token}

                r: httpx.Response = httpx.get(url, headers=headers)

                if r.status_code != 200 and not token.startswith("MT"):
                    headers["Authorization"] = f"MT{token}"
                    r = httpx.get(url, headers=headers)

                    if r.status_code != 200:
                        return None

                elif r.status_code != 200:
                    return None

                response: Dict[str, Union[str, bool]] = dict(r.json())
                response["token"] = token

                return response
            except:
                time.sleep(3)

        return None

    def get_token(
        self, content: str, decryption_key: bytes
    ) -> Optional[Dict[str, Union[str, bool]]]:
        for line in content.split("\n"):
            for match in re.findall(r"dQw4w9WgXcQ:[^\"]*", line):
                encrypted_token: bytes = base64.b64decode(match.split(":")[1])

                iv: bytes = encrypted_token[3:15]
                payload: bytes = encrypted_token[15:]
                cipher: GcmMode = AES.new(decryption_key, AES.MODE_GCM, iv)

                decrypted_token: bytes = cipher.decrypt(payload)[:-16].decode()

                return self.validate_token(decrypted_token)

    def get_accounts(self) -> Dict[str, Dict[str, Union[str, bool]]]:
        discord_accounts: Dict[str, Dict[str, Union[str, bool]]] = {}

        for platform, path in self.local_storage_paths.items():
            if not os.path.exists(path):
                print(path)
                print(f"{platform} path not found")
                continue

            # handle discord clients
            if "cord" in platform:
                local_state_path: str = f"{self.roaming_path}\\{platform}\\Local State"

                if not os.path.isfile(local_state_path):
                    print(f"{platform} Local State file not found")
                    continue
                else:
                    with open(local_state_path, "r", encoding="utf-8") as f:
                        content: str = f.read()
                        encrypted_decryption_key: str = json.loads(content)["os_crypt"][
                            "encrypted_key"
                        ]
                        decryption_key: bytes = CryptUnprotectData(
                            base64.b64decode(encrypted_decryption_key)[5:]
                        )[1]

                for file in os.listdir(path):
                    if not file.endswith(".log") and not file.endswith(".ldb"):
                        continue

                    with open(f"{path}{file}", "r", errors="ignore") as f:
                        content: str = f.read()
                        data: Optional[Dict[str, Union[str, bool]]] = self.get_token(
                            content, decryption_key
                        )

                        if data != None and data["id"] not in discord_accounts:
                            discord_accounts[data["id"]] = data

            # handle firefox
            elif "firefox" in platform:
                for _path, _, files in os.walk(path):
                    for file in files:
                        if not file.endswith(".sqlite"):
                            continue

                        with open(f"{_path}\\{file}", "r", errors="ignore") as f:
                            content: str = f.read()

                            for token in re.findall(
                                r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}", content
                            ):
                                data: Optional[Dict[str, Union[str, bool]]] = (
                                    self.validate_token(token)
                                )

                                if data != None and data["id"] not in discord_accounts:
                                    discord_accounts[data["id"]] = data

            # handle chromium based browsers
            else:
                if "User Data\\Default" in path:
                    profiles: List[str] = ["Default"]

                    user_data_path: str = path.split("User Data\\")[0] + "User Data\\"
                    for file in os.listdir(user_data_path):
                        if file.startswith("Profile"):
                            profiles.append(file)

                    for profile in profiles:
                        for _path, _, files in os.walk(
                            f"{user_data_path}{profile}\\Local Storage\\leveldb\\"
                        ):
                            for file in files:
                                if not file.endswith(".log") and not file.endswith(
                                    ".ldb"
                                ):
                                    continue

                                with open(f"{_path}{file}", "r", errors="ignore") as f:
                                    content: str = f.read()

                                    for token in re.findall(
                                        r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}", content
                                    ):
                                        data: Optional[Dict[str, Union[str, bool]]] = (
                                            self.validate_token(token)
                                        )

                                        if (
                                            data != None
                                            and data["id"] not in discord_accounts
                                        ):
                                            discord_accounts[data["id"]] = data

        return discord_accounts


class Api:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def quit(self):
        self._window.destroy()


app: Flask = Flask(__name__, template_folder="ui")
quit_event: threading.Event = threading.Event()


@app.route("/", methods=["GET"])
def index() -> str:
    return render_template("index.html")


@app.route("/quit", methods=["GET"])
def quit() -> str:
    parameters: Dict[str, str] = request.args

    api.quit()

    copy: Optional[str] = parameters.get("copy")
    if copy != "null":
        pyclip.copy(copy)
        ctypes.windll.user32.MessageBoxW(
            0,
            "The token was successfully copied to your clipboard.",
            "Ethone | Token Helper",
            0,
        )

    return "1"


@app.route("/get_accounts", methods=["GET"])
def get_accounts() -> str:
    discord: Discord = Discord()
    accounts: Dict[str, Dict[str, Union[str, bool]]] = discord.get_accounts()

    return jsonify(accounts)


def flask() -> None:
    while not quit_event.is_set():
        app.run(port=3801, use_reloader=False)


if __name__ == "__main__":
    # force admin to access local storage if program runtime is blocking it
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        os._exit(0)

    threading.Thread(target=flask, daemon=True).start()

    api: Api = Api()
    window = webview.create_window(
        "Ethone | Token Helper",
        "http://127.0.0.1:3801",
        width=800,
        height=500,
        resizable=False,
        easy_drag=True,
        background_color="#0e0e13",
        frameless=True,
        js_api=Api(),
    )
    api.set_window(window)

    window.events.shown += setup_all_windows_borderless

    webview.start()
    quit_event.set()
    time.sleep(3)
