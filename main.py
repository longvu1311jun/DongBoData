# ============================================================
# ENTRY POINT - DataSync Pro
# ============================================================
# Chạy: python main.py
# ============================================================

import sys
import subprocess

# Tự động cài requests + mariadb nếu chưa có
for pkg, imp in [("requests", "requests"), ("mariadb", "mariadb")]:
    try:
        __import__(imp)
    except ImportError:
        print(f">>> Đang cài đặt '{pkg}'...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pkg, "-q"])
        print(">>> Done!\n")

from gui import main

if __name__ == "__main__":
    main()

