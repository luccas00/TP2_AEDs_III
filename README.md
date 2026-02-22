# CSI115 – 2025/2 – Algoritmos E Estruturas De Dados III (UFOP/DECSI)

## 👤 Discentes
- **Luccas Carneiro**
- **Thiago Ker**
- **Rany Souza**
- **Marco Antônio**

---

## 🎯 Contexto E Entregável
Este repositório contém o material do **seminário da disciplina CSI115 (AEDs III)** no tema **Redes Sociais E Redes Complexas**, cobrindo os itens exigidos na apresentação:

- Definição do problema
- Modelagem em grafos
- Algoritmo de solução
- Resultados obtidos

O foco é o problema **“Caminho Mais Eficiente Para Viralização”**: em uma rede social, a propagação não depende apenas do menor número de conexões (saltos), mas também da **força das relações** (fricção/custo de repasse).

---

## ✅ Objetivo Do Projeto
Dado um par de usuários `(A, B)`:

1. Determinar o caminho que minimiza **distância topológica** (menor número de saltos).
2. Determinar o caminho que minimiza **custo de repasse** (fricção), derivado da interação entre usuários.
3. Comparar **custo**, **hops** e **caminho** entre os dois critérios.

---

## 🧠 Modelagem (Rede Social → Grafo)
### Representação
- **Usuário** → vértice `v`
- **Relação social** → aresta **não-direcionada** `u ↔ v`
- A rede é **organizada em comunidades**: conexões internas são mais prováveis que conexões entre comunidades.

### Dois Grafos Na Mesma Topologia
Para isolar o impacto do critério de custo, são construídos **dois grafos sobre o mesmo conjunto de vértices e arestas**, mudando apenas o peso:

- **Grafo Baseline (Saltos):** peso = `1` em todas as arestas  
  → otimiza **menor número de hops**
- **Grafo De Fricção (Custo de Repasse):** peso calculado por aresta  
  → otimiza **menor custo total de propagação**

---

## 🧾 Função De Peso (Fricção)
A fricção transforma “interação” em custo aditivo por aresta:

```
peso(u, v) = 1 + α / (1 + interacao(u, v))
```

Leitura:
- `interacao` alta ⇒ relacionamento forte ⇒ **menor custo**
- `interacao` baixa ⇒ relacionamento fraco ⇒ **maior custo**
- `α` (alpha) controla a sensibilidade (quanto a rede “penaliza” relações fracas)

---

## 🧮 Algoritmo Utilizado
### Dijkstra
O algoritmo de caminhos mínimos utilizado é o **Dijkstra**, aplicado separadamente em cada grafo (baseline e fricção), sempre partindo da mesma origem `A`.

### Reconstrução De Caminho
Após executar Dijkstra, o caminho `A → B` é reconstruído via vetor de predecessores (`prev`):

- inicia em `B`
- caminha `prev` até `A`
- inverte a sequência para obter o caminho na ordem correta

---

## 🧱 Estrutura Do Repositório
Principais arquivos do trabalho (os nomes podem variar conforme a organização do zip/entrega):

- `Main.py`  
  Executa os **2 cenários** e imprime no console:
  - `CustoTotal`
  - `Hops`
  - `Caminho` (lista de nós)
  - comparação **Baseline vs Fricção** + detecção de divergência

- `MainBenchmark.py`  
  Executa benchmark (rodadas repetidas por cenário) e grava log com:
  - tempo por rodada
  - custo por rodada
  - hops por rodada
  - médias consolidadas

- `RedeSocial.py`  
  Gerador da rede sintética com:
  - comunidades (conexões internas densas)
  - pontes intercomunidades (relações fracas)
  - dois grafos (baseline e fricção) na mesma topologia

> Observação de governança: o projeto **reutiliza integralmente** as implementações didáticas de `Dijkstra` e da reconstrução por predecessores. A camada deste trabalho é a **modelagem** + **geração de rede** + **análise comparativa**.

---

## ▶️ Como Executar
### 1) Execução dos cenários (prints do console)
```bash
python Main.py
```

O console exibirá:
- **CASO 1 — Mesma Comunidade**
- **CASO 2 — Comunidades Diferentes**
- baseline vs fricção (custo/hops/caminho) + mensagem de divergência quando aplicável

### 2) Execução do benchmark (10 rodadas por cenário)
```bash
python MainBenchmark.py
```

O benchmark gera um arquivo `.txt` (nome definido no script) com a tabela de rodadas e as **médias**.

---

## 🧪 Cenários Avaliados (Padrão do Trabalho)
### Cenário 1 — Mesma Comunidade
- Origem e destino pertencem ao mesmo bloco (comunidade).
- Expectativa: **hops podem coincidir**, porém o **caminho pode divergir** por custo.

### Cenário 2 — Comunidades Diferentes
- Origem e destino pertencem a comunidades diferentes.
- Expectativa: maior chance de divergência devido a **pontes intercomunidades**.
- Mesmo quando o número de hops é igual, a fricção pode trocar totalmente o caminho (otimiza custo, não “curtura” topológica).

---

## 📊 Resultados (Benchmark Consolidado)
Abaixo um resumo das médias (10 rodadas por cenário), conforme logs de benchmark fornecidos:

| Caso | Modelo | Tempo Médio (s) | Custo Médio | Hops Médio |
|------|--------|------------------|------------|-----------|
| 1 (Mesma Comunidade) | Baseline | 0.0199 | 3.00 | 3.00 |
| 1 (Mesma Comunidade) | Fricção  | 0.0136 | 4.6718 | 3.00 |
| 2 (Com. Diferentes)  | Baseline | 0.0175 | 6.00 | 6.00 |
| 2 (Com. Diferentes)  | Fricção  | 0.0139 | 14.2786 | 7.00 |

Leitura executiva:
- **Baseline** otimiza distância topológica (menor número de saltos).
- **Fricção** otimiza custo de repasse; tende a evitar relações fracas, mesmo com mais hops.

---

## 🧷 Nota Sobre Tamanho Da Rede (500 vs 700 usuários)
Nos artefatos de benchmark utilizados no projeto:

- Benchmarks **1, 2, 3 e 7** foram executados com **500 usuários**.
- Benchmarks **4, 5 e 6** foram executados com **700 usuários**.

Resultado prático:
- A tendência se mantém: **baseline minimiza hops** e **fricção minimiza custo**.
- Ao aumentar o tamanho da rede, muda o perfil de tempos e caminhos, mas o comportamento comparativo permanece consistente.

---

## 🧾 Métricas Reportadas
Para cada cenário `(A, B)` reportamos:
- `CustoTotal`: soma dos pesos do caminho
- `Hops`: número de saltos (`|caminho| - 1`)
- `Caminho`: sequência de nós reconstruída via `prev`

---

## 🔁 Reprodutibilidade
- Os scripts utilizam `seed` para reduzir variabilidade e garantir previsibilidade dos experimentos.
- Parâmetros de geração (densidade intra, pontes inter, ranges de interação e `α`) ficam em `RedeSocial.py`/scripts de execução.

---

## 📌 Observações Finais
- Divergência entre caminhos (baseline vs fricção) **é esperada** em redes sociais realistas, principalmente em cenários intercomunidades.
- O desenho de comunidades + pontes é o que materializa a hipótese: **viralização pode preferir relações fortes**, não apenas o “menor caminho em hops”.

