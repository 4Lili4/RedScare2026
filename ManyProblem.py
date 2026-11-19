from pathlib import Path
from collections import defaultdict


def read_graph_many(path):
    """Return (graph, s, t, red, N) where graph[u] = {v: capacity}."""

    lines = [l.strip() for l in Path(path).read_text().splitlines()]
    n, m, r = map(int, lines[0].split())
    s, t = lines[1].split()

    graph = defaultdict(dict)
    red = set()

    for line in lines[2  :  2 + n]:
        parts = line.split()
        if len(parts) > 1:
            red.add(parts[0])

    for line in lines[2 + n  :  2 + n + m]:
        if " -> " in line:
            u, v = (x.strip() for x in line.split(" -> "))
            
            if v in red:
                graph[u][v] = 1

            else:
                graph[u][v] = 0

        else:
            u, v = (x.strip() for x in line.split(" -- "))
            for i in [1,2]:
                if i == 2:
                    b=u
                    u=v
                    v=b

                if v in red:
                    graph[u][v] = 1
                else:
                    graph[u][v] = 0

    return graph, s, t, red, n, m


def exhaustive_dfs_undirected_many(graph, s, t, red): # K is the number of red vertices
    n = len(graph)
    visited = {s}
    path = [s]
    best_weight = -1
    best_path = None
    K = len(red)

    def dfs(u, weight):
        nonlocal best_weight, best_path
        if u == t:
            if weight > best_weight:
                best_weight = weight
                best_path = path.copy()
            return

        # If we have a path hitting all red vertices, we can stop searching
        if best_weight == K:
            return

        # A little optimisation step, if our current weight + the remining vertices is less than the best weight,
        #  we can stop searching this path
        if weight + (n - len(visited)) <= best_weight:
            return
        
        # Sort the neighbors to prioritise the ones with the highest weight first (red vertices)
        for v, w in sorted(graph[u].items(), key=lambda x: -x[1]):
            if v not in visited:
                visited.add(v)
                path.append(v)

                dfs(v, weight + w)

                path.pop()
                visited.remove(v)

    dfs(s, 0)
    return best_weight

def longest_path_dags_many(graph, s, t, red):
    def topo_sort(u):
        visited.add(u)

        for v in graph.get(u, {}):
            if v not in visited:
                topo_sort(v)

        stack.append(u)

    visited = set()
    stack = []

    topo_sort(s)

    dist = {v: float("-inf") for v in visited}
    dist[s] = 0

    while stack:
        u = stack.pop()

        for v, weight in graph.get(u, {}).items():
            if dist[u] != float("-inf"):
                dist[v] = max(dist[v], dist[u] + weight)

    if dist.get(t, float("-inf")) == float("-inf"):
        return False

    return dist[t] + (1 if s in red else 0)


def longest_path_many(graph_type, graph, s, t, red, m):
    if graph_type == "Directed Acyclic Graph":
        return longest_path_dags_many(graph, s, t, red)
    else:
        if m <= 500:  # Adjust this threshold based on performance
            return exhaustive_dfs_undirected_many(graph, s, t, red)
        else:
            return "?!"
