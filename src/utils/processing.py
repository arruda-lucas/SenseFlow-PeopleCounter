from typing import Tuple, List, Optional
import numpy as np

DIRECTION_IN = "in"
DIRECTION_OUT = "out"

class PolylineConfig:
    @staticmethod
    def load_from_config(config) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        return [
            (tuple(segment['start']), tuple(segment['end']))
            for segment in config['polyline']
        ]

class PolylineCounter:
    def __init__(self, segments: List[Tuple[Tuple[int, int], Tuple[int, int]]], right=True):
        """
        Args:
            segments: Lista de tuplas representando segmentos da poligonal [(start, end), ...]
        """
        self.segments = segments
        self.track_history = {}
        self._precompute_normals(right)

    def _precompute_normals(self):
        """Calcula vetores normais consistentes para todos os segmentos."""
        self.normals = []
        for (start, end) in self.segments:
            dx, dy = end[0] - start[0], end[1] - start[1]
            length = np.sqrt(dx**2 + dy**2)
            self.normals.append((-dy/length, dx/length))

    def _precompute_normals(self, right=True):
        self.normals = []
        for (start, end) in self.segments:
            dx, dy = end[0] - start[0], end[1] - start[1]
            length = np.sqrt(dx**2 + dy**2)
            if right:
                normal = (-dy/length, dx/length)  # Interior à direita
            else:
                normal = (dy/length, -dx/length)  # Interior à esquerda
            self.normals.append(normal)

    def check_crossing(self, track_id: int, current_pos: Tuple[int, int]) -> Optional[str]:
        """
        Verifica se o objeto cruzou a poligonal e retorna a direção.
        
        Args:
            track_id: ID único do objeto
            current_pos: Posição atual (x, y)
            
        Returns:
            "in" se entrou, "out" se saiu, None caso contrário
        """
        if track_id not in self.track_history:
            self.track_history[track_id] = current_pos
            return None

        prev_pos = self.track_history[track_id]
        direction = None
        
        for (seg_start, seg_end), normal in zip(self.segments, self.normals):
            if self._segments_intersect(seg_start, seg_end, prev_pos, current_pos):
                trajectory_vec = np.array([current_pos[0]-prev_pos[0], current_pos[1]-prev_pos[1]])
                dot = np.dot(trajectory_vec, normal)
                direction = DIRECTION_IN if dot > 0 else DIRECTION_OUT
                break

        self.track_history[track_id] = current_pos
        return direction

    @staticmethod
    def _segments_intersect(A: Tuple, B: Tuple, C: Tuple, D: Tuple) -> bool:
        """Verifica interseção entre segmentos AB e CD com bounding box check."""
        def ccw(a, b, c):
            return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
        
        # Bounding box check rápida
        if max(A[0], B[0]) < min(C[0], D[0]) or min(A[0], B[0]) > max(C[0], D[0]) or \
           max(A[1], B[1]) < min(C[1], D[1]) or min(A[1], B[1]) > max(C[1], D[1]):
            return False
            
        return (ccw(A, C, D) * ccw(B, C, D) < 0) and (ccw(C, A, B) * ccw(D, A, B) < 0)

    def cleanup_inactive_tracks(self, active_ids: set):
        """Remove tracks não ativos do histórico."""
        self.track_history = {k: v for k, v in self.track_history.items() if k in active_ids}

class PeopleCounter:
    def __init__(self):
        self.count_in = 0
        self.count_out = 0
        
    def update_count(self, direction: str):
        if direction == DIRECTION_IN:
            self.count_in += 1
        else:
            self.count_out += 1
        print(f"Movimento: {direction.upper()} | Entradas: {self.count_in} | Saídas: {self.count_out}")