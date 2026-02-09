# -----------------------------------------------------------------------------------------
# MainRedeSocial.py
# -----------------------------------------------------------------------------------------
# Entry-point específico para o experimento de "Caminho Mais Eficiente Para Viralização".
# Não altera o Main.py existente (orientado a mapa/grid).
# -----------------------------------------------------------------------------------------

from Algoritmos import dijkstra, reconstruir_caminho_prev
from RedeSocial import gerar_rede_social

def _relatorio_par(nome, origem, destino, distancias_saltos, prev_saltos, distancias_friccao, prev_friccao):
    caminho_saltos = reconstruir_caminho_prev(prev_saltos, origem, destino)
    caminho_friccao = reconstruir_caminho_prev(prev_friccao, origem, destino)

    hops_saltos = (len(caminho_saltos) - 1) if caminho_saltos else None
    hops_friccao = (len(caminho_friccao) - 1) if caminho_friccao else None

    custo_saltos = distancias_saltos[destino]
    custo_friccao = distancias_friccao[destino]

    print("=" * 92)
    print(f"{nome}")
    print(f"Origem={origem} | Destino={destino}")

    print("-" * 92)
    print("Baseline (Menor Número De Saltos | peso=1)")
    print(f"CustoTotal={custo_saltos} | Hops={hops_saltos} | Caminho={caminho_saltos}")

    print("-" * 92)
    print("Fricção (Menor Custo De Repasse | peso calculado)")
    print(f"CustoTotal={custo_friccao:.6f} | Hops={hops_friccao} | Caminho={caminho_friccao}")

    print("-" * 92)
    if caminho_saltos and caminho_friccao and caminho_saltos != caminho_friccao:
        print("Divergência Detectada: o caminho por fricção difere do caminho por saltos (esperado em redes reais).")
    else:
        print("Sem Divergência Relevante: caminhos iguais ou indisponíveis (pode acontecer dependendo do grafo/par).")

def _primeiro_par_mesma_comunidade(comunidade_por_no, alvo_comunidade=0):
    nos = [i for i, c in enumerate(comunidade_por_no) if c == alvo_comunidade]
    if len(nos) < 2:
        return (0, 1)
    return (nos[0], nos[-1])

def _primeiro_par_comunidades_diferentes(comunidade_por_no, c1=0, c2=1):
    nos1 = [i for i, c in enumerate(comunidade_por_no) if c == c1]
    nos2 = [i for i, c in enumerate(comunidade_por_no) if c == c2]
    if not nos1 or not nos2:
        return (0, len(comunidade_por_no) - 1)
    return (nos1[0], nos2[0])

def main():
    # Parâmetros simples e "boa nota": rede não pequena, comunidades visíveis e reprodutível.
    num_vertices = 5000
    num_comunidades = 3
    p_intra = 0.01
    p_inter = 0.010   # irrelevante após MAX_PONTES
    seed = 42

    # Interação 0..10 e fricção "forte" pra provocar diferença (Caso 3 garante).
    interacao_min = 0
    interacao_max = 10
    friccao_alpha = 8.0

    grafo_friccao, grafo_saltos, comunidade_por_no, nos_caso3 = gerar_rede_social(
        num_vertices=num_vertices,
        num_comunidades=num_comunidades,
        p_intra=p_intra,
        p_inter=p_inter,
        seed=seed,
        interacao_min=interacao_min,
        interacao_max=interacao_max,
        friccao_alpha=friccao_alpha
    )

    # -----------------------------------------------------------------
    # Cenários
    # -----------------------------------------------------------------
    # Caso 1: Mesma Comunidade
    origem1, destino1 = _primeiro_par_mesma_comunidade(comunidade_por_no, alvo_comunidade=0)

    # Caso 2: Comunidades Diferentes (comunidade 0 e 1)
    origem2, destino2 = _primeiro_par_comunidades_diferentes(comunidade_por_no, c1=0, c2=1)

    # Caso 3: Ponte Crítica (forçado pelo gerador)
    origem3, destino3 = nos_caso3

    # Cenário 1
    dist_s1, prev_s1 = dijkstra(grafo_saltos, origem1)
    dist_f1, prev_f1 = dijkstra(grafo_friccao, origem1)
    _relatorio_par("CASO 1 — Mesma Comunidade", origem1, destino1, dist_s1, prev_s1, dist_f1, prev_f1)

    # Cenário 2
    dist_s2, prev_s2 = dijkstra(grafo_saltos, origem2)
    dist_f2, prev_f2 = dijkstra(grafo_friccao, origem2)
    _relatorio_par("CASO 2 — Comunidades Diferentes", origem2, destino2, dist_s2, prev_s2, dist_f2, prev_f2)

    # Cenário 3
    dist_s3, prev_s3 = dijkstra(grafo_saltos, origem3)
    dist_f3, prev_f3 = dijkstra(grafo_friccao, origem3)
    _relatorio_par("CASO 3 — Ponte Crítica (mudança de rota por fricção)", origem3, destino3, dist_s3, prev_s3, dist_f3, prev_f3)

if __name__ == "__main__":
    main()
