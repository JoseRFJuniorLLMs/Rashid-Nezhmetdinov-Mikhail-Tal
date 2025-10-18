# === main.py ===
"""
Pipeline Rashid–Tal: Análise de Xadrez Tático
==============================================

Extrai features táticas de partidas PGN usando Stockfish.
Detecta sacrifícios, iniciativa e padrões estilo Tal/Nezhmetdinov.

Uso básico:
    python main.py --pgn_folder ./pgns

Uso avançado:
    python main.py --pgn_folder ./pgns \\
                   --engine_path /usr/local/bin/stockfish \\
                   --depth 15 \\
                   --output dataset_custom.csv \\
                   --no-cache
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from config import PipelineConfig, EngineConfig, AnalysisConfig, OutputConfig
from logger import init_logger
from pipeline import RashidTalPipeline


def parse_arguments():
    """Parse argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description='Pipeline Rashid–Tal: Análise tática de xadrez',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Básico
  python main.py --pgn_folder ./tal_games

  # Customizado
  python main.py --pgn_folder ./pgns \\
                 --engine_path D:\\stockfish\\sf.exe \\
                 --depth 15 \\
                 --output resultados.csv

  # Teste rápido (profundidade 10)
  python main.py --pgn_folder ./pgns --quick
        """
    )

    # Obrigatório
    parser.add_argument(
        '--pgn_folder',
        type=Path,
        required=True,
        help='Pasta contendo arquivos .pgn para análise'
    )

    # Engine
    parser.add_argument(
        '--engine_path',
        type=Path,
        help='Caminho para executável do Stockfish (usa config.py se omitido)'
    )
    parser.add_argument(
        '--depth',
        type=int,
        default=13,
        help='Profundidade de análise da engine (padrão: 13)'
    )
    parser.add_argument(
        '--threads',
        type=int,
        default=1,
        help='Threads da engine (padrão: 1)'
    )
    parser.add_argument(
        '--hash',
        type=int,
        default=128,
        help='Tamanho hash da engine em MB (padrão: 128)'
    )

    # Output
    parser.add_argument(
        '--output',
        type=Path,
        help='Caminho para CSV de saída (padrão: dataset_rashid_tal.csv)'
    )
    parser.add_argument(
        '--no-json',
        action='store_true',
        help='Desabilita geração de JSON'
    )
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Desabilita barra de progresso'
    )

    # Análise
    parser.add_argument(
        '--sacrifice-threshold',
        type=float,
        default=150.0,
        help='Threshold material para sacrifício em centipawns (padrão: 150)'
    )
    parser.add_argument(
        '--initiative-threshold',
        type=float,
        default=80.0,
        help='Threshold eval para iniciativa em centipawns (padrão: 80)'
    )

    # Performance
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Desabilita cache de posições'
    )

    # Modos especiais
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Modo rápido: depth 10, limite de tempo'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Habilita logging detalhado'
    )

    return parser.parse_args()


def build_config(args) -> PipelineConfig:
    """Constrói configuração a partir dos argumentos."""

    # Modo rápido
    if args.quick:
        config = PipelineConfig.for_quick_test()
    else:
        config = PipelineConfig.from_defaults()

    # Engine
    if args.engine_path:
        config.engine.path = args.engine_path
    config.engine.depth = args.depth
    config.engine.threads = args.threads
    config.engine.hash_mb = args.hash

    # Análise
    config.analysis.sacrifice_material_threshold = args.sacrifice_threshold
    config.analysis.initiative_eval_threshold = args.initiative_threshold

    # Output
    if args.output:
        config.output.csv_path = args.output
        # Ajusta JSON e summary paths automaticamente
        base = args.output.stem
        config.output.json_path = args.output.with_stem(base).with_suffix('.json')

    config.output.enable_json = not args.no_json
    config.output.enable_progress = not args.no_progress

    # Performance
    config.enable_cache = not args.no_cache

    return config


def main():
    """Função principal."""
    args = parse_arguments()

    # Valida pasta PGN
    if not args.pgn_folder.exists():
        print(f"❌ Erro: Pasta não encontrada: {args.pgn_folder}", file=sys.stderr)
        sys.exit(1)

    if not args.pgn_folder.is_dir():
        print(f"❌ Erro: Não é um diretório: {args.pgn_folder}", file=sys.stderr)
        sys.exit(1)

    # Constrói configuração
    try:
        config = build_config(args)
    except FileNotFoundError as e:
        print(f"❌ Erro: {e}", file=sys.stderr)
        sys.exit(1)

    # Inicializa logger
    log_level = 'DEBUG' if args.debug else 'INFO'
    import logging
    init_logger(
        log_path=config.output.log_path,
        level=logging.DEBUG if args.debug else logging.INFO
    )

    # Banner
    print("=" * 60)
    print("  🧠 PIPELINE RASHID–TAL: Análise Tática de Xadrez")
    print("=" * 60)
    print(f"📁 Pasta PGN: {args.pgn_folder}")
    print(f"🔧 Engine: {config.engine.path.name} (depth={config.engine.depth})")
    print(f"💾 Output: {config.output.csv_path}")
    print(f"⚡ Cache: {'Ativado' if config.enable_cache else 'Desativado'}")
    print("=" * 60)
    print()

    # Executa pipeline
    pipeline = RashidTalPipeline(config)
    success = pipeline.run(
        pgn_folder=args.pgn_folder,
        output_path=config.output.csv_path
    )

    # Relatório final
    print()
    print("=" * 60)
    if success:
        print("✅ PIPELINE CONCLUÍDO COM SUCESSO")
        stats = pipeline.get_statistics()
        print(f"   • Jogos processados: {stats['games_processed']}")
        print(f"   • Lances analisados: {stats['moves_processed']}")
        print(f"   • Sacrifícios detectados: {stats['sacrifices_found']}")
        print(f"   • Iniciativas detectadas: {stats['initiative_found']}")
        print(f"   • Tempo total: {stats['processing_time']:.1f}s")
        print(f"   • Taxa: {stats['moves_per_second']:.1f} lances/segundo")
    else:
        print("❌ PIPELINE FINALIZADO COM ERROS")
        print("   Verifique os logs para mais detalhes")
    print("=" * 60)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)