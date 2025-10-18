# === file: exporter.py ===
import pandas as pd
import json
from typing import List, Dict


def export_to_csv(rows: List[Dict], path: str):
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False, encoding='utf-8')


def export_to_json(rows: List[Dict], path: str):
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=2)
