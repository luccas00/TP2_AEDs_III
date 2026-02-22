# -----------------------------------------------------------------------------------------
# MainBenchmark.py
# -----------------------------------------------------------------------------------------
# Este arquivo roda benchmark com múltiplas rodadas e escreve o log em arquivo.

# Benchmark do experimento "Caminho Mais Eficiente Para Viralização".
# Objetivo é medir tempo, custo e hops médios por cenário e por modelo.

#
# Importante:
# - NÃO alterar Algoritmos.py e Grafo.py.
# Mantém restrição do trabalho, benchmark só chama APIs existentes.

# - Usamos o gerador novo gerar_rede_social_realista() para gerar cenários mais coerentes.
# Usa o mesmo gerador de rede realista do experimento principal.
# -----------------------------------------------------------------------------------------

# Importa o módulo time para medir tempo de execução.
import time

# Importa dijkstra e reconstrução do caminho (mesmo stack do experimento).
from Algoritmos import dijkstra, reconstruir_caminho_prev

# Importa o gerador da rede social.
from RedeSocial import gerar_rede_social

# Quantidade de rodadas por cenário para tirar média.
RODADAS = 10

# Nome do arquivo de log gerado pelo benchmark.
LOG_FILE = "benchmark_rede_social.txt"


# Executa Dijkstra em um grafo para um par (origem, destino) e retorna métricas de benchmark.
def executar_dijkstra(grafo, origem, destino):
    # Marca o tempo inicial (timestamp).
    inicio = time.time()

    # Executa Dijkstra a partir da origem retornando distâncias e predecessores.
    dist, prev = dijkstra(grafo, origem)

    # Marca o tempo final após o cálculo.
    fim = time.time()

    # Reconstrói o caminho final (lista de nós) usando o vetor de predecessores.
    caminho = reconstruir_caminho_prev(prev, origem, destino)

    # Calcula hops como quantidade de arestas (nós-1). Se não tem caminho, deixa None.
    hops = len(caminho) - 1 if caminho else None

    # Captura o custo total até o destino usando o array dist do Dijkstra.
    custo = dist[destino]

    # Retorna tempo gasto (fim-inicio), custo, hops e o caminho em si.
    return fim - inicio, custo, hops, caminho


# Roda o benchmark de um caso completo (saltos e fricção) e escreve no log.
def benchmark_caso(nome, grafo_saltos, grafo_friccao, origem, destino, log):

    # Linha separadora para padronizar log e facilitar leitura.
    log.write("=" * 90 + "\n")

    # Escreve o nome do caso (ex.: CASO 1 — Mesma Comunidade).
    log.write(f"{nome}\n")

    # Escreve origem e destino usados no caso.
    log.write(f"Origem={origem} | Destino={destino}\n")

    # Fecha a “capa” do caso com outra linha separadora.
    log.write("=" * 90 + "\n")

    # ---------------- SALTOS ----------------
    # Inicia seção baseline.
    log.write("Executando Dijkstra (Saltos | peso=1)\n")

    # Cabeçalho da tabela por rodada.
    log.write("Rodada | Tempo(s) | Custo | Hops | Status\n")

    # Vetores para acumular métricas e calcular média.
    tempos_s, custos_s, hops_s = [], [], []

    # Loop das RODADAS para baseline (saltos).
    for i in range(RODADAS):
        # Executa Dijkstra no grafo baseline.
        t, c, h, _ = executar_dijkstra(grafo_saltos, origem, destino)

        # Armazena tempo para cálculo de média.
        tempos_s.append(t)

        # Armazena custo para cálculo de média.
        custos_s.append(c)

        # Armazena hops para cálculo de média.
        hops_s.append(h)

        # Escreve linha da rodada formatada.
        log.write(f"{i + 1:<6} | {t:.6f} | {c} | {h} | OK\n")

    # Após as rodadas, escreve as médias baseline.
    log.write(
        f"MÉDIA SALTOS: Tempo={sum(tempos_s) / RODADAS:.6f} | "
        f"Custo={sum(custos_s) / RODADAS:.2f} | "
        f"Hops={sum(hops_s) / RODADAS:.2f}\n\n"
    )

    # ---------------- FRICÇÃO ----------------
    # Inicia seção fricção.
    log.write("Executando Dijkstra (Fricção | peso calculado)\n")

    # Cabeçalho da tabela por rodada para fricção.
    log.write("Rodada | Tempo(s) | Custo | Hops | Status\n")

    # Vetores para acumular métricas e calcular média (fricção).
    tempos_f, custos_f, hops_f = [], [], []

    # Loop das RODADAS para fricção.
    for i in range(RODADAS):
        # Executa Dijkstra no grafo ponderado por fricção.
        t, c, h, _ = executar_dijkstra(grafo_friccao, origem, destino)

        # Armazena tempo.
        tempos_f.append(t)

        # Armazena custo (float).
        custos_f.append(c)

        # Armazena hops.
        hops_f.append(h)

        # Escreve linha da rodada com custo formatado.
        log.write(f"{i + 1:<6} | {t:.6f} | {c:.6f} | {h} | OK\n")

    # Após as rodadas, escreve as médias fricção.
    log.write(
        f"MÉDIA FRICÇÃO: Tempo={sum(tempos_f) / RODADAS:.6f} | "
        f"Custo={sum(custos_f) / RODADAS:.4f} | "
        f"Hops={sum(hops_f) / RODADAS:.2f}\n\n"
    )


