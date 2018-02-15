"""Tests for the class DirectedGraph."""

import pytest
from src.directed_graph import Vertex, DirectedGraph


def test_initial_state():
    """Check the initial state of directed graph."""
    g = DirectedGraph()
    assert g.num_vertices == 0


def test_add_vertex():
    """Check that new vertex can be added to directed graph."""
    g = DirectedGraph()
    v0 = g.add_vertex(vertex_props=None)
    assert v0.id >= 0


def test_num_vertices_counter():
    """Check the num_vertices counter."""
    g = DirectedGraph()
    assert g.num_vertices == 0
    g.add_vertex(vertex_props=None)
    assert g.num_vertices == 1
    g.add_vertex(vertex_props=None)
    assert g.num_vertices == 2


def test_get_vertex():
    """Check if vertex can be retrieved from directed graph."""
    g = DirectedGraph()
    g.add_vertex(vertex_props=None)
    v = g.get_vertex(vertex_id=0)
    assert v is not None
    assert v.id == 0


def test_get_nonexistent_vertex():
    """Check if non existent vertex can not be retrieved from directed graph."""
    g = DirectedGraph()
    g.add_vertex(vertex_props=None)
    v = g.get_vertex(vertex_id=42)
    assert v is None


def test_get_vertex_ids_empty_graph():
    """Test whether method DirectedGraph.get_vertex_ids() works correctly for empty graph."""
    g = DirectedGraph()

    list_ids = g.get_vertex_ids()
    assert not list_ids


def test_get_vertex_ids_graph_with_one_vertex():
    """Test whether method DirectedGraph.get_vertex_ids() works correctly for graph with vertex."""
    g = DirectedGraph()
    v0 = g.add_vertex(vertex_props=None)

    list_ids = g.get_vertex_ids()
    assert len(list_ids) == 1
    assert v0.id in list_ids


def test_get_vertex_ids_graph_with_two_vertices():
    """Test whether method DirectedGraph.get_vertex_ids() works correctly."""
    g = DirectedGraph()
    v0 = g.add_vertex(vertex_props=None)
    v1 = g.add_vertex(vertex_props=None)

    list_ids = g.get_vertex_ids()
    assert len(list_ids) == 2
    assert v0.id in list_ids
    assert v1.id in list_ids


def test_get_vertices_empty_graph():
    """Test whether method DirectedGraph.get_vertices() works correctly for empty graph."""
    g = DirectedGraph()

    list_vertices = g.get_vertices()
    assert not list_vertices


def test_get_vertices_graph_with_one_vertex():
    """Test whether method DirectedGraph.get_vertices() works correctly."""
    g = DirectedGraph()
    v0 = g.add_vertex(vertex_props=None)

    list_vertices = g.get_vertices()
    assert len(list_vertices) == 1
    assert v0 in list_vertices


def test_get_vertices_graph_with_two_vertices():
    """Test whether method DirectedGraph.get_vertices() works correctly."""
    g = DirectedGraph()
    v0 = g.add_vertex(vertex_props=None)
    v1 = g.add_vertex(vertex_props=None)

    list_vertices = g.get_vertices()
    assert len(list_vertices) == 2
    assert v0 in list_vertices
    assert v1 in list_vertices


def test_add_edge():
    """Test whether method DirectedGraph.add_edge() works correctly."""
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


def test_add_cycle():
    """Test whether method DirectedGraph.add_edge() works correctly."""
    g = DirectedGraph()
    v0 = g.add_vertex(vertex_props=None)
    v1 = g.add_vertex(vertex_props=None)

    g.add_edge(from_id=v0.id, to_id=v1.id)
    g.add_edge(from_id=v1.id, to_id=v0.id)
    v0_neighbours = v0.get_neighbours()
    # only one neighbour
    assert len(v0_neighbours) == 1
    # neighbour has id = 1
    assert v0_neighbours[0].id == 1

    v1_neighbours = v1.get_neighbours()
    # no neighbour of v1 as it is directed graph
    assert len(v1_neighbours) == 1
    # neighbour has id = 0
    assert v1_neighbours[0].id == 0


