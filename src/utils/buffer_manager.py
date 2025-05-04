import time
from threading import Thread, Event
from datetime import datetime
from site.backend.database import get_db # type: ignore
from typing import List, Tuple

class BufferManager:
    def __init__(self, upload_interval: int = 5):  # 300 segundos = 5 minutos
        self.buffer: List[Tuple[datetime, str]] = []
        self.upload_interval = upload_interval
        self.stop_event = Event()
        self.upload_thread = Thread(target=self._upload_worker, daemon=True)
        self.upload_thread.start()

    def add_event(self, direction: str):
        """Adiciona um evento ao buffer com o timestamp atual"""
        timestamp = datetime.now()
        self.buffer.append((timestamp, direction))
        print(f"Evento adicionado ao buffer: {direction} em {timestamp}")

    def _upload_worker(self):
        """Thread worker que faz upload periódico dos dados"""
        while not self.stop_event.is_set():
            time.sleep(self.upload_interval)
            self._upload_buffer()

    def _upload_buffer(self):
        """Faz upload do buffer atual para o banco de dados"""
        if not self.buffer:
            return

        try:
            conn = get_db()
            cursor = conn.cursor()
            # Insere todos os itens do buffer de uma vez
            cursor.executemany(
                "INSERT INTO events (timestamp, direction) VALUES (?, ?)",
                self.buffer
            )
            conn.commit()
            print(f"Upload realizado: {len(self.buffer)} eventos enviados ao banco de dados")
            self.buffer.clear()
        except Exception as e:
            print(f"Erro ao fazer upload do buffer: {e}")
        finally:
            if conn:
                conn.close()

    def shutdown(self):
        """Envia qualquer dado pendente e para a thread de upload"""
        self.stop_event.set()
        self.upload_thread.join()
        self._upload_buffer()

# Instância global do buffer manager
buffer_manager = BufferManager()