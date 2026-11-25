"""Animate Some on several small graphs. Run: python SomeViz.py (or %run SomeViz.py)."""

import argparse
from itertools import groupby
import json
from math import cos, pi, sin
from pathlib import Path
import sys
import webbrowser

import networkx as nx
from networkx.algorithms.connectivity import build_auxiliary_node_connectivity
from networkx.algorithms.flow import edmonds_karp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from SomeProblem import read_graph_some, some_function


EXAMPLES = {
    'wall-p-2.txt': 'Flow with rerouting',
    'G-ex.txt': 'Shortest path succeeds',
    'P3.txt': 'Three-vertex path',
    'wall-p-1.txt': 'Flow without rerouting',
    'wall-n-2.txt': 'No valid path through red',
    'grid-5-0.txt': 'Grid graph',
    'increase-n8-3.txt': 'DAG reachability shortcut',
}


def layout(filename, nodes):
    wall = {'0': [100, 360], '1': [100, 240], '2': [260, 240],
            '3': [420, 240], '4': [540, 240], '5': [660, 240],
            '6': [660, 360], '7': [380, 360], '8': [420, 160],
            '9': [420, 80], '10': [300, 80], '11': [180, 80],
            '12': [100, 80], '13': [100, 160]}
    if filename.startswith('wall-p'):
        positions = {u: wall[u] for u in nodes}
    elif filename == 'wall-n-2.txt':
        positions = dict(zip(map(str, range(16)), [
            [100, 360], [100, 280], [200, 280], [300, 280],
            [400, 280], [500, 280], [500, 360], [300, 360],
            [300, 180], [220, 180], [220, 80], [320, 60],
            [420, 80], [500, 120], [500, 180], [400, 180],
        ]))
    elif filename == 'G-ex.txt':
        positions = dict(zip(map(str, range(8)), [
            [100, 360], [260, 360], [420, 360], [660, 360],
            [380, 240], [200, 100], [420, 100], [600, 100],
        ]))
    elif filename.startswith('grid'):
        positions = {u: [100 + 140 * int(u.split('_')[0]),
                         100 + 80 * int(u.split('_')[1])] for u in nodes}
    elif filename == 'P3.txt':
        positions = {'1': [180, 240], '2': [380, 240], '3': [580, 240]}
    else:
        positions = {u: [round(380 + 270 * cos(-pi / 2 + 2 * pi * i / len(nodes)), 2),
                         round(260 + 170 * sin(-pi / 2 + 2 * pi * i / len(nodes)), 2)]
                     for i, u in enumerate(nodes)}
    positions['T'] = [240, 490]
    return positions


