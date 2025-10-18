# === test_pipeline.py ===
"""
Testes unitários para o pipeline Rashid–Tal.

Execute com: pytest test_pipeline.py -v
"""

import pytest
import chess
import chess.pgn
from pathlib import Path
from io import StringIO

from config import PipelineConfig, AnalysisConfig
from utils import (
    score_to_centipawns, calculate_material, determine_phase,
    normalize_eval_for_side, format_eval
)
from parser import PGNParser, GameMetadata
from features import TacticalAnalyzer


class TestUtils:
    """Testes para funções utilitárias."""

    def test_material_calculation(self):
        """Testa cálculo de material."""
        board = chess.Board()  # Posição inicial
        material = calculate_material(board)

        assert material['white'] == material['black']
        assert material['balance'] == 0

        # Remove uma peça
        board.remove_piece_at(chess.E2)  # Remove peão branco
        material = calculate_material(board)
        assert material['balance'] == -100  # Pretas têm 1 peão a mais

    def test_phase_determination(self):
        """Testa determinação de fase."""
        assert determine_phase(5) == 'opening'
        assert determine_phase(15) == 'opening'
        assert determine_phase(16) == 'middlegame'
        assert determine_phase(40) == 'middlegame'
        assert determine_phase(41) == 'endgame'

    def test_eval_normalization(self):
        """Testa normalização de avaliação."""
        eval_cp = 150.0  # Brancas melhor

        assert normalize_eval_for_side(eval_cp, is_white=True) == 150.0
        assert normalize_eval_for_side(eval_cp, is_white=False) == -150.0

    def test_eval_formatting(self):
        """Testa formatação de avaliação."""
        assert format_eval(145.0) == "+1.45"
        assert format_eval(-32.0) == "-0.32"
        assert format_eval(0.0) == "+0.00"
        assert format_eval(10000.0) == "#10"
        assert format_eval(-10000.0) == "#-10"


class TestParser:
    """Testes para parser PGN."""

    def test_game_metadata_extraction(self):
        """Testa extração de metadados."""
        pgn_str = """
[Event "World Championship"]
[Site "Moscow"]
[Date "1960.03.15"]
[Round "1"]
[White "Tal, Mikhail"]
[Black "Botvinnik, Mikhail"]
[Result "1-0"]
[ECO "B10"]

1. e4 c6 2. d4 d5 1-0
"""
        pgn = StringIO(pgn_str)
        game = chess.pgn.read_game(pgn)
        metadata = GameMetadata.from_game(game)

        assert metadata.event == "World Championship"
        assert metadata.white == "Tal, Mikhail"
        assert metadata.black == "Botvinnik, Mikhail"
        assert metadata.result == "1-0"
        assert metadata.eco == "B10"
        assert "tal" in metadata.game_id.lower()

    def test_parser_with_empty_game(self):
        """Testa parser com jogo sem lances."""
        pgn_str = """
[Event "Test"]
[White "Player1"]
[Black "Player2"]

*
"""
        pgn = StringIO(pgn_str)
        game = chess.pgn.read_game(pgn)

        # Parser deve detectar e ignorar jogos vazios
        assert game is not None
        moves = list(game.mainline_moves())
        assert len(moves) == 0


