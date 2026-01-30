import sys
import os

# Ensure 'backend' folder is on sys.path so 'app' package imports resolve during tests
TEST_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(TEST_DIR, '..'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
