#DO NOT CHANGE THIS to fix_imports PATTERN! OR OTHERWISE THIS WILL BE CIRCULAR IMPORT!
import os, sys
pardir = None
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(current_dir) not in sys.path:
    sys.path.append(os.path.dirname(current_dir))
while pardir != "":
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    pardir = os.path.basename(parent_dir)
    current_dir = parent_dir
    if os.path.dirname(parent_dir) not in sys.path:
        sys.path.append(parent_dir)