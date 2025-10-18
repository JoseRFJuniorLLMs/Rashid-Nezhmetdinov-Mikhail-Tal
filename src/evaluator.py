import chess
import chess.engine
from tqdm import tqdm
from config import STOCKFISH_PATH, ENGINE_DEPTH
from utils import sf_score_to_float, material_value

def analyze_game(game: chess.pgn.Game, engine_path: str = STOCKFISH_PATH, depth: int = ENGINE_DEPTH):
    """
    Analisa um jogo inteiro e retorna uma lista de dicionários com features por lance.
    Cada item corresponde a um lance ply (meio-movimento).
    """
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    board = game.board()
    nodes = []
    ply_index = 0

    for move in game.mainline_moves():
        ply_index += 1
        move_number = (ply_index + 1) // 2

        fen_before = board.fen()
        # Avaliação antes do lance
        info_before = engine.analyse(board, chess.engine.Limit(depth=depth))
        score_before = sf_score_to_float(info_before.get('score'))
        material_before = material_value(board)

        # SAN antes de push
        try:
            san_move = board.san(move)
        except Exception as e:
            print(f"Aviso: erro ao converter move {move}: {e}")
            san_move = move.uci()

        # Executa o lance
        board.push(move)

        fen_after = board.fen()
        # Avaliação após o lance
        info_after = engine.analyse(board, chess.engine.Limit(depth=depth))
        score_after = sf_score_to_float(info_after.get('score'))
        material_after = material_value(board)

        # Armazena as informações
        nodes.append({
            'move_number': move_number,
            'ply_index': ply_index,
            'move_uci': move.uci(),
            'san': san_move,
            'fen_before': fen_before,
            'fen_after': fen_after,
            'eval_before': score_before,
            'eval_after': score_after,
            'material_before': material_before,
            'material_after': material_after,
        })

    engine.quit()
    return nodes
