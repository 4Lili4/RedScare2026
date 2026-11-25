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
            graph[u][v] = 0
        else:
            u, v = (x.strip() for x in line.split(" -- "))
            graph[u][v] = 0
            graph[v][u] = 0

    return graph, s, t, red, n, m


def some_function(graph_type, graph, s, t, red, m=None):
    """Return True if a simple s-t path through a red vertex exists, else False. Directed inputs must be DAGs, which we know from the problem statement that they are.
    Undirected 
    """
    G = nx.DiGraph()
    G.add_nodes_from(graph)
    G.add_edges_from((u, v) for u in graph for v in graph[u])

    #easy checks - if the shortest path from s to t already goes through a red vertex, or if s == t, then we can return early
    try:
        path = nx.shortest_path(G, s, t) #the graph is unweighted, so this is the same as a BFS
    except nx.NetworkXNoPath: #if there is no path from s to t, then we can return early
        return False
    if any(node in red for node in path): #if the shortest path from s to t already goes through a red vertex, then we can return early
        return True
    if s == t: #this shouldn't happen but is worth a check
        return False

    # Red vertices that are reachable from s and can reach t, aka the intersection of red nodes, descendants of s, and ancestors of t.
    #this excludes s and t from the check as if either were red, we would have returned early above. 
    # This also excludes any red vertices that are not reachable from s or cannot reach t, as they cannot be part of a valid path.
    candidates = red & nx.descendants(G, s) & nx.ancestors(G, t)

    if all(u in graph[v] for u in graph for v in graph[u]):  # if all edges exist both ways, the graph is undirected. Otherwise, it is directed.
        # A red vertex works if it has two vertex-disjoint paths, one to s and one to t.
        # Joining s and t to an extra vertex turns that into a 2-path max-flow check.

        G = G.to_undirected()
        target = object()
        G.add_edges_from([(s, target), (t, target)])
        for node in candidates:
            try:
                if len(list(nx.node_disjoint_paths(G, node, target, cutoff=2))) == 2:
                    return True
            except nx.NetworkXNoPath:
                continue
        return False

    if not nx.is_directed_acyclic_graph(G): #If it is directed but not a DAG, we cannot use the Some method, so we raise an error.
        raise ValueError('The directed Some method requires a DAG.')
    
    # In a DAG, s -> red -> t can never revisit a vertex, so any candidate works, which means we can just check if there are any candidates.
    return bool(candidates)
