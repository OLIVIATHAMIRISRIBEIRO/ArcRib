"""
run_arcrib.py - Launch Script for ArcRib GIS Studio
Run with: python run_arcrib.py
"""

import sys
import os

# Ensure project root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from arcrib.app import main

if __name__ == "__main__":
    main()
