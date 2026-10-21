"""
arcgeo.spatial_index - High-Performance 2D QuadTree Spatial Index
Implements spatial partitioning for O(log N) bounding-box queries, matching
the spatial indexing mechanisms used in ESRI File Geodatabases and Shapefiles.
"""

from typing import List, Tuple, Any, Optional
from arcgeo.geometry import Envelope, Geometry


class QuadTreeNode:
    def __init__(self, bounds: Envelope, capacity: int = 8, depth: int = 0, max_depth: int = 12):
        self.bounds = bounds
        self.capacity = capacity
        self.depth = depth
        self.max_depth = max_depth
        self.items: List[Tuple[Envelope, Any]] = []
        self.divided = False
        self.nw: Optional['QuadTreeNode'] = None
        self.ne: Optional['QuadTreeNode'] = None
        self.sw: Optional['QuadTreeNode'] = None
        self.se: Optional['QuadTreeNode'] = None

    def subdivide(self):
        cx, cy = self.bounds.center
        b = self.bounds
        self.nw = QuadTreeNode(Envelope(b.xmin, cy, cx, b.ymax), self.capacity, self.depth + 1, self.max_depth)
        self.ne = QuadTreeNode(Envelope(cx, cy, b.xmax, b.ymax), self.capacity, self.depth + 1, self.max_depth)
        self.sw = QuadTreeNode(Envelope(b.xmin, b.ymin, cx, cy), self.capacity, self.depth + 1, self.max_depth)
        self.se = QuadTreeNode(Envelope(cx, b.ymin, b.xmax, cy), self.capacity, self.depth + 1, self.max_depth)
        self.divided = True

        # Re-distribute existing items to children when possible
        unmoved = []
        for env, item in self.items:
            inserted = False
            for child in (self.nw, self.ne, self.sw, self.se):
                if child.bounds.contains_point(env.xmin, env.ymin) and child.bounds.contains_point(env.xmax, env.ymax):
                    child.insert(env, item)
                    inserted = True
                    break
            if not inserted:
                unmoved.append((env, item))
        self.items = unmoved

    def insert(self, env: Envelope, item: Any) -> bool:
        if not self.bounds.intersects(env):
            return False

        if not self.divided:
            if len(self.items) < self.capacity or self.depth >= self.max_depth:
                self.items.append((env, item))
                return True
            self.subdivide()

        # Try to insert into child nodes
        for child in (self.nw, self.ne, self.sw, self.se):
            if child.bounds.contains_point(env.xmin, env.ymin) and child.bounds.contains_point(env.xmax, env.ymax):
                return child.insert(env, item)

        # Spans across children boundaries, keep at this parent node
        self.items.append((env, item))
        return True

    def query(self, search_env: Envelope, results: List[Any]):
        if not self.bounds.intersects(search_env):
            return

        for env, item in self.items:
            if env.intersects(search_env):
                results.append(item)

        if self.divided:
            self.nw.query(search_env, results)
            self.ne.query(search_env, results)
            self.sw.query(search_env, results)
            self.se.query(search_env, results)


class SpatialIndex:
    """Public QuadTree Spatial Index interface."""
    def __init__(self, initial_bounds: Optional[Envelope] = None, capacity: int = 16):
        self.bounds = initial_bounds or Envelope(-180.0, -90.0, 180.0, 90.0)
        self.root = QuadTreeNode(self.bounds, capacity=capacity)
        self.total_count = 0

    def insert(self, geom: Geometry, item: Any):
        env = geom.get_envelope()
        # Auto-expand bounds if needed
        if not self.bounds.contains_point(env.xmin, env.ymin) or not self.bounds.contains_point(env.xmax, env.ymax):
            self.bounds = self.bounds.union(env)
            # Rebuild tree with expanded bounds
            new_root = QuadTreeNode(self.bounds, capacity=self.root.capacity)
            existing: List[Any] = []
            self.root.query(self.bounds, existing)
            for old_env, old_item in self._get_all_entries(self.root):
                new_root.insert(old_env, old_item)
            self.root = new_root

        self.root.insert(env, item)
        self.total_count += 1

    def _get_all_entries(self, node: QuadTreeNode) -> List[Tuple[Envelope, Any]]:
        entries = list(node.items)
        if node.divided:
            for child in (node.nw, node.ne, node.sw, node.se):
                entries.extend(self._get_all_entries(child))
        return entries

    def query_envelope(self, search_env: Envelope) -> List[Any]:
        """Finds all items whose bounding box intersects search_env in O(log N) time."""
        results: List[Any] = []
        self.root.query(search_env, results)
        return results

    def __len__(self) -> int:
        return self.total_count

    def __repr__(self) -> str:
        return f"SpatialIndex(items={self.total_count}, bounds={self.bounds})"
