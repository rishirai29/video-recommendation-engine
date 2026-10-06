"""Graph model of who watched what, plus BFS and DFS traversal for related videos.

The graph is bipartite: user nodes ("u:alice") are only connected to video nodes
("v:video_1") and the other way round. Two videos are "related" when they are
connected through users who watched both.
"""
import json
from collections import defaultdict, deque


class WatchGraph:
    def __init__(self):
        self.adj = defaultdict(set)  # node -> set of neighbour nodes

    def add_watch(self, user_id, video_id):
        u, v = f"u:{user_id}", f"v:{video_id}"
        self.adj[u].add(v)
        self.adj[v].add(u)

    def has_video(self, video_id):
        return f"v:{video_id}" in self.adj

    def popularity(self, video_id):
        """How many users watched this video."""
        return len(self.adj[f"v:{video_id}"])

    def recommend_bfs(self, video_id, limit=5, max_depth=4):
        """Breadth-first search: explore the graph layer by layer.

        Layer 1 = users who watched the start video.
        Layer 2 = other videos those users watched (closest relatives).
        Layer 3 = other users who watched those videos, layer 4 = their videos, ...
        A video's score = number of shortest paths reaching it, divided by how many
        video-hops away it is, so videos co-watched by many of the same users win.
        """
        start = f"v:{video_id}"
        if start not in self.adj:
            return []
        dist = {start: 0}
        paths = defaultdict(int)
        queue = deque([start])
        while queue:
            node = queue.popleft()
            depth = dist[node]
            if depth >= max_depth:
                continue
            for nb in self.adj[node]:
                if nb not in dist:
                    dist[nb] = depth + 1
                    queue.append(nb)
                if dist[nb] == depth + 1:
                    paths[nb] += 1
        scored = []
        for node, count in paths.items():
            if node.startswith("v:") and node != start:
                scored.append((node[2:], count / (dist[node] / 2)))
        scored.sort(key=lambda item: (-item[1], item[0]))
        return [(vid, round(score, 3)) for vid, score in scored[:limit]]

    def recommend_dfs(self, video_id, limit=5, max_depth=6):
        """Depth-first search: follow one chain of viewing behaviour as deep as it goes.

        This reaches videos further from the start video than BFS does, so it is useful
        for discovery. Videos found along the way are ranked by how many users watched
        them (popularity), with the video id as a tie-breaker so results are stable.
        """
        start = f"v:{video_id}"
        if start not in self.adj:
            return []
        visited = {start}
        stack = [(start, 0)]
        found = []
        while stack:
            node, depth = stack.pop()
            if node.startswith("v:") and node != start:
                found.append(node[2:])
            if depth >= max_depth:
                continue
            for nb in sorted(self.adj[node], reverse=True):
                if nb not in visited:
                    visited.add(nb)
                    stack.append((nb, depth + 1))
        found.sort(key=lambda vid: (-self.popularity(vid), vid))
        return [(vid, float(self.popularity(vid))) for vid in found[:limit]]


def load_graph(path):
    graph = WatchGraph()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for user_id, video_id in data["watches"]:
        graph.add_watch(user_id, video_id)
    return graph