def trace_flow(G, node, s, t, frame):
    """Record actual NetworkX augmentations, including reverse-arc cancellations."""
    target = 'T'
    frame('Flow', 'Add a temporary target T',
          f'T connects only to s = {s} and t = {t}. Two internally disjoint {node} → T paths must arrive through different endpoints.',
          target=True, candidate=node)
    H = build_auxiliary_node_connectivity(G)
    mapping = H.graph['mapping']
    source, sink = f'{mapping[node]}B', f'{mapping[target]}A'
    first = edmonds_karp(H, source, sink, cutoff=1)
    second = edmonds_karp(H, source, sink, cutoff=2)

    used = nx.DiGraph((u, v) for u, v, data in first.edges(data=True) if data['flow'] > 0)
    auxiliary_path = nx.shortest_path(used, source, sink)
    first_path = [name for name, _ in groupby(H.nodes[u]['id'] for u in auxiliary_path)]
    flow = set()
    for u, v in zip(first_path, first_path[1:]):
        flow.add((u, v))
        frame('Flow', f'First flow: {u} → {v}',
              'Build the first path from red to T. Each internal vertex has capacity 1.',
              target=True, flow=sorted(flow), walk=[u, v], candidate=node)
    frame('Flow', 'One branch found; search for a second',
          f'The first branch enters T through {first_path[-2]}. The second must use the other endpoint.',
          target=True, flow=sorted(flow), candidate=node, value=1)

    if second.graph['flow_value'] < 2:
        frame('Flow', f'No disjoint pair through red vertex {node}',
              'The maximum flow is only 1. Two branches would have to share an internal vertex; this red candidate cannot work.',
              target=True, flow=sorted(flow), candidate=node, value=1)
        return None

    changes = nx.DiGraph((u, v) for u, v, data in second.edges(data=True)
                         if data['flow'] > first[u][v]['flow'])
    augmentation = nx.shortest_path(changes, source, sink)
    for a, b in zip(augmentation, augmentation[1:]):
        u, v = H.nodes[a]['id'], H.nodes[b]['id']
        if u == v:
            continue
        cancel = not H.has_edge(a, b)
        if cancel:
            flow.remove((v, u))
            title = f'Undo {v} → {u} using reverse arc {u} → {v}'
            detail = 'Cancel part of the first path so both branches can be rerouted. The first path is allowed to move.'
        else:
            flow.add((u, v))
            title = f'Second augmentation: {u} → {v}'
            detail = 'Trace the next residual-network edge. Commit the augmentation when it reaches T.'
        frame('Flow', title, detail, target=True, flow=sorted(flow),
              walk=[u, v], cancel=cancel, candidate=node, value=1)

    paths = list(nx.node_disjoint_paths(G, node, target, flow_func=edmonds_karp, cutoff=2))
    left = next(p[:-1] for p in paths if p[-2] == s)
    right = next(p[:-1] for p in paths if p[-2] == t)
    frame('Flow', 'Two internally disjoint branches found',
          f'One reaches s = {s}; the other reaches t = {t}. They share only red vertex {node} after T is removed.',
          target=True, left=list(zip(left, left[1:])) + [(s, target)],
          right=list(zip(right, right[1:])) + [(t, target)], candidate=node, value=2)
    frame('Result', 'Remove T and reverse the branch toward s',
          'Reversing the first branch is valid because this graph is undirected. Join the two branches at red.',
          left=list(zip(left[::-1], left[-2::-1])), right=list(zip(right, right[1:])), candidate=node)
    return left[::-1], right


