# 🚀 Quick Start — Pipeline Rashid–Tal

Guia de início rápido em **5 minutos**.

---

## ⚡ Instalação Express

```bash
# 1. Clone ou baixe os arquivos do projeto
cd rashid-tal-pipeline

# 2. Instale dependências
pip install python-chess pandas tqdm

# 3. Baixe Stockfish
# Windows: https://stockfishchess.org/download/
# Linux: sudo apt install stockfish
# Mac: brew install stockfish

# 4. Configure o caminho do Stockfish
# Edite config.py e ajuste STOCKFISH_PATH
```

---

## 📦 Estrutura Mínima

```
seu-projeto/
├── pgns/              # 📁 Coloque seus PGNs aqui
│   ├── tal_1960.pgn
│   └── nezh_1958.pgn
├── config.py          # ⚙️ Configuração
├── main.py            # 🎯 Script principal
└── ...outros arquivos
```

---

## 🎯 Uso Básico

### 1️⃣ Processar PGNs

```bash
python main.py --pgn_folder ./pgns
```

**Output:**
- `dataset_rashid_tal.csv` — Dataset principal
- `dataset_rashid_tal.json` — Versão JSON
- `dataset_rashid_tal_summary.json` — Estatísticas
- `pipeline.log` — Logs detalhados

### 2️⃣ Analisar Resultados

```bash
# Sumário geral
python analyze_dataset.py dataset_rashid_tal.csv

# Análise de jogador específico
python analyze_dataset.py dataset_rashid_tal.csv --player "Mikhail Tal"

# Comparar dois jogadores
python analyze_dataset.py dataset_rashid_tal.csv --compare "Tal" "Botvinnik"

# Top lances brilhantes
python analyze_dataset.py dataset_rashid_tal.csv --brilliant 20
```

---

## 🔧 Configuração Rápida

### Windows

```python
# config.py
STOCKFISH_PATH = r"C:\stockfish\stockfish-windows-x86-64-avx2.exe"
ENGINE_DEPTH = 13
```

### Linux/Mac

```python
# config.py
STOCKFISH_PATH = "/usr/local/bin/stockfish"  # ou "/usr/bin/stockfish"
ENGINE_DEPTH = 13
```

---

## 📊 Analisando com Pandas

```python
import pandas as pd

# Carrega dataset
df = pd.read_csv('dataset_rashid_tal.csv')

# Filtra sacrifícios de Tal
tal_sac = df[
    (df['white'] == 'Mikhail Tal') & 
    (df['is_sacrifice'] == True)
]

print(f"Tal fez {len(tal_sac)} sacrifícios")

# Top 5 sacrifícios mais dramáticos
top5 = tal_sac.nsmallest(5, 'material_diff')
print(top5[['game_id', 'move_number', 'move_san', 'material_diff', 'comment']])

# Estatísticas por fase
print(df.groupby('phase')['is_sacrifice'].mean() * 100)
```

---

## 🎨 Exemplos de Análise

### 1. Taxa de Sacrifício por Jogador

```python
sacrifice_rate = df.groupby('white')['is_sacrifice'].mean() * 100
top_sacrificers = sacrifice_rate.nlargest(10)
print(top_sacrificers)
```

### 2. Lances Mais Impactantes

```python
# Maiores mudanças de avaliação
impact = df.nlargest(10, 'eval_diff_abs')
print(impact[['white', 'black', 'move_number', 'move_san', 'eval_diff', 'comment']])
```

### 3. Padrões Táticos por Fase

```python
tactics_by_phase = pd.crosstab(df['phase'], df['motif'], normalize='index') * 100
print(tactics_by_phase.round(1))
```

### 4. Heatmap de Sacrifícios

```python
import matplotlib.pyplot as plt

sac_by_move = df[df['is_sacrifice']].groupby('move_number').size()
sac_by_move.plot(kind='bar', figsize=(12, 6))
plt.title('Sacrifícios por Lance')
plt.xlabel('Número do Lance')
plt.ylabel('Quantidade')
plt.show()
```

---

## 🐛 Troubleshooting Express

| Problema | Solução |
|----------|---------|
| `FileNotFoundError: stockfish` | Ajuste `STOCKFISH_PATH` em `config.py` |
| "Nenhum .pgn encontrado" | Verifique extensão dos arquivos (deve ser `.pgn` minúsculo) |
| Muito lento | Use `--quick` ou reduza `--depth` para 10-12 |
| Memória insuficiente | Processe em lotes menores |

---

## 📈 Performance

| Configuração | Velocidade Aproximada |
|--------------|----------------------|
| `--depth 10 --quick` | ~20 lances/seg |
| `--depth 13` (padrão) | ~10-15 lances/seg |
| `--depth 15` | ~5-8 lances/seg |

**Dica:** Para datasets grandes (>100 jogos), use cache ativo (padrão) e considere `--threads 4` se tiver CPU multicore.

---

## 🎯 Próximos Passos

1. ✅ Rode seu primeiro processamento
2. ✅ Analise com `analyze_dataset.py`
3. ✅ Experimente com Pandas/Matplotlib
4. 📖 Leia o [README.md](README.md) completo para features avançadas
5. 🧪 Execute testes: `pytest test_pipeline.py -v`

---

## 💡 Dicas Pro

```bash
# Processa apenas abrindo e meio-jogo (mais rápido)
# Edite features.py e ajuste thresholds

# Exporta apenas CSV (mais rápido)
python main.py --pgn_folder ./pgns --no-json --no-progress

# Máxima performance
python main.py --pgn_folder ./pgns --depth 12 --threads 4 --hash 1024

# Debug detalhado
python main.py --pgn_folder ./pgns --debug
```

---

## 📚 Recursos

- **Documentação completa:** [README.md](README.md)
- **Testes:** `pytest test_pipeline.py -v`
- **Análise avançada:** `analyze_dataset.py --help`

---

**Pronto! Você está preparado para analisar sacrifícios estilo Tal! 🎉**