class TestTacticalAnalyzer:
    """Testes para análise tática."""

    @pytest.fixture
    def analyzer(self):
        """Cria analyzer para testes."""
        config = AnalysisConfig()
        return TacticalAnalyzer(config)

    def test_sacrifice_detection(self, analyzer):
        """Testa detecção de sacrifício."""
        # Cenário: perda de 3 peões (300cp) mas avaliação melhorou
        material_diff = -300.0  # Brancas perderam material
        eval_before = 0.0
        eval_after = 200.0  # Mas avaliação melhorou

        is_sac = analyzer.detect_sacrifice(
            material_diff, eval_before, eval_after, is_white=True
        )

        assert is_sac is True

    def test_not_sacrifice_when_eval_worse(self, analyzer):
        """Testa que não detecta sacrifício quando avaliação piora muito."""
        material_diff = -300.0
        eval_before = 0.0
        eval_after = -300.0  # Avaliação piorou muito

        is_sac = analyzer.detect_sacrifice(
            material_diff, eval_before, eval_after, is_white=True
        )

        assert is_sac is False

    def test_initiative_detection(self, analyzer):
        """Testa detecção de iniciativa."""
        eval_diff_abs = 150.0  # Mudança grande

        assert analyzer.detect_initiative(eval_diff_abs) is True

        eval_diff_abs = 50.0  # Mudança pequena
        assert analyzer.detect_initiative(eval_diff_abs) is False

    def test_motif_classification(self, analyzer):
        """Testa classificação de motivos."""
        # Sacrifício com xeque
        motif = analyzer.classify_motif(
            is_sacrifice=True, is_initiative=False,
            is_capture=False, is_check=True
        )
        assert motif == 'sacrifice_check'

        # Sacrifício normal
        motif = analyzer.classify_motif(
            is_sacrifice=True, is_initiative=False,
            is_capture=False, is_check=False
        )
        assert motif == 'sacrifice'

        # Golpe tático
        motif = analyzer.classify_motif(
            is_sacrifice=False, is_initiative=True,
            is_capture=True, is_check=False
        )
        assert motif == 'tactical_blow'

        # Lance quieto
        motif = analyzer.classify_motif(
            is_sacrifice=False, is_initiative=False,
            is_capture=False, is_check=False
        )
        assert motif == 'quiet'

    def test_imbalance_calculation(self, analyzer):
        """Testa cálculo de imbalance score."""
        imbalance = analyzer.calculate_imbalance(
            eval_after=200.0,
            material_diff=-300.0,
            eval_diff_abs=150.0
        )

        # Score deve ser positivo e razoável
        assert imbalance > 0
        assert imbalance < 1000  # Sanity check


class TestConfig:
    """Testes para configuração."""

    def test_default_config_creation(self):
        """Testa criação de config padrão."""
        config = PipelineConfig.from_defaults()

        assert config.engine.depth == 13
        assert config.analysis.sacrifice_material_threshold == 150.0
        assert config.enable_cache is True

    def test_quick_test_config(self):
        """Testa config de teste rápido."""
        config = PipelineConfig.for_quick_test()

        assert config.engine.depth == 10
        assert config.engine.time_limit_ms == 500


class TestIntegration:
    """Testes de integração."""

    def test_full_game_processing_simulation(self):
        """Simula processamento de jogo completo sem engine."""
        # Cria jogo simples
        pgn_str = """
[Event "Test"]
[White "Player1"]
[Black "Player2"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 *
"""
        pgn = StringIO(pgn_str)
        game = chess.pgn.read_game(pgn)
        metadata = GameMetadata.from_game(game)

        # Valida que conseguimos extrair os dados básicos
        assert metadata.white == "Player1"
        assert len(list(game.mainline_moves())) == 6

        # Simula board states
        board = game.board()
        moves = list(game.mainline_moves())

        assert len(moves) > 0

        for move in moves:
            board.push(move)

        # Verifica que board está em estado válido
        assert board.is_valid()


# === Fixtures globais ===

@pytest.fixture(scope="session")
def sample_pgn_content():
    """PGN de exemplo para testes."""
    return """
[Event "Candidates Tournament"]
[Site "Bled/Zagreb/Belgrade"]
[Date "1959.09.18"]
[Round "8"]
[White "Tal, Mikhail"]
[Black "Smyslov, Vassily"]
[Result "1-0"]
[ECO "B10"]

1. e4 c6 2. d3 d5 3. Nd2 e5 4. Ngf3 Nd7 5. d4 dxe4 6. Nxe4 exd4 
7. Qxd4 Ngf6 8. Bg5 Be7 9. O-O-O O-O 10. Nd6 Qa5 1-0
"""


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])