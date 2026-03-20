# ============================================================
# CẤU HÌNH ỨNG DỤNG - DataSync Pro v2
# ============================================================

# ── API Config (Pancake/POS pages.fm) ───────────────────────
API_CONFIG = {
    "base_url": "https://pos.pages.fm/api/v1",
    "timeout": 60,
}

# Shop + API key — pre-filled từ file list_api.text
SHOP_ID = "1546758"
API_KEY = "2a6ed8b51a8d4ae49a851d5876b00018"

# Các endpoint — page_size=500 để giảm số lần gọi
ENDPOINTS = {
    # Entity: (url_template, có_pagination)
    "variations":    ("/shops/{shop_id}/products/variations",            True),
    "orders":        ("/shops/{shop_id}/orders",                          True),
    "customers":     ("/shops/{shop_id}/customers",                      True),
    "warehouses":    ("/shops/{shop_id}/warehouses",                       False),
    "categories":    ("/shops/{shop_id}/categories",                      False),
    "tags":          ("/shops/{shop_id}/orders/tags",                     False),
    "order_sources": ("/shops/{shop_id}/order_source",                    False),
    "users":         ("/shops/{shop_id}/users",                           False),
    # products: extracted from variations (nested in response)
    # addresses: extracted from customers (nested in response)
}

# ── Database Config (MariaDB) ───────────────────────────────
DB_CONFIG = {
    "host":     "100.70.133.122",
    "port":     3306,
    "user":     "root",
    "password": "123123123",
    "database": "pos_db",
}

# ── Sync Config ──────────────────────────────────────────────
SYNC_CONFIG = {
    "variations":    {"enabled": True,  "last_sync": None},
    "products":      {"enabled": True,  "last_sync": None},  # extracted from variations
    "customers":     {"enabled": True,  "last_sync": None},
    "orders":        {"enabled": True,  "last_sync": None},
    "warehouses":    {"enabled": True,  "last_sync": None},
    "categories":    {"enabled": True,  "last_sync": None},
    "tags":          {"enabled": True,  "last_sync": None},
    "order_sources": {"enabled": True,  "last_sync": None},
    "users":         {"enabled": True,  "last_sync": None},
    "addresses":     {"enabled": True,  "last_sync": None},
}

# ── App Settings ─────────────────────────────────────────────
MAX_LOG_LINES = 500
PAGE_SIZE = 1000        # page_size gửi lên API
BATCH_INSERT = 200     # batch upsert vào DB
REQUEST_TIMEOUT = 60   # timeout cho API request (giây)

# ── Sync Checkpoint ──────────────────────────────────────────
# Lưu page cuối cùng đã sync thành công cho từng entity.
# File: <cwd>/sync_checkpoint.json
# Key: entity name → {"page": N, "total_pages": M, "total_entries": K}
import json as _json
import os as _os

_CHECKPOINT_FILE = _os.path.join(_os.path.dirname(__file__), "sync_checkpoint.json")

def _load_checkpoint() -> dict:
    if _os.path.exists(_CHECKPOINT_FILE):
        try:
            with open(_CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return _json.load(f)
        except Exception:
            return {}
    return {}

def get_checkpoint(entity: str) -> dict:
    """Trả về checkpoint của entity, VD: {'page': 180, 'total_pages': 443}"""
    return _load_checkpoint().get(entity, {})

def save_checkpoint(entity: str, page: int, total_pages: int, total_entries: int = 0):
    """Lưu checkpoint sau mỗi page thành công."""
    ck = _load_checkpoint()
    ck[entity] = {"page": page, "total_pages": total_pages, "total_entries": total_entries}
    try:
        with open(_CHECKPOINT_FILE, "w", encoding="utf-8") as f:
            _json.dump(ck, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def clear_checkpoint(entity: str = None):
    """Xóa checkpoint của 1 entity, hoặc tất cả nếu entity=None."""
    if entity is None:
        try:
            if _os.path.exists(_CHECKPOINT_FILE):
                _os.remove(_CHECKPOINT_FILE)
        except Exception:
            pass
    else:
        ck = _load_checkpoint()
        ck.pop(entity, None)
        try:
            with open(_CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                _json.dump(ck, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

