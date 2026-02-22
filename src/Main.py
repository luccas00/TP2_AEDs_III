# -----------------------------------------------------------------------------------------
# Main.py
#
# Link para Repositorio do Projeto no GitHub
# 
# https://github.com/luccas00/TP2_AEDs_III
# 
# -----------------------------------------------------------------------------------------
from Algoritmos import dijkstra, reconstruir_caminho_prev
from RedeSocial import gerar_rede_social


# Função utilitária para imprimir o relatório comparando Baseline (saltos) vs Fricção para um par origem/destino.
def _relatorio_par(nome, origem, destino, distancias_saltos, prev_saltos, distancias_friccao, prev_friccao):
    
    caminho_saltos = reconstruir_caminho_prev(prev_saltos, origem, destino)
    caminho_friccao = reconstruir_caminho_prev(prev_friccao, origem, destino)

    # Calcula a quantidade de hops (arestas) do caminho baseline; se não existe caminho, fica None.
    hops_saltos = (len(caminho_saltos) - 1) if caminho_saltos else None

    # Calcula a quantidade de hops do caminho por fricção; se não existe caminho, fica None.
    hops_friccao = (len(caminho_friccao) - 1) if caminho_friccao else None

    # Obtém o custo total baseline (distância final no destino, calculada pelo Dijkstra no grafo de saltos).
    custo_saltos = distancias_saltos[destino]

    # Obtém o custo total por fricção (distância final no destino, calculada pelo Dijkstra no grafo de fricção).
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

    # Se ambos caminhos existem e são diferentes, sinaliza divergência (resultado esperado no contexto do experimento).
    if caminho_saltos and caminho_friccao and caminho_saltos != caminho_friccao:
        print("Divergência Detectada: o caminho por fricção difere do caminho por saltos (esperado em redes reais).")
    # Caso contrário, informa que não houve divergência relevante ou não foi possível calcular algum caminho.
    else:
        print("Sem Divergência Relevante: caminhos iguais ou indisponíveis (pode acontecer dependendo do grafo/par).")


# Seleciona um par (origem, destino) dentro da mesma comunidade, priorizando nós “distantes” no bloco.
def _primeiro_par_mesma_comunidade(comunidade_por_no, alvo_comunidade=0):
    # Filtra todos os nós que pertencem à comunidade alvo (ex.: comunidade 0).
    nos = [i for i, c in enumerate(comunidade_por_no) if c == alvo_comunidade]

    # Se a comunidade não tiver ao menos dois nós, retorna um fallback trivial.
    if len(nos) < 2:
        return (0, 1)

    # Retorna o primeiro e o último nó da lista para maximizar distância interna no bloco.
    return (nos[0], nos[-1])


# Escolhe um par em comunidades diferentes, garantindo que NÃO exista aresta direta entre eles.
def _par_comunidades_diferentes_sem_aresta(grafo_saltos, comunidade_por_no, c1=0, c2=1, tentativas=5000):
    # Docstring explica o racional de negócio/experimento: evitar casos de 1 hop por conexão direta aleatória.
    """Escolhe um par (origem,destino) em comunidades diferentes que NÃO tenha aresta direta.

    Motivo: evitar o caso "1 hop" aleatório (u-v direto) que destrói a narrativa do experimento.
    """

    # Lista de nós da comunidade c1.
    nos1 = [i for i, c in enumerate(comunidade_por_no) if c == c1]

    # Lista de nós da comunidade c2.
    nos2 = [i for i, c in enumerate(comunidade_por_no) if c == c2]

    # Se alguma comunidade não existir (lista vazia), retorna fallback origem 0 e último nó.
    if not nos1 or not nos2:
        return (0, len(comunidade_por_no) - 1)

    # Primeiro tenta um “scan” determinístico em subset (até 50x50) para achar par sem aresta direta rapidamente.
    for u in nos1[:50]:
        for v in nos2[:50]:
            # Checa se existe aresta direta no grafo de saltos (peso=1).
            if not grafo_saltos.possuiAresta(u, v):
                # Retorna assim que encontra um par sem conexão direta.
                return (u, v)

    # Fallback por tentativa controlada; mantém execução simples e previsível.
    idx1 = 0  # Índice de varredura para nos1.
    idx2 = 0  # Índice de varredura para nos2.

    # Loop de tentativas para achar um par sem aresta direta.
    while tentativas > 0:
        # Seleciona u ciclando na lista nos1.
        u = nos1[idx1 % len(nos1)]

        # Seleciona v ciclando na lista nos2.
        v = nos2[idx2 % len(nos2)]

        # Condição desejada: não existe aresta direta entre u e v.
        if not grafo_saltos.possuiAresta(u, v):
            return (u, v)

        # Incrementos “saltados” para reduzir repetição e cobrir melhor o espaço de pares.
        idx1 += 7
        idx2 += 13

        # Decrementa contador de tentativas para garantir término.
        tentativas -= 1

    # Se não conseguir, devolve o primeiro par possível (mesmo que tenha aresta direta).
    return (nos1[0], nos2[0])


