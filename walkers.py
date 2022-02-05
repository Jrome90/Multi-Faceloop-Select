from bmesh.types import BMLoop, BMEdge
"""Adapted from Blender source Bmesh Walker with some modifications"""
def bmesh_face_loop_walker(start_edge, start_loop=None, return_loop=False):

    def rewind(edge):
        first_loop: BMLoop = edge.link_loops[0]

        visited_faces.add(first_loop.face)
        visited_edges.add(first_loop.edge)

        current_face = first_loop.face
        next_loop = first_loop

        while True:
            current_face = next_loop.face
            next_loop = next_loop.link_loop_radial_next
            l = next_loop
            if not include_face(l):
                l = l.link_loop_radial_prev.link_loop_next.link_loop_next
                if not l.edge.is_manifold:
                    l = l.link_loop_prev.link_loop_prev
                l = l.link_loop_radial_next

            if include_face(l):
                visited_faces.add(next_loop.face)
                visited_edges.add(next_loop.edge)
                next_loop = l
            else:
                break
        
        return next_loop.link_loop_radial_next

    def include_face(loop: BMLoop):
        if len(loop.face.verts) != 4:
            return False
        if loop.face in visited_faces and loop.edge in visited_edges:
            return False

        return True

    def can_start_from_edge(edge: BMEdge, start_loop):
        if edge.is_wire:
            return False
        if edge.is_boundary and include_face(start_loop):
            return False
        if not edge.is_manifold:
            return False
        return True

    visited_faces = set()
    visited_edges = set()

    first_loop: BMLoop = start_loop
    if not can_start_from_edge(start_edge, first_loop):
        return


    if start_loop is None:
        first_loop: BMLoop = rewind(start_edge)
        visited_faces.clear()
        visited_edges.clear()

    visited_faces.add(first_loop.face)
    visited_edges.add(first_loop.edge)

    current_face = first_loop.face
    next_loop = first_loop

    while True:

        current_face = next_loop.face
        next_loop = next_loop.link_loop_radial_next
        l = next_loop

        if not include_face(l):
            l = l.link_loop_radial_prev.link_loop_next.link_loop_next
            if not l.edge.is_manifold:
                l = l.link_loop_prev.link_loop_prev
            l = l.link_loop_radial_next

        if include_face(l):
            next_loop = l
            visited_faces.add(next_loop.face)
            visited_edges.add(next_loop.edge)

            if len(current_face.verts) == 4:
                if return_loop:
                    yield (current_face.index, next_loop)
                else:
                    yield current_face.index
        else:
            if len(current_face.verts) == 4:
                if return_loop:
                    yield (current_face.index, next_loop)
                else:
                    yield current_face.index
            yield None
            break