def test_add_cycle_to_the_same_vertex():
    """Test whether method DirectedGraph.add_edge() works correctly."""
    g = DirectedGraph()
    v0 = g.add_vertex(vertex_props=None)

    # create edge from and to the same vertex
    g.add_edge(from_id=v0.id, to_id=v0.id)
    v0_neighbours = v0.get_neighbours()
    # only one neighbour
    assert len(v0_neighbours) == 1
    # neighbour has id = 1
    assert v0_neighbours[0].id == 0


def test_add_edge_between_nonexistent_vertices():
    """Test whether method DirectedGraph.add_edge() works correctly."""
    g = DirectedGraph()
    v0 = Vertex(0, {})
    v1 = Vertex(1, {})

    # neither vertex are put into the directed graph, so it is impossible
    # to add an edge to connect them. ATM the exception thrown by the
    # add_edge method is not very specific, it might need to be improved.
    with pytest.raises(Exception):
        g.add_edge(from_id=v0.id, to_id=v1.id)


def test_find_vertex_empty_graph():
    """Test if method DirectedGraph.find_vertex() works correctly for empty graph."""
    g = DirectedGraph()
    v = g.find_vertex(prop_name='license', prop_value='L1')
    assert v is None


def test_find_vertex_graph_with_one_vertex():
    """Test if method DirectedGraph.find_vertex() works correctly."""
    g = DirectedGraph()
    v0 = g.add_vertex(vertex_props={'license': 'L0', 'type': 'P'})

    v = g.find_vertex(prop_name='license', prop_value='L0')
    assert v is not None
    assert v == v0

    v = g.find_vertex(prop_name='license', prop_value='something_else')
    assert v is None

    with pytest.raises(Exception):
        v = g.find_vertex(prop_name='unknown_property', prop_value='L0')


def test_find_vertex():
    """Test if method DirectedGraph.find_vertex() works correctly."""
    g = DirectedGraph()
    v0 = g.add_vertex(vertex_props={'license': 'L0', 'type': 'P'})
    v1 = g.add_vertex(vertex_props={'license': 'L1', 'type': 'WP'})

    v = g.find_vertex(prop_name='license', prop_value='L1')
    assert v != v0
    assert v == v1

    v = g.find_vertex(prop_name='license', prop_value='L2')
    assert v is None


def test_find_common_reachable_vertex_empty_graph():
    """Test if method DirectedGraph.find_common_reachable_vertices() works correctly."""
    list_vertices = DirectedGraph.find_common_reachable_vertices(input_vertices=None)
    assert list_vertices is None

    list_vertices = DirectedGraph.find_common_reachable_vertices(input_vertices=[])
    assert list_vertices is None

    v0 = Vertex(0, {})
    list_vertices = DirectedGraph.find_common_reachable_vertices(input_vertices=[v0])
    assert list_vertices is not None
    assert list_vertices[0] == v0


def test_find_common_reachable_vertex():
    """Test if method DirectedGraph.find_common_reachable_vertices() works correctly."""
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


def test_iterator():
    """Test that the iterator over all vertexes works correctly."""
    g = DirectedGraph()
    items = [item for item in g]
    assert not items

    v0 = g.add_vertex(vertex_props={'license': 'L0', 'type': 'P'})
    items = [item for item in g]
    assert len(items) == 1
    assert items[0] == v0

    v1 = g.add_vertex(vertex_props={'license': 'L1', 'type': 'WP'})
    items = [item for item in g]
    assert len(items) == 2
    assert v0 in items
    assert v1 in items

    v2 = g.add_vertex(vertex_props={})
    items = [item for item in g]
    assert len(items) == 3
    assert v0 in items
    assert v1 in items
    assert v2 in items
