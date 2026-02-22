# -----------------------------------------------------------------------------------------
# MainBenchmark.py
# -----------------------------------------------------------------------------------------
# Benchmark do experimento "Caminho Mais Eficiente Para Viralização".
#
# Importante:
# - NÃO alterar Algoritmos.py e Grafo.py.
# - Usamos o gerador novo gerar_rede_social_realista() para gerar cenários mais coerentes.
# -----------------------------------------------------------------------------------------

import time
from Algoritmos import dijkstra, reconstruir_caminho_prev
from RedeSocial import gerar_rede_social

RODADAS = 10
LOG_FILE = "benchmark_rede_social.txt"


def executar_dijkstra(grafo, origem, destino):
    inicio = time.time()
    dist, prev = dijkstra(grafo, origem)
    fim = time.time()

    caminho = reconstruir_caminho_prev(prev, origem, destino)
    hops = len(caminho) - 1 if caminho else None
    custo = dist[destino]

    return fim - inicio, custo, hops, caminho


def benchmark_caso(nome, grafo_saltos, grafo_friccao, origem, destino, log):

    log.write("=" * 90 + "\n")
    log.write(f"{nome}\n")
    log.write(f"Origem={origem} | Destino={destino}\n")
    log.write("=" * 90 + "\n")

    # ---------------- SALTOS ----------------
    log.write("Executando Dijkstra (Saltos | peso=1)\n")
    log.write("Rodada | Tempo(s) | Custo | Hops | Status\n")

    tempos_s, custos_s, hops_s = [], [], []

    for i in range(RODADAS):
        t, c, h, _ = executar_dijkstra(grafo_saltos, origem, destino)
        tempos_s.append(t)
        custos_s.append(c)
        hops_s.append(h)

        log.write(f"{i + 1:<6} | {t:.6f} | {c} | {h} | OK\n")

    log.write(
        f"MÉDIA SALTOS: Tempo={sum(tempos_s) / RODADAS:.6f} | "
        f"Custo={sum(custos_s) / RODADAS:.2f} | "
        f"Hops={sum(hops_s) / RODADAS:.2f}\n\n"
    )

    # ---------------- FRICÇÃO ----------------
    log.write("Executando Dijkstra (Fricção | peso calculado)\n")
    log.write("Rodada | Tempo(s) | Custo | Hops | Status\n")

    tempos_f, custos_f, hops_f = [], [], []

    for i in range(RODADAS):
        t, c, h, _ = executar_dijkstra(grafo_friccao, origem, destino)
        tempos_f.append(t)
        custos_f.append(c)
        hops_f.append(h)

        log.write(f"{i + 1:<6} | {t:.6f} | {c:.6f} | {h} | OK\n")

    log.write(
        f"MÉDIA FRICÇÃO: Tempo={sum(tempos_f) / RODADAS:.6f} | "
        f"Custo={sum(custos_f) / RODADAS:.4f} | "
        f"Hops={sum(hops_f) / RODADAS:.2f}\n\n"
    )


def _primeiro_par_mesma_comunidade(comunidade_por_no, alvo_comunidade=0):
    nos = [i for i, c in enumerate(comunidade_por_no) if c == alvo_comunidade]
    if len(nos) < 2:
        return (0, 1)
    return (nos[0], nos[-1])


def _par_comunidades_diferentes_sem_aresta(grafo_saltos, comunidade_por_no, c1=0, c2=1, tentativas=10000):
    nos1 = [i for i, c in enumerate(comunidade_por_no) if c == c1]
    nos2 = [i for i, c in enumerate(comunidade_por_no) if c == c2]
    if not nos1 or not nos2:
        return (0, len(comunidade_por_no) - 1)

    # tenta achar um par sem aresta direta (evita hop=1)
    i1 = 0
    i2 = 0
    while tentativas > 0:
        u = nos1[i1 % len(nos1)]
        v = nos2[i2 % len(nos2)]
        if not grafo_saltos.possuiAresta(u, v):
            return (u, v)
        i1 += 17
        i2 += 31
        tentativas -= 1

    return (nos1[0], nos2[0])


def main():

    # ---------------- PARÂMETROS DA REDE ----------------
    num_vertices = 5000
    num_comunidades = 5
    p_intra = 0.02
    p_inter = 0.0002
    max_pontes_por_par = 10
    seed = 42

    interacao_intra_min = 20
    interacao_intra_max = 100
    interacao_inter_min = 0
    interacao_inter_max = 5

    friccao_alpha = 30.0

    grafo_friccao, grafo_saltos, comunidade_por_no, nos_caso3 = gerar_rede_social(
        num_vertices=num_vertices,
        num_comunidades=num_comunidades,
        p_intra=p_intra,
        p_inter=p_inter,
        max_pontes_por_par=max_pontes_por_par,
        seed=seed,
        interacao_intra_min=interacao_intra_min,
        interacao_intra_max=interacao_intra_max,
        interacao_inter_min=interacao_inter_min,
        interacao_inter_max=interacao_inter_max,
        friccao_alpha=friccao_alpha,
        construir_caso3=True
    )

    # --------- DEFINIÇÃO DOS PARES ---------
    origem1, destino1 = _primeiro_par_mesma_comunidade(comunidade_por_no, alvo_comunidade=0)
    origem2, destino2 = _par_comunidades_diferentes_sem_aresta(grafo_saltos, comunidade_por_no, c1=0, c2=1)
    origem3, destino3 = nos_caso3

    with open(LOG_FILE, "w", encoding="utf-8") as log:
        log.write("BENCHMARK — CAMINHO MAIS EFICIENTE PARA VIRALIZAÇÃO\n")
        log.write(f"Rodadas por cenário: {RODADAS}\n")
        log.write("Modelo: Grafo não-direcionado | Baseline(peso=1) vs Fricção(peso calculado)\n\n")

        benchmark_caso(
            "CASO 1 — Mesma Comunidade",
            grafo_saltos, grafo_friccao,
            origem1, destino1, log
        )

        benchmark_caso(
            "CASO 2 — Comunidades Diferentes",
            grafo_saltos, grafo_friccao,
            origem2, destino2, log
        )

        benchmark_caso(
            "CASO 3 — Ponte Crítica",
            grafo_saltos, grafo_friccao,
            origem3, destino3, log
        )

    print(f"Benchmark finalizado. Log salvo em: {LOG_FILE}")


if __name__ == "__main__":
    main()
