# -----------------------------------------------------------------------------------------
# RedeSocial.py
# -----------------------------------------------------------------------------------------
# Geração de uma rede social sintética com "comunidades" (blocos) e pesos de fricção.
#
# Objetivo do experimento:
# - Comparar menor número de saltos (peso=1) vs menor fricção (peso calculado)
#
# Observação:
# - Reusa a estrutura ListaAdjacencias existente em Grafo.py (sem alterar nada do projeto atual).
# -----------------------------------------------------------------------------------------

import random
from Grafo import ListaAdjacencias

def _peso_friccao(interacao, friccao_alpha):
    """
    Modelo de fricção (custo de repasse) por aresta.

    Intuição corporativa:
    - interacao alta => relacionamento forte => menor fricção => menor custo de repasse
    - interacao baixa => relacionamento fraco => maior fricção => maior custo

    Fórmula (custo aditivo):
        peso = 1 + friccao_alpha / (1 + interacao)

    Onde:
    - interacao: inteiro >= 0 (ex.: 0..10)
    - friccao_alpha: controla o "impacto" da fricção.
      Se alpha for baixo demais, o menor número de saltos tende a dominar;
      se alpha for alto, o algoritmo pode preferir caminhos mais longos porém "mais fluidos".
    """
    return 1.0 + (float(friccao_alpha) / (1.0 + float(interacao)))

def gerar_rede_social(
    num_vertices=400,
    num_comunidades=4,
    p_intra=0.06,
    p_inter=0.0005,
    max_pontes_por_par=10,
    seed=42,
    interacao_intra_min=20,
    interacao_intra_max=100,
    interacao_inter_min=0,
    interacao_inter_max=5,
    friccao_alpha=8.0,
    construir_caso3=True
):
    """
    Versão *realista* do gerador, SEM alterar a função gerar_rede_social() já validada.

    Diferenças principais vs gerar_rede_social():
    - Distribuições distintas de interação:
        * Intra-comunidade: interação alta (laços fortes)
        * Inter-comunidade: interação baixa (pontes fracas)
    - Conectividade inter-comunidades por amostragem controlada:
        * Em vez de MAX_PONTES fixo (=2), usa p_inter * |C1|*|C2| com limite max_pontes_por_par
          => cria mais alternativas e reduz a chance de "caminho 1 hop" aleatório dominar.
    - Mantém o grafo NÃO-DIRECIONADO via duplicação (u->v e v->u).

    Retorna:
    - grafo_friccao, grafo_saltos, comunidade_por_no, nos_caso3
    """
    rnd = random.Random(seed)

    if num_comunidades < 2:
        num_comunidades = 2

    # Distribuição simples: comunidades quase do mesmo tamanho
    comunidade_por_no = [0] * num_vertices
    nos_por_comunidade = [[] for _ in range(num_comunidades)]

    for no in range(num_vertices):
        c = int(no * num_comunidades / num_vertices)  # blocos contíguos
        if c >= num_comunidades:
            c = num_comunidades - 1
        comunidade_por_no[no] = c
        nos_por_comunidade[c].append(no)

    grafo_friccao = ListaAdjacencias(num_vertices)
    grafo_saltos = ListaAdjacencias(num_vertices)

    arestas_undirected = set()

    def add_aresta_undirected(u, v, interacao):
        if u == v:
            return

        a = u if u < v else v
        b = v if u < v else u

        if (a, b) in arestas_undirected:
            return

        arestas_undirected.add((a, b))

        peso = _peso_friccao(interacao, friccao_alpha)

        # Não-direcionado => duplica as duas direções
        grafo_friccao.addAresta(u, v, peso)
        grafo_friccao.addAresta(v, u, peso)

        grafo_saltos.addAresta(u, v, 1)
        grafo_saltos.addAresta(v, u, 1)

    # -----------------------------
    # 1) Arestas intra-comunidade (densas)
    # -----------------------------
    for c in range(num_comunidades):
        nos = nos_por_comunidade[c]
        n = len(nos)
        for i in range(n):
            u = nos[i]
            for j in range(i + 1, n):
                v = nos[j]
                if rnd.random() < p_intra:
                    interacao = rnd.randint(interacao_intra_min, interacao_intra_max)
                    add_aresta_undirected(u, v, interacao)

    # -----------------------------
    # 2) Arestas inter-comunidade (pontes fracas e mais realistas)
    # -----------------------------
    for c1 in range(num_comunidades):
        for c2 in range(c1 + 1, num_comunidades):
            nos1 = nos_por_comunidade[c1]
            nos2 = nos_por_comunidade[c2]

            # alvo de pontes (amostragem), com mínimo 1 para garantir pelo menos alguma conectividade
            alvo = int(p_inter * len(nos1) * len(nos2))
            if alvo < 1:
                alvo = 1
            if alvo > max_pontes_por_par:
                alvo = max_pontes_por_par

            for _ in range(alvo):
                u = nos1[rnd.randrange(len(nos1))]
                v = nos2[rnd.randrange(len(nos2))]
                interacao = rnd.randint(interacao_inter_min, interacao_inter_max)
                add_aresta_undirected(u, v, interacao)

    # -----------------------------
    # 3) Caso 3 opcional: "ponte crítica" forçada
    # -----------------------------
    nos_caso3 = None
    if construir_caso3:
        c0 = 0
        c3 = num_comunidades - 1

        c_mid1 = 1 if num_comunidades > 2 else c3
        c_mid2 = 2 if num_comunidades > 3 else c_mid1

        u0 = nos_por_comunidade[c0][0]
        u3 = nos_por_comunidade[c3][0]
        u1 = nos_por_comunidade[c_mid1][0]
        u2 = nos_por_comunidade[c_mid2][0]

        # Aresta direta "ruim": interacao inter mínima => custo alto
        add_aresta_undirected(u0, u3, interacao_inter_min)

        # Rota alternativa "boa": arestas com interação alta
        add_aresta_undirected(u0, u1, interacao_intra_max)
        add_aresta_undirected(u1, u2, interacao_intra_max)
        add_aresta_undirected(u2, u3, interacao_intra_max)

        nos_caso3 = (u0, u3)

    return grafo_friccao, grafo_saltos, comunidade_por_no, nos_caso3
