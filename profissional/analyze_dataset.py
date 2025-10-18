# === analyze_dataset.py ===
"""
Script de análise do dataset gerado pelo pipeline Rashid–Tal.

Exemplos de uso:
    python analyze_dataset.py dataset_rashid_tal.csv
    python analyze_dataset.py dataset_rashid_tal.csv --player "Mikhail Tal"
"""

import pandas as pd
import argparse
from pathlib import Path
from typing import Optional


class DatasetAnalyzer:
    """Analisador de datasets Rashid–Tal."""

    def __init__(self, csv_path: Path):
        self.df = pd.read_csv(csv_path)
        print(f"📊 Dataset carregado: {len(self.df)} lances, {self.df['game_id'].nunique()} jogos\n")

    def summary(self):
        """Exibe sumário geral do dataset."""
        print("=" * 70)
        print("📈 SUMÁRIO GERAL")
        print("=" * 70)

        print(f"\n🎮 Jogos:")
        print(f"  • Total: {self.df['game_id'].nunique()}")
        print(f"  • Lances totais: {len(self.df)}")
        print(f"  • Média de lances por jogo: {len(self.df) / self.df['game_id'].nunique():.1f}")

        print(f"\n⚔️ Jogadores mais frequentes:")
        white_top = self.df['white'].value_counts().head(5)
        for player, count in white_top.items():
            print(f"  • {player}: {count} jogos com brancas")

        print(f"\n🎯 Padrões Táticos:")
        motifs = self.df['motif'].value_counts()
        for motif, count in motifs.items():
            pct = count / len(self.df) * 100
            print(f"  • {motif}: {count} ({pct:.1f}%)")

        print(f"\n💥 Sacrifícios:")
        sac_count = self.df['is_sacrifice'].sum()
        sac_pct = sac_count / len(self.df) * 100
        print(f"  • Total: {sac_count} ({sac_pct:.2f}%)")

        if sac_count > 0:
            sac_df = self.df[self.df['is_sacrifice']]
            avg_material = sac_df['material_diff'].mean()
            print(f"  • Material médio sacrificado: {abs(avg_material) / 100:.2f} peões")
            print(f"  • Δeval médio: {sac_df['eval_diff'].mean() / 100:+.2f} peões")

        print(f"\n⚡ Iniciativa:")
        init_count = self.df['is_initiative'].sum()
        init_pct = init_count / len(self.df) * 100
        print(f"  • Lances com iniciativa: {init_count} ({init_pct:.2f}%)")

        print(f"\n📊 Por Fase:")
        phases = self.df['phase'].value_counts()
        for phase, count in phases.items():
            pct = count / len(self.df) * 100
            print(f"  • {phase}: {count} ({pct:.1f}%)")

        print()

    def player_analysis(self, player_name: str):
        """Analisa jogos de um jogador específico."""
        player_df = self.df[
            (self.df['white'].str.contains(player_name, case=False, na=False)) |
            (self.df['black'].str.contains(player_name, case=False, na=False))
            ]

        if len(player_df) == 0:
            print(f"❌ Nenhum jogo encontrado para: {player_name}")
            return

        print("=" * 70)
        print(f"👤 ANÁLISE: {player_name}")
        print("=" * 70)

        # Jogos
        games = player_df['game_id'].nunique()
        as_white = player_df[player_df['white'].str.contains(player_name, case=False, na=False)]['game_id'].nunique()
        as_black = player_df[player_df['black'].str.contains(player_name, case=False, na=False)]['game_id'].nunique()

        print(f"\n🎮 Partidas:")
        print(f"  • Total: {games}")
        print(f"  • Com brancas: {as_white}")
        print(f"  • Com pretas: {as_black}")
        print(f"  • Lances analisados: {len(player_df)}")

        # Sacrifícios
        sacrifices = player_df[player_df['is_sacrifice']]
        if len(sacrifices) > 0:
            print(f"\n💥 Sacrifícios:")
            print(f"  • Total: {len(sacrifices)}")
            print(f"  • Taxa: {len(sacrifices) / len(player_df) * 100:.2f}%")
            print(f"  • Material médio: {abs(sacrifices['material_diff'].mean()) / 100:.2f} peões")

            # Top 5 sacrifícios mais dramáticos
            print(f"\n  🔥 Top 5 Sacrifícios (por material):")
            top_sac = sacrifices.nsmallest(5, 'material_diff')[
                ['game_id', 'move_number', 'move_san', 'material_diff', 'eval_diff', 'comment']
            ]
            for idx, row in top_sac.iterrows():
                print(f"     {row['game_id'][:30]}... Lance {row['move_number']}: {row['move_san']}")
                print(f"       Material: {row['material_diff'] / 100:.1f} | Δeval: {row['eval_diff'] / 100:+.2f}")
                print(f"       {row['comment']}")

        # Iniciativa
        initiative = player_df[player_df['is_initiative']]
        if len(initiative) > 0:
            print(f"\n⚡ Iniciativa:")
            print(f"  • Lances com iniciativa: {len(initiative)}")
            print(f"  • Taxa: {len(initiative) / len(player_df) * 100:.2f}%")
            print(f"  • Δeval médio: {initiative['eval_diff_abs'].mean() / 100:.2f} peões")

        # Preferências táticas
        print(f"\n🎯 Motivos Favoritos:")
        motifs = player_df['motif'].value_counts().head(3)
        for motif, count in motifs