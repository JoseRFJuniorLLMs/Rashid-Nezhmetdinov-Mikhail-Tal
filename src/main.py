# === file: main.py ===
import argparse
import os
from tqdm import tqdm
from parser import iter_pgn_games
from evaluator import analyze_game
from features import compute_features_for_game
from exporter import export_to_csv, export_to_json
from config import OUTPUT_CSV, OUTPUT_JSON, STOCKFISH_PATH, ENGINE_DEPTH


def game_metadata_to_dict(game):
    headers = ['Event','Site','Date','Round','White','Black','Result','ECO']
    meta = {}
    for h in headers:
        meta[h] = game.headers.get(h,'')
    return meta


def iter_all_games(pgn_paths):
    """Itera sobre todos os jogos, aceitando lista de arquivos ou pasta única."""
    if isinstance(pgn_paths, str):
        pgn_paths = [pgn_paths]

    for path in pgn_paths:
        if os.path.isfile(path):
            yield from iter_pgn_games(path)
        elif os.path.isdir(path):
            for fname in os.listdir(path):
                if fname.lower().endswith(".pgn"):
                    full_path = os.path.join(path, fname)
                    yield from iter_pgn_games(full_path)
        else:
            print(f"Arquivo ou pasta inválida: {path}")


def process_folder(pgn_paths, engine_path: str = STOCKFISH_PATH, depth:int = ENGINE_DEPTH, out_csv: str = OUTPUT_CSV, out_json: str = OUTPUT_JSON):
    all_rows = []

    # Conta total de jogos para a barra de progresso
    total_games = sum(1 for _ in iter_all_games(pgn_paths))
    if total_games == 0:
        print("Nenhum jogo encontrado.")
        return

    print(f"Total de jogos a processar: {total_games}")

    processed_games = 0
    for game in tqdm(iter_all_games(pgn_paths), total=total_games, desc="Jogos processados"):
        processed_games += 1
        meta = game_metadata_to_dict(game)
        try:
            nodes = analyze_game(game, engine_path=engine_path, depth=depth)
            rows = compute_features_for_game(meta, nodes)
            all_rows.extend(rows)
        except Exception as e:
            print(f"\nErro ao analisar jogo {meta.get('Event','')} {meta.get('Date','')}: {e}")

    if not all_rows:
        print("Nenhum lance processado.")
        return

    export_to_csv(all_rows, out_csv)
    export_to_json(all_rows, out_json)
    print(f"\nProcessados {processed_games} jogos. CSV salvo em: {out_csv}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Processa PGNs e gera dataset para análise Rashid/Tal')
    parser.add_argument('--pgn_paths', nargs='+', required=True, help='Arquivos ou pastas com PGNs')
    parser.add_argument('--engine_path', default=STOCKFISH_PATH, help='Caminho para o executável Stockfish')
    parser.add_argument('--depth', type=int, default=ENGINE_DEPTH, help='Profundidade da engine (ex: 13)')
    parser.add_argument('--out_csv', default=OUTPUT_CSV, help='Arquivo CSV de saída')
    parser.add_argument('--out_json', default=OUTPUT_JSON, help='Arquivo JSON de saída')
    args = parser.parse_args()
    process_folder(args.pgn_paths, engine_path=args.engine_path, depth=args.depth, out_csv=args.out_csv, out_json=args.out_json)
# === End of files ===
