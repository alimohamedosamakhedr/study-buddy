import subprocess
import os
import webbrowser
import time
import sys
BASE_DIR = os.path.dirname(sys.executable)

files = ["Math.py", "english.py", "compsci.py", "physics.py"]

for f in files:
    subprocess.Popen(["python", os.path.join(BASE_DIR, f)])

time.sleep(2) 
webbrowser.open(os.path.join(BASE_DIR, "login.html"))