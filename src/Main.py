# -----------------------------------------------------------------------------------------
# Main.py
# -----------------------------------------------------------------------------------------
# Entry-point específico para o experimento de "Caminho Mais Eficiente Para Viralização".
#
# Importante (requisito do grupo/professor):
# - NÃO alterar Algoritmos.py, Grafo.py e a função gerar_rede_social() existente.
# - Aqui usamos um gerador *novo* (gerar_rede_social_realista) para obter resultados
#   mais coerentes/realistas na comparação Baseline vs Fricção.
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

    # força nós "distantes" dentro do bloco
    return (nos[0], nos[-1])


def _par_comunidades_diferentes_sem_aresta(grafo_saltos, comunidade_por_no, c1=0, c2=1, tentativas=5000):
    """Escolhe um par (origem,destino) em comunidades diferentes que NÃO tenha aresta direta.

    Motivo: evitar o caso "1 hop" aleatório (u-v direto) que destrói a narrativa do experimento.
    """
    nos1 = [i for i, c in enumerate(comunidade_por_no) if c == c1]
    nos2 = [i for i, c in enumerate(comunidade_por_no) if c == c2]

    if not nos1 or not nos2:
        return (0, len(comunidade_por_no) - 1)

    # varredura determinística antes de partir para tentativa
    for u in nos1[:50]:
        for v in nos2[:50]:
            if not grafo_saltos.possuiAresta(u, v):
                return (u, v)

    # fallback por tentativa (mantém execução simples)
    idx1 = 0
    idx2 = 0
    while tentativas > 0:
        u = nos1[idx1 % len(nos1)]
        v = nos2[idx2 % len(nos2)]
        if not grafo_saltos.possuiAresta(u, v):
            return (u, v)
        idx1 += 7
        idx2 += 13
        tentativas -= 1

    # se não conseguir, devolve o primeiro mesmo
    return (nos1[0], nos2[0])


def main():
    # ---------------- PARÂMETROS DA REDE (realista) ----------------
    # Ideia: laços fortes dentro da comunidade e pontes fracas entre comunidades.
    num_vertices = 500
    num_comunidades = 3

    # intra: densidade moderada para gerar várias rotas dentro do bloco
    p_intra = 0.02

    # inter: probabilidade baixa (amostragem), com cap por par de comunidades
    # Observação: aqui p_inter é usado como fator de amostragem: alvo ~= p_inter * |C1|*|C2|
    p_inter = 0.0005
    max_pontes_por_par = 8

    seed = 42

    # Interação (realista):
    interacao_intra_min = 20
    interacao_intra_max = 100
    interacao_inter_min = 0
    interacao_inter_max = 5

    # alpha alto aumenta contraste de custo entre laços fortes vs pontes fracas
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

    # -----------------------------------------------------------------
    # Cenários
    # -----------------------------------------------------------------
    # Caso 1: Mesma Comunidade
    origem1, destino1 = _primeiro_par_mesma_comunidade(comunidade_por_no, alvo_comunidade=0)

    # Caso 2: Comunidades Diferentes (0 e 1) - evita aresta direta pra não virar "1 hop"
    origem2, destino2 = _par_comunidades_diferentes_sem_aresta(grafo_saltos, comunidade_por_no, c1=0, c2=1)

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