# Função principal que orquestra geração da rede + execução dos 2 cenários.
def main():
    # ---------------- PARÂMETROS DA REDE ----------------
    # Define o tamanho da rede e a quantidade de comunidades.
    num_vertices = 500
    num_comunidades = 3

    # Probabilidade de aresta intra-comunidade (densidade dentro do bloco).
    p_intra = 0.04

    # Fator de amostragem para pontes inter-comunidades.
    p_inter = 0.002

    # Limite máximo de pontes entre cada par de comunidades.
    max_pontes_por_par = 3

    # Seed para reprodutibilidade do experimento (mesma rede a cada execução).
    seed = 42

    # Faixa de “interação” dentro da comunidade (relacionamento forte).
    interacao_intra_min = 20
    interacao_intra_max = 100

    # Faixa de “interação” entre comunidades (relacionamento fraco).
    interacao_inter_min = 0
    interacao_inter_max = 5

    # Parâmetro que controla o impacto da fricção no peso das arestas.
    friccao_alpha = 30.0

    # Gera os dois grafos:
    # - grafo_friccao: pesos calculados por fricção (custo de repasse)
    # - grafo_saltos: pesos fixos 1 (minimiza hops)
    # - comunidade_por_no: mapeamento nó -> comunidade
    grafo_friccao, grafo_saltos, comunidade_por_no = gerar_rede_social(
        num_vertices=num_vertices,                 # Tamanho da rede
        num_comunidades=num_comunidades,           # Número de comunidades
        p_intra=p_intra,                           # Densidade intra
        p_inter=p_inter,                           # Amostragem inter
        max_pontes_por_par=max_pontes_por_par,     # Cap de pontes
        seed=seed,                                 # Reprodutibilidade
        interacao_intra_min=interacao_intra_min,   # Interação intra mínima
        interacao_intra_max=interacao_intra_max,   # Interação intra máxima
        interacao_inter_min=interacao_inter_min,   # Interação inter mínima
        interacao_inter_max=interacao_inter_max,   # Interação inter máxima
        friccao_alpha=friccao_alpha               # Intensidade da fricção
    )

    # -----------------------------------------------------------------
    # Cenários
    # -----------------------------------------------------------------

    # Caso 1 (mesma comunidade). Seleciona um par dentro do mesmo bloco.
    origem1, destino1 = _primeiro_par_mesma_comunidade(comunidade_por_no, alvo_comunidade=0)

    # Caso 2 (comunidades diferentes). Seleciona um par sem aresta direta para evitar hop=1.
    origem2, destino2 = _par_comunidades_diferentes_sem_aresta(grafo_saltos, comunidade_por_no, c1=0, c2=1)

    # Executa Dijkstra no grafo de saltos e fricção para o Cenário 1 (baseline).
    dist_s1, prev_s1 = dijkstra(grafo_saltos, origem1)
    dist_f1, prev_f1 = dijkstra(grafo_friccao, origem1)

    _relatorio_par("CASO 1 — Mesma Comunidade", origem1, destino1, dist_s1, prev_s1, dist_f1, prev_f1)

    # Executa Dijkstra no grafo de saltos e fricção para o Cenário 2
    dist_s2, prev_s2 = dijkstra(grafo_saltos, origem2)
    dist_f2, prev_f2 = dijkstra(grafo_friccao, origem2)

    _relatorio_par("CASO 2 — Comunidades Diferentes", origem2, destino2, dist_s2, prev_s2, dist_f2, prev_f2)


if __name__ == "__main__":
    main()