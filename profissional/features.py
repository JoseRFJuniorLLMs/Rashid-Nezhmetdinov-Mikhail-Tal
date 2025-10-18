# === features.py ===
"""Extração de features táticas e heurísticas Rashid–Tal."""

import chess
from typing import Dict, List, Optional
from dataclasses import dataclass
from config import AnalysisConfig
from utils import determine_phase, normalize_eval_for_side, is_capture, is_check
from evaluator import PositionEvaluation
from logger import get_logger


@dataclass
class MoveFeatures:
    """Features completas de um lance."""
    # Identificação
    game_id: str
    move_number: int
    ply_index: int
    color_to_move: str

    # Lance
    move_san: str
    move_uci: str

    # Posições
    fen_before: str
    fen_after: str

    # Avaliações
    eval_before: float
    eval_after: float
    eval_diff: float
    eval_diff_abs: float

    # Material
    material_before: float
    material_after: float
    material_diff: float

    # Características do lance
    is_capture: bool
    is_check: bool
    is_mate: bool

    # Features táticas
    motif: str
    is_sacrifice: bool
    is_initiative: bool
    phase: str
    imbalance_score: float

    # Metadados da partida
    white_player: str
    black_player: str
    result: str
    eco: str

    # Comentário interpretativo
    comment: str

    def to_dict(self) -> Dict:
        """Converte para dicionário para export."""
        return {
            'game_id': self.game_id,
            'white': self.white_player,
            'black': self.black_player,
            'result': self.result,
            'eco': self.eco,
            'move_number': self.move_number,
            'ply_index': self.ply_index,
            'color_to_move': self.color_to_move,
            'move_san': self.move_san,
            'move_uci': self.move_uci,
            'fen_before': self.fen_before,
            'fen_after': self.fen_after,
            'eval_before': self.eval_before,
            'eval_after': self.eval_after,
            'eval_diff': self.eval_diff,
            'eval_diff_abs': self.eval_diff_abs,
            'material_before': self.material_before,
            'material_after': self.material_after,
            'material_diff': self.material_diff,
            'is_capture': self.is_capture,
            'is_check': self.is_check,
            'is_mate': self.is_mate,
            'motif': self.motif,
            'is_sacrifice': self.is_sacrifice,
            'is_initiative': self.is_initiative,
            'phase': self.phase,
            'imbalance_score': self.imbalance_score,
            'comment': self.comment
        }


class TacticalAnalyzer:
    """Analisador de padrões táticos estilo Rashid–Tal."""

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.logger = get_logger()

    def detect_sacrifice(self, material_diff: float, eval_before: float,
                         eval_after: float, is_white: bool) -> bool:
        """
        Detecta se um lance é um sacrifício.

        Critérios:
        - Material perdido significativo
        - Avaliação não piora muito (compensação posicional)
        """
        # Normaliza do ponto de vista do jogador
        sign = 1 if is_white else -1
        material_loss = -material_diff * sign

        # Perdeu material?
        if material_loss < self.config.sacrifice_material_threshold:
            return False

        # Avaliação compensou?
        eval_before_norm = normalize_eval_for_side(eval_before, is_white)
        eval_after_norm = normalize_eval_for_side(eval_after, is_white)
        eval_change = eval_after_norm - eval_before_norm

        # Sacrifício válido: perda material mas avaliação não caiu muito
        return eval_change >= -self.config.sacrifice_eval_tolerance

    def detect_initiative(self, eval_diff_abs: float) -> bool:
        """
        Detecta lance que gera iniciativa (mudança brusca de avaliação).
        """
        return eval_diff_abs > self.config.initiative_eval_threshold

    def calculate_imbalance(self, eval_after: float, material_diff: float,
                            eval_diff_abs: float) -> float:
        """
        Calcula score de desequilíbrio posicional.

        Combina:
        - Avaliação absoluta
        - Diferença de material
        - Mudança de avaliação
        """
        return (abs(eval_after) * self.config.eval_weight +
                abs(material_diff) * self.config.material_weight +
                eval_diff_abs * self.config.eval_diff_weight)