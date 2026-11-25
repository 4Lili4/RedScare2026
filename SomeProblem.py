from pathlib import Path
import networkx as nx


def read_graph_some(path):
    """Return (graph, s, t, red, n, m) where graph[u] = {v: capacity}."""
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
            graph[u][v] = 1
        else:
            u, v = (x.strip() for x in line.split(" -- "))
            graph[u][v] = 1
            graph[v][u] = 1

    return graph, s, t, red, n, m


def some_function(graph_type, graph, s, t, red, m=None):
    """Find a simple path through red; directed inputs must be DAGs."""
    G = nx.DiGraph()
    G.add_nodes_from(graph)
    G.add_edges_from((u, v) for u in graph for v in graph[u])

    def result(left, right):
        # Keep the notebook's format: a list containing two lists of edge tuples.
        return [(
            [(u, v, graph[u][v]) for u, v in zip(left, left[1:])],
            [(u, v, graph[u][v]) for u, v in zip(right, right[1:])],
        )]

    try:
        path = nx.shortest_path(G, s, t)
    except nx.NetworkXNoPath:
        return []
    for i, node in enumerate(path):
        if node in red:
            return result(path[:i + 1], path[i:])
    if s == t:
        return []

    candidates = red & (nx.descendants(G, s) | {s}) & (nx.ancestors(G, t) | {t})
    if all(u in graph[v] for u in graph for v in graph[u]):
        G = G.to_undirected()
        target = object()
        G.add_edges_from([(s, target), (t, target)])
        for node in candidates:
            try:
                paths = list(nx.node_disjoint_paths(G, node, target, cutoff=2))
            except nx.NetworkXNoPath:
                continue
            if len(paths) == 2:
                left = next(p[:-1] for p in paths if p[-2] == s)
                right = next(p[:-1] for p in paths if p[-2] == t)
                return result(left[::-1], right)
    else:
        if not nx.is_directed_acyclic_graph(G):
            raise ValueError('The directed Some method requires a DAG.')
        # In a DAG, an overlap between the two branches would form a cycle.
        if candidates:
            node = next(iter(candidates))
            return result(nx.shortest_path(G, s, node), nx.shortest_path(G, node, t))
    return []
