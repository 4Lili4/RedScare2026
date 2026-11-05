from pathlib import Path
from collections import deque


def read_graph_none(path):
    """Return (graph, s, t, red) where graph[u] = {v: capacity}.

    Red vertices (except s and t) and their edges are left out of the graph.
    """
    lines = [l.strip() for l in Path(path).read_text().splitlines() if l.strip()]
    n, m, r = map(int, lines[0].split())
    s, t = lines[1].split()

    graph, red = {}, set()
    for line in lines[2:2 + n]:
        parts = line.split()
        if len(parts) > 1 and parts[1] == "*":
            red.add(parts[0])
            if parts[0] not in (s, t):
                continue
        graph[parts[0]] = {}

    for line in lines[2 + n:2 + n + m]:
        if " -> " in line:
            u, v = (x.strip() for x in line.split(" -> "))
            if u in graph and v in graph:
                graph[u][v] = 1
        else:
            u, v = (x.strip() for x in line.split(" -- "))
            if u in graph and v in graph:
                graph[u][v] = 1
                graph[v][u] = 1

    return graph, s, t, red

def bfs_none(res_graph, source='s', sink='t'):
    visited = {source}
    pointer = {source: None}
    reachable = deque([source])

    while reachable:
        u = reachable.popleft()

        for v, capacity in res_graph[u].items():
            if v not in visited:
                visited.add(v)
                pointer[v] = (u, capacity)

                if v == sink: #finishing case
                    path = []
                    vert = sink
                    while pointer[vert] is not None:
                        prev, cap = pointer[vert]
                        path.append((prev, vert, cap))
                        vert = prev
                    return path[::-1]

                reachable.append(v)
    return False
