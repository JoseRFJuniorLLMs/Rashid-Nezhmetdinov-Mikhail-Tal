# === file: features.py ===
from typing import List, Dict
from utils import material_value, phase_from_move_number


def compute_features_for_game(game_meta: Dict, nodes: List[Dict]) -> List[Dict]:
    """Recebe metadados do jogo e lista de nodes da função analyze_game. Retorna linhas prontas para export.
    game_meta: dict com campos padrão (Event, White, Black, Date, Result, ECO...)
    nodes: lista com dicionários por ply contendo fen_before/after, evals e materiais
    """
    out = []
    for n in nodes:
        eval_before = n['eval_before']
        eval_after = n['eval_after']
        material_before = n['material_before']
        material_after = n['material_after']
        material_diff = material_after - material_before
        eval_diff = eval_after - eval_before
        # heurística de sacrifício: material decreased (white advantage less material) but eval improves for mover
        mover = 'white' if (n['ply_index'] % 2)==1 else 'black'
        # normalize eval diff sign relative to mover
        mover_sign = 1 if mover == 'white' else -1
        is_sacrifice = False
        if material_diff * mover_sign < -150:  # perdeu ~1.5 peões ou mais
            # sacrifice plausible if eval_after is not much worse for mover
            if (eval_after * mover_sign) >= (eval_before * mover_sign) - 50:
                is_sacrifice = True
        # initiative heuristic
        initiative = abs(eval_diff) > 80  # >0.8 pawn ≈ 80 centipawns
        motif = 'none'
        if is_sacrifice:
            motif = 'sacrifice'
        elif initiative:
            motif = 'initiative'
        # imbalance score: combinação ad-hoc
        imbalance = abs(eval_after) * 0.6 + abs(material_diff) * 0.1 + abs(eval_diff) * 0.3
        phase = phase_from_move_number(n['move_number'])
        row = {
            'game_id': game_meta.get('Event','') + '_' + str(game_meta.get('Date','')),
            'white': game_meta.get('White',''),
            'black': game_meta.get('Black',''),
            'result': game_meta.get('Result',''),
            'eco': game_meta.get('ECO',''),
            'move_number': n['move_number'],
            'ply_index': n['ply_index'],
            'color_to_move': mover,
            'move_san': n['san'],
            'move_uci': n['move_uci'],
            'fen_before': n['fen_before'],
            'fen_after': n['fen_after'],
            'eval_before': eval_before,
            'eval_after': eval_after,
            'eval_diff': eval_diff,
            'material_diff': material_diff,
            'motif': motif,
            'phase': phase,
            'imbalance_score': imbalance,
        }
        out.append(row)
    return out
