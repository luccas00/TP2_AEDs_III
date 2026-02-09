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
    p_inter=0.010,
    seed=42,
    interacao_min=0,
    interacao_max=10,
    friccao_alpha=5.0
):
    """
    Gera uma rede social sintética com comunidades (sem detecção de comunidade).
    Estratégia: blocos com alta densidade interna (p_intra) e poucas pontes (p_inter).

    Retorna:
    - grafo_friccao: ListaAdjacencias com pesos pela fricção
    - grafo_saltos:  ListaAdjacencias com peso=1 (baseline de hops)
    - comunidade_por_no: lista[int] com id da comunidade de cada nó
    - nos_caso3: tupla (origem, destino) preparada para o caso 3 (ponte crítica)
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

    # Para evitar aresta duplicada (v1->v2 e v2->v1), controlamos por set de pares não-direcionados
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

        # Rede social não-direcionada => adiciona as duas direções
        grafo_friccao.addAresta(u, v, peso)
        grafo_friccao.addAresta(v, u, peso)

        grafo_saltos.addAresta(u, v, 1)
        grafo_saltos.addAresta(v, u, 1)

    # -----------------------------
    # 1) Arestas intra-comunidade
    # -----------------------------
    for c in range(num_comunidades):
        nos = nos_por_comunidade[c]
        n = len(nos)
        for i in range(n):
            u = nos[i]
            for j in range(i + 1, n):
                v = nos[j]
                if rnd.random() < p_intra:
                    interacao = rnd.randint(interacao_min, interacao_max)
                    add_aresta_undirected(u, v, interacao)

    # -----------------------------
    # 2) Arestas inter-comunidade (pontes CONTROLADAS)
    # -----------------------------
    MAX_PONTES = 2  # número máximo de ligações entre cada par de comunidades

    for c1 in range(num_comunidades):
        for c2 in range(c1 + 1, num_comunidades):

            nos1 = nos_por_comunidade[c1]
            nos2 = nos_por_comunidade[c2]

            pontes_criadas = 0

            while pontes_criadas < MAX_PONTES:
                u = nos1[rnd.randrange(len(nos1))]
                v = nos2[rnd.randrange(len(nos2))]

                interacao = rnd.randint(interacao_min, interacao_max)
                add_aresta_undirected(u, v, interacao)

                pontes_criadas += 1


    # -----------------------------
    # 3) "Ponte crítica" (Caso 3) - construída de propósito
    # -----------------------------
    c0 = 0
    c1 = 1
    c2 = 2 if num_comunidades > 2 else 1
    c3 = num_comunidades - 1

    # Seleciona nós "representantes"
    u0 = nos_por_comunidade[c0][0]
    u1 = nos_por_comunidade[c1][0]
    u2 = nos_por_comunidade[c2][0]
    u3 = nos_por_comunidade[c3][0]

    # Aresta direta muito friccionada (interacao baixa)
    add_aresta_undirected(u0, u3, interacao_min)

    # Rota alternativa com interacao alta (baixo custo relativo)
    inter_alta = interacao_max
    add_aresta_undirected(u0, u1, inter_alta)
    add_aresta_undirected(u1, u2, inter_alta)
    add_aresta_undirected(u2, u3, inter_alta)

    nos_caso3 = (u0, u3)

    return grafo_friccao, grafo_saltos, comunidade_por_no, nos_caso3
