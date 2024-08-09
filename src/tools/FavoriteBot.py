import httpc
import random
from Tool import Tool
import concurrent.futures
import time
from utils import Utils
from config import ConfigType, Config

class FavoriteBot(Tool):
    def __init__(self, app):
        super().__init__("Favorite Bot", "Increase/Decrease stars count of an asset", app)

    def run(self):
        self.asset_id = ConfigType.integer(self.config, "asset_id")
        self.unfavorite = ConfigType.boolean(self.config, "unfavorite")
        self.use_proxy = ConfigType.boolean(self.config, "use_proxy")
        self.max_threads = ConfigType.integer(self.config, "max_threads")
        self.timeout = ConfigType.integer(self.config, "timeout")
        self.max_generations = Config.input_max_generations()

        if not self.asset_id or not self.max_generations or self.timeout is None:
            raise Exception("asset_id, max_generations and timeout must not be null.")

        cookies = self.get_cookies(self.max_generations)
        proxies_lines = self.get_proxies_lines() if self.use_proxy else [None]

        req_sent = 0
        req_failed = 0
        total_req = len(cookies)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as self.executor:
            self.results = [self.executor.submit(self.send_favorite, cookie, random.choice(proxies_lines)) for cookie in cookies]

            for future in concurrent.futures.as_completed(self.results):
                try:
                    is_success, response_text = future.result()
                except Exception as e:
                    is_success, response_text = False, str(e)

                if is_success:
                    req_sent += 1
                else:
                    req_failed += 1

                self.print_status(req_sent, req_failed, total_req, response_text, is_success, "New favorites")

    @Utils.handle_exception(3)
    def send_favorite(self, cookie, proxies_line):
        """
        Send a favorite to an asset
        """
        time.sleep(self.timeout)

        proxies = self.convert_line_to_proxy(proxies_line) if proxies_line else None

        with httpc.Session(proxies=proxies) as client:
            user_agent = httpc.get_random_user_agent()
            csrf_token = self.get_csrf_token(cookie, client)
            user_info = self.get_user_info(cookie, client, user_agent)
            user_id = user_info["UserID"]

            req_url = f"https://catalog.roblox.com/v1/favorites/users/{user_id}/assets/{self.asset_id}/favorite"
            req_cookies = {".ROBLOSECURITY": cookie}
            req_headers = httpc.get_roblox_headers(user_agent, csrf_token)

            send_favorite = client.delete if self.unfavorite else client.post

            response = send_favorite(req_url, headers=req_headers, cookies=req_cookies)

        return (response.status_code == 200), Utils.return_res(response)