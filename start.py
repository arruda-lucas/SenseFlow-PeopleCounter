import os
import sys
from multiprocessing import Process
from pathlib import Path
import json

config = json.load(open("config/config.json"))
config_source_1 = config['source_1']
config_source_2 = config['source_2']

# Configura caminhos absolutos
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

def run_fastapi():
    """Executa o servidor FastAPI"""
    from src.site.backend.app import app
    import uvicorn
    uvicorn.run("src.site.backend.app:app", host="0.0.0.0", port=8000)

def run_main():
    """Executa o main.py de visão computacional"""
    from main import main
    main(video_source=config_source_1['local'], polyline_segments=config_source_1)

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