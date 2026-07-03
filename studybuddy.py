import subprocess
import os
import webbrowser
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

files = ["Math.py", "english.py", "compsci.py", "physics.py"]

for f in files:
    subprocess.Popen(["python", os.path.join(BASE_DIR, f)])

time.sleep(2) 
webbrowser.open(os.path.join(BASE_DIR, "login.html"))