import subprocess
import sys
from multiprocessing import Process

def run_main():
    subprocess.run([sys.executable, "src/main.py"])

def run_app():
    subprocess.run([sys.executable, "-m", "uvicorn", "site.backend.app:app", "--host", "0.0.0.0", "--port", "8000"])

if __name__ == "__main__":
    p1 = Process(target=run_app)
    p2 = Process(target=run_main)
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()