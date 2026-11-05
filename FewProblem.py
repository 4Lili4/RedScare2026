from pathlib import Path
from collections import deque, defaultdict
import heapq


def read_graph_few(path):
    """Return (graph, s, t, red) where graph[u] = {v: capacity}."""

    lines = [l.strip() for l in Path(path).read_text().splitlines()]
    n, m, r = map(int, lines[0].split())
    s, t = lines[1].split()

    graph = defaultdict(dict)
    red = set()

    for line in lines[2  :  2 + n]:
        parts = line.split()
        #graph[parts[0]] = {} #turn into defaultdict!
        if len(parts) > 1:
            red.add(parts[0])

    for line in lines[2 + n  :  2 + n + m]:
        if " -> " in line:
            u, v = (x.strip() for x in line.split(" -> "))
            
            if u in red and v in red:
                graph[u+"in"][v+"out"]=2

            elif v in red:
                graph[u][v+"in"] = 0
                graph[v+"in"][v+"out"] = 1

            elif u in red:
                graph[u+"in"][u+"out"] = 1
                graph[u+"out"][v] = 0

            else:
                graph[u][v] = 0

        else:
            u, v = (x.strip() for x in line.split(" -- "))
            for i in [1,2]:
                if i == 2:
                    b=u
                    u=v
                    v=b
                    
                if u in red and v in red:
                    graph[u+"in"][v+"out"]=2

                elif v in red:
                    graph[u][v+"in"] = 0
                    graph[v+"in"][v+"out"] = 1

                elif u in red:
                    graph[u+"in"][u+"out"] = 1
                    graph[u+"out"][v] = 0

                else:
                    graph[u][v] = 0

    return graph, s, t, red

def dijkstra_few(graph, s, t, red):
    """Return the weight of a lightest s,t-path in graph, or False if t is unreachable."""
    dist = {s: 0}
    done = set()
    heap = [(0, s)]

    if s in red:
        s=s+"out"
    if t in red:
        t=t+"in"

    while heap:
        d, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)

        if u == t:
            weight_of_path = d
            return weight_of_path

        for v, weight in graph.get(u, {}).items():
            new_d = d + weight
            if v not in dist or new_d < dist[v]:
                dist[v] = new_d
                heapq.heappush(heap, (new_d, v))

    return False