# CSI115 – 25.2 – Algoritmos e Estruturas de Dados III

## 👤 Discentes
- **Luccas Carneiro**
- **Thiago Ker**
- **Rany Souza**
- **Marco Antonio**

---

## 📄 Descrição Geral
Este projeto implementa e avalia **algoritmos clássicos de caminhos mínimos em grafos**, aplicados à **simulação de propagação de mensagens em redes sociais**, com o objetivo de identificar o **caminho mais eficiente para viralização** entre dois usuários.

A rede social é modelada como um **grafo ponderado**, onde vértices representam usuários e arestas representam relações sociais. Os pesos das arestas expressam o **custo de repasse da informação**, permitindo simular fricção, intensidade de interação ou facilidade de propagação.

O projeto reutiliza integralmente implementações didáticas do algoritmo **Dijkstra** e do mecanismo de **reconstrução de caminho por predecessores**, seguindo os pseudocódigos apresentados em sala, além de módulos de geração de redes sintéticas e coleta de resultados.

---

## 📌 Interpretação do Problema (Rede Social → Grafo → Caminho Mínimo)

### Objetivo
Dado um par de usuários `(A, B)` em uma rede social, determinar:

- O **menor custo total** para uma mensagem sair de `A` e chegar em `B`.
- O **caminho mínimo** (sequência de usuários intermediários) que viabiliza essa propagação.

---

### Como a rede social vira grafo
- Cada usuário é modelado como um vértice `v`.
- Cada relação social é modelada como uma aresta `u -> v`.

---

### Arestas e pesos (custo de repasse)
```
custo(u, v) = 1 + (1 / (1 + interacao(u, v)))
```
Ou, para comparação:
```
custo(u, v) = 1
```

---

## ▶️ Execução
```
python main.py
```
