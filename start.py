import os
import sys
from multiprocessing import Process
from pathlib import Path

# Configura caminhos absolutos
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

def run_fastapi():
    """Executa o servidor FastAPI"""
    from src.site.backend.app import app
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

def run_main():
    """Executa o main.py de visão computacional"""
    from main import main
    main()

if __name__ == "__main__":
    # Configura o ambiente
    os.environ["PYTHONPATH"] = str(src_dir)
    
    # Cria os processos
    fastapi_process = Process(target=run_fastapi)
    main_process = Process(target=run_main)
    
    # Inicia os processos
    fastapi_process.start()
    main_process.start()
    
    # Aguarda ambos terminarem
    fastapi_process.join()
    main_process.join()