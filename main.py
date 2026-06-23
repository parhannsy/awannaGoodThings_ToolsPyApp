"""
Sales Data Tool - Main Entry Point
Mengatur inisialisasi environment path dan menjalankan window utama aplikasi.
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, 'src')

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from presentation.app import SalesDataApp

def main():
    # Langsung jalankan Software Utama proyekmu sejak awal
    app = SalesDataApp()
    if hasattr(app, 'run'):
        app.run()
    else:
        app.mainloop()

if __name__ == "__main__":
    main()