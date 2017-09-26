from src.directed_graph import Vertex, DirectedGraph


def test_add_vertex():
    g = DirectedGraph()
    v0 = g.add_vertex(vertex_props=None)
    assert v0.id >= 0


def test_get_vertex():
    g = DirectedGraph()
    g.add_vertex(vertex_props=None)
    v = g.get_vertex(vertex_id=0)
    assert v is not None


def test_get_vertex_ids():
    g = DirectedGraph()
    v0 = g.add_vertex(vertex_props=None)
    v1 = g.add_vertex(vertex_props=None)

    list_ids = g.get_vertex_ids()
    assert len(list_ids) == 2
    assert v0.id in list_ids
    assert v1.id in list_ids


def test_get_vertices():
    g = DirectedGraph()
    v0 = g.add_vertex(vertex_props=None)
    v1 = g.add_vertex(vertex_props=None)

    list_vertices = g.get_vertices()
    assert len(list_vertices) == 2
    assert v0 in list_vertices
    assert v1 in list_vertices


def test_add_edge():
    g = DirectedGraph()
    v0 = g.add_vertex(vertex_props=None)
    v1 = g.add_vertex(vertex_props=None)

    g.add_edge(from_id=v0.id, to_id=v1.id)
    v0_neighbours = v0.get_neighbours()
    # only one neighbour
    assert len(v0_neighbours) == 1
    # neighbour has id = 1
    assert v0_neighbours[0].id == 1

    v1_neighbours = v1.get_neighbours()
    # no neighbour of v1 as it is directed graph
    assert len(v1_neighbours) == 0


def test_find_vertex():
    g = DirectedGraph()
    v0 = g.add_vertex(vertex_props={'license': 'L0', 'type': 'P'})
    v1 = g.add_vertex(vertex_props={'license': 'L1', 'type': 'WP'})

    v = g.find_vertex(prop_name='license', prop_value='L1')
    assert v != v0
    assert v == v1

    v = g.find_vertex(prop_name='license', prop_value='L2')
    assert v is None


def test_find_common_reachable_vertex():
    g = DirectedGraph()
    v0 = g.add_vertex(vertex_props={'license': 'L0', 'type': 'P'})
    v1 = g.add_vertex(vertex_props={'license': 'L1', 'type': 'WP'})

    g.add_edge(from_id=v0.id, to_id=v1.id)

    list_vertices = DirectedGraph.find_common_reachable_vertices(input_vertices=None)
    assert list_vertices is None

    list_vertices = DirectedGraph.find_common_reachable_vertices(input_vertices=[])
    assert list_vertices is None

    list_vertices = DirectedGraph.find_common_reachable_vertices(input_vertices=[v0])
    assert list_vertices is not None
    assert len(list_vertices) == 2
    assert list_vertices[0] == v0
    assert list_vertices[1] == v1

    list_vertices = DirectedGraph.find_common_reachable_vertices(input_vertices=[v0, v1])
    assert list_vertices is not None
    assert len(list_vertices) == 1
    assert list_vertices[0] == v1

    v2 = g.add_vertex(vertex_props={'license': 'L2', 'type': 'SP'})
    g.add_edge(from_id=v2.id, to_id=v1.id)
    list_vertices = DirectedGraph.find_common_reachable_vertices(input_vertices=[v0, v2])
    assert list_vertices is not None
    assert len(list_vertices) == 1
    assert list_vertices[0] == v1
