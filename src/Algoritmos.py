
# -----------------------------------------------------------------------------------------
# Implementação do algoritmo de Dijkstra conforme pseudocódigo
# -----------------------------------------------------------------------------------------

INF = float("inf") 

def dijkstra(grafo, origem):
    total_vertices = grafo.numVertices
    distancias = [INF] * total_vertices
    predecessor = [None] * total_vertices
    distancias[origem] = 0
    predecessor[origem] = origem
    abertos = set(range(total_vertices))
    fechados = set()
    while fechados != set(range(total_vertices)):
        vertice_atual = next(iter(abertos))
        menor_distancia = distancias[vertice_atual]
        for v in abertos:
            if distancias[v] < menor_distancia:
                menor_distancia = distancias[v]
                vertice_atual = v
                
        fechados.add(vertice_atual)
        abertos.remove(vertice_atual)
        for (vizinho, peso) in grafo.vizinhos(vertice_atual):
            if vizinho not in fechados:    
                distancia_alternativa = distancias[vertice_atual] + peso
                if distancias[vizinho] > distancia_alternativa:
                    distancias[vizinho] = distancia_alternativa
                    predecessor[vizinho] = vertice_atual

    # retorna as listas dist e prev
    return distancias, predecessor

# -----------------------------
# Reconstrução de Caminho (prev por vértice)
# -----------------------------
def reconstruir_caminho_prev(prev, s, t):
    
    if s == t:
        return [s]

    if prev[t] is None:
        return []

    caminho = []

    # começa pelo destino e volta usando o vetor de predecessores
    vertice_atual = t

    max_passos = len(prev)
    passos = 0

    while True:
        # adiciona o vértice atual ao caminho
        caminho.append(vertice_atual)

        # se chegou na origem, finaliza
        if vertice_atual == s:
            break

        # anda para o predecessor do vértice atual
        vertice_atual = prev[vertice_atual]

        if vertice_atual is None:
            return []

        passos += 1
        if passos > max_passos:
            return []  # prev contém ciclo/inconsistência

    # inverte para ficar na ordem correta: s -> ... -> t
    caminho.reverse()
    return caminho
