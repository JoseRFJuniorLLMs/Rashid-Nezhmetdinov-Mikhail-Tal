# === config.py ===
"""Configuração centralizada do pipeline Rashid–Tal."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class EngineConfig:
    """Configurações da engine de xadrez."""
    path: Path = Path(r"D:\stockfish\stockfish-windows-x86-64-avx2.exe")
    depth: int = 13
    time_limit_ms: Optional[int] = None
    threads: int = 1
    hash_mb: int = 128

    def __post_init__(self):
        if not self.path.exists():
            raise FileNotFoundError(f"Stockfish não encontrado: {self.path}")


@dataclass
class AnalysisConfig:
    """Configurações de análise tática."""
    # Thresholds para detecção de padrões
    sacrifice_material_threshold: float = 150.0  # centipawns
    sacrifice_eval_tolerance: float = 50.0
    initiative_eval_threshold: float = 80.0

    # Pesos para imbalance score
    eval_weight: float = 0.6
    material_weight: float = 0.1
    eval_diff_weight: float = 0.3

    # Limites de fase
    opening_moves: int = 15
    endgame_moves: int = 40


@dataclass
class OutputConfig:
    """Configurações de output."""
    csv_path: Path = Path("dataset_rashid_tal.csv")
    json_path: Path = Path("dataset_rashid_tal.json")
    log_path: Path = Path("pipeline.log")
    enable_json: bool = True
    enable_progress: bool = True


@dataclass
class PipelineConfig:
    """Configuração completa do pipeline."""
    engine: EngineConfig = field(default_factory=EngineConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    # Performance
    enable_cache: bool = True
    parallel_games: int = 1  # Experimental: processar jogos em paralelo

    @classmethod
    def from_defaults(cls) -> 'PipelineConfig':
        """Cria configuração com valores padrão."""
        return cls()

    @classmethod
    def for_quick_test(cls) -> 'PipelineConfig':
        """Configuração otimizada para testes rápidos."""
        config = cls()
        config.engine.depth = 10
        config.engine.time_limit_ms = 500
        return config


# Constantes globais
MATE_VALUE = 10000.0
PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 0
}