# Seleciona par dentro da mesma comunidade (primeiro e último nó).
def _primeiro_par_mesma_comunidade(comunidade_por_no, alvo_comunidade=0):
    # Filtra os nós da comunidade alvo.
    nos = [i for i, c in enumerate(comunidade_por_no) if c == alvo_comunidade]

    # Se insuficiente, fallback trivial.
    if len(nos) < 2:
        return (0, 1)

    # Usa extremos para aumentar distância interna no bloco.
    return (nos[0], nos[-1])


# Seleciona par em comunidades diferentes sem aresta direta (evita hop=1).
def _par_comunidades_diferentes_sem_aresta(grafo_saltos, comunidade_por_no, c1=0, c2=1, tentativas=10000):
    # Filtra nós da comunidade 1.
    nos1 = [i for i, c in enumerate(comunidade_por_no) if c == c1]

    # Filtra nós da comunidade 2.
    nos2 = [i for i, c in enumerate(comunidade_por_no) if c == c2]

    # Se alguma lista vazia, fallback.
    if not nos1 or not nos2:
        return (0, len(comunidade_por_no) - 1)

    # Loop de tentativas para achar um par sem aresta direta.
    i1 = 0
    i2 = 0
    while tentativas > 0:
        # Seleciona u ciclando.
        u = nos1[i1 % len(nos1)]

        # Seleciona v ciclando.
        v = nos2[i2 % len(nos2)]

        # Se não tem aresta direta, ok.
        if not grafo_saltos.possuiAresta(u, v):
            return (u, v)

        # Incrementos para diversificar a busca.
        i1 += 17
        i2 += 31

        # Decrementa tentativas para garantir término.
        tentativas -= 1

    # Se falhar, retorna primeiro par (mesmo que tenha aresta direta).
    return (nos1[0], nos2[0])


# Função principal do benchmark.
def main():

    # ---------------- PARÂMETROS DA REDE ----------------
    # Define o tamanho padrão do benchmark.
    num_vertices = 1000

    # Número de comunidades.
    num_comunidades = 3

    # Densidade intra-comunidade.
    p_intra = 0.04

    # Fator de amostragem para pontes inter-comunidades.
    p_inter = 0.002

    # Cap de pontes por par de comunidades.
    max_pontes_por_par = 10

    # Seed para reprodutibilidade.
    seed = 42

    # Range de interações fortes (intra).
    interacao_intra_min = 20
    interacao_intra_max = 100

    # Range de interações fracas (inter).
    interacao_inter_min = 0
    interacao_inter_max = 5

    # Intensidade do impacto da fricção no peso.
    friccao_alpha = 30.0

    # Gera os grafos para baseline e fricção + mapa de comunidade.
    grafo_friccao, grafo_saltos, comunidade_por_no = gerar_rede_social(
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
        friccao_alpha=friccao_alpha
    )

    # --------- DEFINIÇÃO DOS PARES ---------
    # Caso 1: par dentro da mesma comunidade.
    origem1, destino1 = _primeiro_par_mesma_comunidade(comunidade_por_no, alvo_comunidade=0)

    # Caso 2: par entre comunidades diferentes sem aresta direta.
    origem2, destino2 = _par_comunidades_diferentes_sem_aresta(grafo_saltos, comunidade_por_no, c1=0, c2=1)

    # Abre o arquivo de log para escrita (sobrescreve).
    with open(LOG_FILE, "w", encoding="utf-8") as log:
        # Cabeçalho geral do benchmark.
        log.write("BENCHMARK — CAMINHO MAIS EFICIENTE PARA VIRALIZAÇÃO\n")

        # Informa número de rodadas por cenário.
        log.write(f"Rodadas por cenário: {RODADAS}\n")

        # Informa o modelo comparado.
        log.write("Modelo: Grafo não-direcionado | Baseline(peso=1) vs Fricção(peso calculado)\n\n")

        # Executa benchmark do Caso 1 e escreve no log.
        benchmark_caso(
            "CASO 1 — Mesma Comunidade",
            grafo_saltos, grafo_friccao,
            origem1, destino1, log
        )

        # Executa benchmark do Caso 2 e escreve no log.
        benchmark_caso(
            "CASO 2 — Comunidades Diferentes",
            grafo_saltos, grafo_friccao,
            origem2, destino2, log
        )

    # Feedback final no console indicando onde o log foi salvo.
    print(f"Benchmark finalizado. Log salvo em: {LOG_FILE}")


# Padrão Python para execução direta do script.
if __name__ == "__main__":
    # Dispara a execução do benchmark.
    main()