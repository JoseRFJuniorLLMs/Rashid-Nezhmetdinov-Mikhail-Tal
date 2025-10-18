import math
import chess

MATE_VALUE = 10000.0

def sf_score_to_float(score: chess.engine.PovScore):
    """Converte um PovScore do Stockfish para float em centipawns.
    Mate é convertido para ±10000 cp (valor arbitrário grande).
    """
    if score is None:
        return 0.0
    # Checa se é mate
    if hasattr(score, "is_mate") and score.is_mate():
        try:
            mate_in = score.mate()
            if mate_in is not None:
                return 10000 if mate_in > 0 else -10000
            else:
                return 0.0
        except AttributeError:
            # fallback caso PovScore não tenha mate
            return 0.0
    # Centipawns
    cp = getattr(score, "score", lambda: None)()
    return float(cp) if cp is not None else 0.0

def material_value(board: chess.Board) -> float:
    """Retorna o valor material simples (em centipawns) do lado branco menos preto.
    Usa valores: P=100, N=320, B=330, R=500, Q=900
    """
    values = {chess.PAWN:100, chess.KNIGHT:320, chess.BISHOP:330, chess.ROOK:500, chess.QUEEN:900}
    val = 0
    for piece_type, v in values.items():
        val += len(board.pieces(piece_type, chess.WHITE)) * v
        val -= len(board.pieces(piece_type, chess.BLACK)) * v
    return val

def phase_from_move_number(move_number:int) -> str:
    """Retorna a fase do jogo com base no número do lance."""
    if move_number <= 15:
        return 'opening'
    if move_number <= 40:
        return 'middlegame'
    return 'endgame'