def make_trace(filename):
    folder = Path(__file__).resolve().parent
    graph, s, t, red, *_ = read_graph_some(folder.parent / 'forked_data' / filename)
    D = nx.DiGraph()
    D.add_nodes_from(graph)
    D.add_edges_from((u, v) for u in graph for v in graph[u])
    undirected = all(u in graph[v] for u in graph for v in graph[u])
    dag = not undirected and nx.is_directed_acyclic_graph(D)
    if not undirected and not dag:
        raise ValueError('The directed Some animation requires a DAG.')
    G = D.to_undirected() if undirected else D
    edges, frames, solution = list(G.edges()), [], None

    def frame(phase, title, detail, **state):
        frames.append(dict(phase=phase, title=title, detail=detail, **state))

    def finish(left, right):
        path = left + right[1:]
        assert len(path) == len(set(path)) and set(path) & red
        assert all(v in graph[u] for u, v in zip(path, path[1:]))
        frame('Result', 'A valid simple path through red', ' → '.join(path),
              left=list(zip(left, left[1:])), right=list(zip(right, right[1:])),
              candidate=left[-1], outcome='success')
        return path

    frame('Input', 'Find a simple path through red',
          f'Find s = {s} → t = {t}, visiting at least one red vertex without repeating any vertex.')
    try:
        shortest = nx.shortest_path(D, s, t)
    except nx.NetworkXNoPath:
        frame('Result', 'No s → t path exists', 'Even without the red constraint, t is unreachable from s.', outcome='failure')
    else:
        active = []
        for u, v in zip(shortest, shortest[1:]):
            active.append((u, v))
            frame('Shortest path', f'Check shortest path: {u} → {v}',
                  'First inspect an ordinary shortest path. If it already visits red, return it immediately.',
                  active=list(active), walk=[u, v])
        for i, node in enumerate(shortest):
            if node in red:
                solution = finish(shortest[:i + 1], shortest[i:])
                break
        if solution is None and s != t:
            reachable = nx.descendants(D, s) | {s}
            can_reach_t = nx.ancestors(D, t) | {t}
            candidates = red & reachable & can_reach_t
            frame('Red candidate', 'The shortest path misses red',
                  'Eligible red vertices: ' + (', '.join(sorted(candidates)) or 'none') + '. Each must be reachable from s and able to reach t.',
                  active=list(zip(shortest, shortest[1:])))
            if dag:
                frame('DAG reachability', 'This directed graph has no cycles',
                      'Two branches meeting again would create a directed cycle. Reachability is therefore sufficient here.')
                frame('DAG reachability', f'Find vertices reachable from s = {s}',
                      'Reachable vertices: ' + ', '.join(sorted(reachable)) + '.',
                      active=list(nx.bfs_edges(D, s)))
                frame('DAG reachability', f'Find vertices that can reach t = {t}',
                      'Search from t using reversed edges. Eligible red vertices lie in both reachability sets: ' + (', '.join(sorted(candidates)) or 'none') + '.',
                      active=[(v, u) for u, v in nx.bfs_edges(D.reverse(copy=False), t)])
            if undirected:
                G.add_edges_from([(s, 'T'), (t, 'T')])
                edges = list(G.edges())
            for node in candidates:
                frame('Red candidate', f'Try red vertex {node}',
                      'Find two disjoint branches.' if undirected else
                      'This red vertex lies in both reachability sets; its branches cannot overlap in a DAG.',
                      candidate=node)
                if undirected:
                    pair = trace_flow(G, node, s, t, frame)
                    if pair:
                        solution = finish(*pair)
                        break
                else:
                    left = nx.shortest_path(D, s, node)
                    right = nx.shortest_path(D, node, t)
                    frame('DAG reachability', 'Recover the two branches',
                          'Join s → red and red → t. A repeated vertex would imply a directed cycle, so this path is simple.',
                          left=list(zip(left, left[1:])), right=list(zip(right, right[1:])), candidate=node)
                    solution = finish(left, right)
                    break
        if solution is None:
            frame('Result', 'No simple path through red exists',
                  'All eligible red candidates were exhausted. Reaching red and then t would require repeating a vertex.', outcome='failure')

    assert bool(solution) == bool(some_function('undirected' if undirected else 'directed', graph, s, t, red))
    note = ('Flow steps come from NetworkX’s Edmonds–Karp search. Vertex splitting is internal; the drawing keeps the original vertices.'
            if undirected else 'All directed dataset inputs are DAGs. Two reachability searches suffice: a red vertex in both sets gives a simple path because the graph has no directed cycles.')
    return dict(file=filename, description=EXAMPLES[filename], s=s, t=t, red=sorted(red),
                directed=not undirected, dag=dag, vertices=len(graph), edge_count=D.number_of_edges() // 2 if undirected else D.number_of_edges(),
                positions=layout(filename, list(graph)), edges=edges, frames=frames, note=note,
                solution=solution)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-open', action='store_true', help='Update the animation without opening a browser.')
    args = parser.parse_args()
    page = Path(__file__).with_suffix('.html')
    marker = '<script id="trace" type="application/json">'
    before, rest = page.read_text().split(marker, 1)
    _, after = rest.split('</script>', 1)
    traces = [make_trace(filename) for filename in EXAMPLES]
    page.write_text(before + marker + json.dumps(dict(graphs=traces)) + '</script>' + after)
    print(f'{len(traces)} graphs, {sum(len(trace["frames"]) for trace in traces)} animation steps: {page}')
    if not args.no_open:
        webbrowser.open(page.resolve().as_uri())
