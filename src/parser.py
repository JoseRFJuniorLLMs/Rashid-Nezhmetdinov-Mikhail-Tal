import os
import chess.pgn

def iter_pgn_games(path):
    if os.path.isfile(path) and path.endswith(".pgn"):
        with open(path, encoding="utf-8") as f:
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                yield game
    elif os.path.isdir(path):
        for fname in os.listdir(path):
            full_path = os.path.join(path, fname)
            yield from iter_pgn_games(full_path)
