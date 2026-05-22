"""
Sales Data Tool - Entry Point
"""

import sys
import os

# Get absolute path of project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, 'src')

# Add src to Python path
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Import TANPA 'src.' prefix
from presentation.app import SalesDataApp


def main():
    app = SalesDataApp()
    app.run()


if __name__ == "__main__":
    main()