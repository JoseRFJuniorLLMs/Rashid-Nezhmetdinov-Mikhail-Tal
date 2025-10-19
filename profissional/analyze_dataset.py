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
        for motif, count in motifs.items():
            pct = count / len(player_df) * 100
            print(f"  • {motif}: {count} ({pct:.1f}%)")

        # Por fase
        print(f"\n📊 Distribuição por Fase:")
        for phase in ['opening', 'middlegame', 'endgame']:
            phase_df = player_df[player_df['phase'] == phase]
            if len(phase_df) > 0:
                sac_rate = phase_df['is_sacrifice'].sum() / len(phase_df) * 100
                print(f"  • {phase}: {len(phase_df)} lances, {sac_rate:.1f}% sacrifícios")

        print()

    def find_brilliant_moves(self, min_imbalance: float = 200.0, limit: int = 10):
        """Encontra os lances mais brilhantes (alto imbalance)."""
        print("=" * 70)
        print(f"✨ TOP {limit} LANCES MAIS BRILHANTES")
        print("=" * 70)

        brilliant = self.df.nlargest(limit, 'imbalance_score')

        for idx, (i, row) in enumerate(brilliant.iterrows(), 1):
            print(f"\n{idx}. {row['white']} vs {row['black']}")
            print(f"   Lance {row['move_number']}: {row['move_san']} ({row['color_to_move']})")
            print(f"   Imbalance: {row['imbalance_score']:.1f}")
            print(f"   Eval: {row['eval_before'] / 100:+.2f} → {row['eval_after'] / 100:+.2f}")
            print(f"   Material: {row['material_diff'] / 100:+.2f} peões")
            print(f"   Motif: {row['motif']}")
            print(f"   💬 {row['comment']}")

        print()

    def compare_players(self, player1: str, player2: str):
        """Compara estatísticas de dois jogadores."""
        p1_df = self.df[
            (self.df['white'].str.contains(player1, case=False, na=False)) |
            (self.df['black'].str.contains(player1, case=False, na=False))
            ]

        p2_df = self.df[
            (self.df['white'].str.contains(player2, case=False, na=False)) |
            (self.df['black'].str.contains(player2, case=False, na=False))
            ]

        if len(p1_df) == 0 or len(p2_df) == 0:
            print("❌ Um ou ambos jogadores não encontrados")
            return

        print("=" * 70)
        print(f"⚔️ COMPARAÇÃO: {player1} vs {player2}")
        print("=" * 70)

        def calc_stats(df, name):
            return {
                'name': name,
                'games': df['game_id'].nunique(),
                'moves': len(df),
                'sacrifice_rate': df['is_sacrifice'].sum() / len(df) * 100,
                'initiative_rate': df['is_initiative'].sum() / len(df) * 100,
                'avg_imbalance': df['imbalance_score'].mean(),
                'avg_eval_swing': df['eval_diff_abs'].mean() / 100
            }

        stats1 = calc_stats(p1_df, player1)
        stats2 = calc_stats(p2_df, player2)

        print(f"\n{'Métrica':<25} {player1:<20} {player2:<20}")
        print("-" * 70)
        print(f"{'Jogos':<25} {stats1['games']:<20} {stats2['games']:<20}")
        print(f"{'Lances analisados':<25} {stats1['moves']:<20} {stats2['moves']:<20}")
        print(f"{'Taxa de sacrifício':<25} {stats1['sacrifice_rate']:<20.2f}% {stats2['sacrifice_rate']:<20.2f}%")
        print(f"{'Taxa de iniciativa':<25} {stats1['initiative_rate']:<20.2f}% {stats2['initiative_rate']:<20.2f}%")
        print(f"{'Imbalance médio':<25} {stats1['avg_imbalance']:<20.1f} {stats2['avg_imbalance']:<20.1f}")
        print(f"{'Swing eval médio':<25} {stats1['avg_eval_swing']:<20.2f} {stats2['avg_eval_swing']:<20.2f}")

        print()

    def sacrifice_heatmap(self):
        """Mostra em quais lances ocorrem mais sacrifícios."""
        print("=" * 70)
        print("🔥 HEATMAP DE SACRIFÍCIOS POR LANCE")
        print("=" * 70)

        sac_df = self.df[self.df['is_sacrifice']]

        if len(sac_df) == 0:
            print("❌ Nenhum sacrifício encontrado")
            return

        # Agrupa por faixas de lances
        bins = [0, 10, 20, 30, 40, 50, 100]
        labels = ['1-10', '11-20', '21-30', '31-40', '41-50', '50+']

        sac_df['move_range'] = pd.cut(sac_df['move_number'], bins=bins, labels=labels, include_lowest=True)

        print(f"\n{'Lances':<15} {'Sacrifícios':<15} {'% do Total':<15}")
        print("-" * 45)

        for label in labels:
            count = len(sac_df[sac_df['move_range'] == label])
            pct = count / len(sac_df) * 100
            bar = '█' * int(pct / 2)  # Barra visual
            print(f"{label:<15} {count:<15} {pct:<6.1f}% {bar}")

        print()

    def eco_analysis(self):
        """Analisa padrões por abertura (ECO)."""
        if 'eco' not in self.df.columns or self.df['eco'].isna().all():
            print("❌ Sem informações de ECO no dataset")
            return

        print("=" * 70)
        print("📚 ANÁLISE POR ABERTURA (ECO)")
        print("=" * 70)

        eco_stats = self.df.groupby('eco').agg({
            'game_id': 'nunique',
            'is_sacrifice': 'sum',
            'is_initiative': 'sum',
            'imbalance_score': 'mean'
        }).rename(columns={
            'game_id': 'games',
            'is_sacrifice': 'sacrifices',
            'is_initiative': 'initiative',
            'imbalance_score': 'avg_imbalance'
        })

        # Ordena por número de sacrifícios
        eco_stats = eco_stats.sort_values('sacrifices', ascending=False).head(10)

        print(f"\n🔝 Top 10 Aberturas por Sacrifícios:")
        print(f"\n{'ECO':<8} {'Jogos':<8} {'Sacrifícios':<15} {'Iniciativa':<15} {'Imbalance':<15}")
        print("-" * 70)

        for eco, row in eco_stats.iterrows():
            print(f"{eco:<8} {int(row['games']):<8} {int(row['sacrifices']):<15} "
                  f"{int(row['initiative']):<15} {row['avg_imbalance']:<15.1f}")

        print()


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Analisa dataset gerado pelo Pipeline Rashid–Tal'
    )
    parser.add_argument('csv_file', type=Path, help='Arquivo CSV do dataset')
    parser.add_argument('--player', type=str, help='Analisa jogos de um jogador específico')
    parser.add_argument('--compare', nargs=2, metavar=('PLAYER1', 'PLAYER2'),
                        help='Compara dois jogadores')
    parser.add_argument('--brilliant', type=int, default=10,
                        help='Mostra N lances mais brilhantes (padrão: 10)')
    parser.add_argument('--eco', action='store_true',
                        help='Analisa padrões por abertura (ECO)')
    parser.add_argument('--heatmap', action='store_true',
                        help='Mostra heatmap de sacrifícios por lance')

    args = parser.parse_args()

    if not args.csv_file.exists():
        print(f"❌ Arquivo não encontrado: {args.csv_file}")
        return 1

    # Carrega e analisa
    analyzer = DatasetAnalyzer(args.csv_file)

    # Sumário sempre
    analyzer.summary()

    # Análises opcionais
    if args.player:
        analyzer.player_analysis(args.player)

    if args.compare:
        analyzer.compare_players(args.compare[0], args.compare[1])

    if args.brilliant:
        analyzer.find_brilliant_moves(limit=args.brilliant)

    if args.heatmap:
        analyzer.sacrifice_heatmap()

    if args.eco:
        analyzer.eco_analysis()

    return 0


if __name__ == '__main__':
    import sys

    sys.exit(main())