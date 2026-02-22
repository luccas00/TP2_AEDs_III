# -----------------------------------------------------------------------------------------
# RedeSocial.py
# -----------------------------------------------------------------------------------------
# Este arquivo implementa o gerador da rede social sintética, com comunidades e pesos.

# Geração de uma rede social sintética com "comunidades" (blocos) e pesos de fricção.
# O gerador cria:
# - blocos (comunidades) com maior densidade interna
# - pontes inter-blocos com interações fracas e, portanto, maior fricção

# Objetivo do experimento:
# - Comparar menor número de saltos (peso=1) vs menor fricção (peso calculado)
# São gerados dois grafos: um para hops e outro para custo de repasse.

import random
from Grafo import ListaAdjacencias

# Função interna que calcula o peso (custo) de uma aresta no grafo de fricção.
def _peso_friccao(interacao, friccao_alpha):
    """
    Documenta a regra de negócio usada para converter "interação" em "custo de repasse".
    Modelo de fricção (custo de repasse) por aresta.

    Intuição corporativa:
    - interacao alta => relacionamento forte => menor fricção => menor custo de repasse
    - interacao baixa => relacionamento fraco => maior fricção => maior custo

    Fórmula (custo aditivo):
        peso = 1 + friccao_alpha / (1 + interacao)

    Onde:
    - interacao: inteiro >= 0 (ex.: 0..10)
    - friccao_alpha: controla o "impacto" da fricção.
    """
    return 1.0 + (float(friccao_alpha) / (1.0 + float(interacao)))

# Função pública do módulo que gera a rede social e retorna os dois grafos + mapa de comunidades.
def gerar_rede_social(
    num_vertices=4000,              # Quantidade total de nós (Usuários).
    num_comunidades=4,              # Quantidade de comunidades (blocos).
    p_intra=0.06,                   # Probabilidade de aresta dentro de uma comunidade.
    p_inter=0.0005,                 # Fator de amostragem de pontes entre comunidades.
    max_pontes_por_par=10,          # Limite de pontes entre cada par de comunidades.
    seed=42,                        # Seed para reprodutibilidade.
    interacao_intra_min=20,         # Interação mínima intra-comunidade.
    interacao_intra_max=100,        # Interação máxima intra-comunidade.
    interacao_inter_min=0,          # Interação mínima inter-comunidade.
    interacao_inter_max=5,          # Interação máxima inter-comunidade.
    friccao_alpha=8.0               # Intensidade do custo de fricção.
):
    """
    Docstring explicativa do gerador.

    Retorna:
    - grafo_friccao, grafo_saltos, comunidade_por_no
    """

    rnd = random.Random(seed)

    # Garante pelo menos 2 comunidades para existir “inter-comunidade”.
    if num_comunidades < 2:
        num_comunidades = 2

    # Inicializa vetor nó->comunidade com zeros.
    comunidade_por_no = [0] * num_vertices

    # Lista de listas: cada posição c terá os nós daquela comunidade.
    nos_por_comunidade = [[] for _ in range(num_comunidades)]

    # Distribui nós em blocos contíguos (comunidades por faixa de índice).
    for no in range(num_vertices):
        # Calcula a comunidade com divisão proporcional do range de nós.
        c = int(no * num_comunidades / num_vertices)  # blocos contíguos

        # Proteção para não estourar o índice (edge-case no último nó).
        if c >= num_comunidades:
            c = num_comunidades - 1

        # Registra a comunidade do nó.
        comunidade_por_no[no] = c

        # Adiciona o nó na lista da comunidade correspondente.
        nos_por_comunidade[c].append(no)

    # Cria grafo de fricção (ponderado) com N vértices.
    grafo_friccao = ListaAdjacencias(num_vertices)

    # Cria grafo baseline (peso 1) com N vértices.
    grafo_saltos = ListaAdjacencias(num_vertices)

    # Set para controlar arestas não-direcionadas (evita duplicidade u-v).
    arestas_undirected = set()

    # Função interna para adicionar uma aresta “não-direcionada” (duplica u->v e v->u).
    def add_aresta_undirected(u, v, interacao):
        # Ignora laço (aresta do nó para ele mesmo).
        if u == v:
            return

        # Normaliza ordem (a,b) para representar a aresta não-direcionada.
        a = u if u < v else v
        b = v if u < v else u

        # Se a aresta já foi adicionada, não adiciona de novo.
        if (a, b) in arestas_undirected:
            return

        # Registra a aresta como existente no set de controle.
        arestas_undirected.add((a, b))

        # Calcula o peso de fricção baseado na interação e no alpha.
        peso = _peso_friccao(interacao, friccao_alpha)

        # Como o grafo é NÃO-direcionado, adiciona as duas direções no grafo de fricção.
        grafo_friccao.addAresta(u, v, peso)
        grafo_friccao.addAresta(v, u, peso)

        # No baseline, o peso é 1 em ambas direções (hops).
        grafo_saltos.addAresta(u, v, 1)
        grafo_saltos.addAresta(v, u, 1)

    # -----------------------------
    # 1) Arestas intra-comunidade (densas)
    # -----------------------------
    # Itera cada comunidade para criar conexões internas com probabilidade p_intra.
    for c in range(num_comunidades):
        # Lista de nós da comunidade c.
        nos = nos_por_comunidade[c]

        # Quantidade de nós no bloco.
        n = len(nos)

        # Duplo loop para pares (u,v) dentro do bloco, sem repetir pares.
        for i in range(n):
            # Nó u na posição i.
            u = nos[i]
            for j in range(i + 1, n):
                # Nó v na posição j, com j>i para evitar duplicidade.
                v = nos[j]

                # Sorteia se cria aresta, de acordo com p_intra.
                if rnd.random() < p_intra:
                    # Define a interação intra como alta (forte).
                    interacao = rnd.randint(interacao_intra_min, interacao_intra_max)

                    # Adiciona aresta não-direcionada nos dois grafos.
                    add_aresta_undirected(u, v, interacao)

    # -----------------------------
    # 2) Arestas inter-comunidade (pontes fracas e mais realistas)
    # -----------------------------
    # Itera todos os pares de comunidades (c1,c2) com c2>c1.
    for c1 in range(num_comunidades):
        for c2 in range(c1 + 1, num_comunidades):
            # Nós da comunidade c1.
            nos1 = nos_por_comunidade[c1]

            # Nós da comunidade c2.
            nos2 = nos_por_comunidade[c2]

            # Calcula alvo de pontes com base em p_inter e no tamanho do produto cartesiano.
            alvo = int(p_inter * len(nos1) * len(nos2))

            # Garante pelo menos 1 ponte para manter conectividade mínima entre comunidades.
            if alvo < 1:
                alvo = 1

            # Aplica limite máximo por par de comunidades (governança de densidade).
            if alvo > max_pontes_por_par:
                alvo = max_pontes_por_par

            # Cria "alvo" pontes amostrando aleatoriamente pares (u,v) entre comunidades.
            for _ in range(alvo):
                # Seleciona u aleatório dentro de nos1.
                u = nos1[rnd.randrange(len(nos1))]

                # Seleciona v aleatório dentro de nos2.
                v = nos2[rnd.randrange(len(nos2))]

                # Interação inter é baixa (ponte fraca).
                interacao = rnd.randint(interacao_inter_min, interacao_inter_max)

                # Adiciona aresta não-direcionada nos dois grafos (fricção e saltos).
                add_aresta_undirected(u, v, interacao)

    # Retorna os dois grafos e o vetor comunidade_por_no.
    return grafo_friccao, grafo_saltos, comunidade_por_no