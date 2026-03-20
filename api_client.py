# ============================================================
# API CLIENT - Gọi POS API, phân trang, extract nested data
# ============================================================

import requests
import time
import config


class ApiClient:
    def __init__(self):
        self.base_url = config.API_CONFIG["base_url"]
        self.timeout = config.API_CONFIG.get("timeout", 30)
        self.shop_id = config.SHOP_ID
        self.api_key = config.API_KEY
        self._session = requests.Session()

    def _url(self, endpoint: str, page: int = 1) -> str:
        url = (self.base_url.rstrip("/") + endpoint).format(
            shop_id=self.shop_id, api_key=self.api_key)
        sep = "?" if "?" not in url else "&"
        return f"{url}{sep}api_key={self.api_key}&page_size={config.PAGE_SIZE}&page_number={page}"

    # ── Fetch có phân trang ───────────────────────────────────
    def fetch_pages(self, endpoint: str,
                    on_page: callable,
                    on_progress: callable = None,
                    stop_check: callable = None,
                    delay: float = 0.1,
                    resume_from: int = 1) -> list:
        """Fetch tất cả pages, gọi on_page(data) cho mỗi trang.
        resume_from: bắt đầu từ page N (dùng khi resume sau timeout).
        Trả về tổng hợp kết quả từ on_page."""
        page = resume_from
        total_pages = None
        total_entries = 0
        all_results = []

        while True:
            if stop_check and stop_check():
                break

            resp = self._session.get(
                self._url(endpoint, page), timeout=self.timeout)
            resp.raise_for_status()
            js = resp.json()

            if total_pages is None:
                total_pages = js.get("total_pages", 1) or 1
                total_entries = js.get("total_entries", 0) or 0

            # Gọi callback xử lý data trang này
            page_data = js.get("data", [])
            page_results = on_page(page_data)
            if page_results:
                all_results.extend(page_results)

            if on_progress:
                on_progress(page, total_pages, len(page_data), total_entries)

            if page >= total_pages:
                break

            page += 1
            time.sleep(delay)

        return all_results

    # ── Fetch 1 order detail ──────────────────────────────────
    def fetch_order_detail(self, order_id: int) -> dict:
        endpoint = f"/orders/{order_id}"
        resp = self._session.get(
            self._url(endpoint), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json().get("data", {})

    # ── Paginated order detail fetch ───────────────────────────
    def fetch_order_details(self,
                            order_ids: list,
                            on_order: callable,
                            on_progress: callable = None,
                            stop_check: callable = None,
                            delay: float = 0.05):
        """Với mỗi order_id, gọi API chi tiết, trả về list order_data."""
        total = len(order_ids)
        for i, oid in enumerate(order_ids):
            if stop_check and stop_check():
                break
            try:
                detail = self.fetch_order_detail(oid)
                on_order(detail)
            except Exception:
                pass
            if on_progress:
                on_progress(i + 1, total)
            if i < total - 1:
                time.sleep(delay)

