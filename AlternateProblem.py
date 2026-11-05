from pathlib import Path
from collections import deque


def read_graph_alternating(path):
    """Return (graph, s, t, red) where graph[u] = {v: capacity}."""
    lines = [l.strip() for l in Path(path).read_text().splitlines() if l.strip()]
    n, m, r = map(int, lines[0].split())
    s, t = lines[1].split()

    graph, red = {}, set()
    for line in lines[2:2 + n]:
        parts = line.split()
        graph[parts[0]] = {}
        if len(parts) > 1 and parts[1] == "*":
            red.add(parts[0])

    for line in lines[2 + n:2 + n + m]:
        if " -> " in line:
            u, v = (x.strip() for x in line.split(" -> "))
            if (u in red) ^ (v in red):
                graph[u][v] = 1
        else:
            u, v = (x.strip() for x in line.split(" -- "))
            if (u in red) ^ (v in red):
                graph[u][v] = 1
                graph[v][u] = 1

    return graph, s, t, red


def bfs_alternating(res_graph, source, sink):
    visited = {source}
    reachable = deque([source])

    while reachable:
        u = reachable.popleft()

        for v, _ in res_graph[u].items():
            if v not in visited:
                visited.add(v)

                if v == sink: #finishing case
                    return True

                reachable.append(v)
    return False
