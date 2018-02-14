"""Unit tests for the Vertex class."""

import pytest
from src.directed_graph import Vertex


def test_initial_state():
    """Check the initial state of vertex."""
    v = Vertex(1, {})
    assert v.id == 1
    assert not v.props


def test_get_id():
    """Check the method get_id."""
    v = Vertex(1, {})
    assert v.get_id() == 1
    v = Vertex(42, {})
    assert v.get_id() == 42


def test_add_neigbor():
    """Check the methods add_neighbor and get_neighbours."""
    v = Vertex(1, {})
    assert not v.get_neighbours()

    v2 = Vertex(2, {})
    v.add_neighbor(v2, 100)
    assert v2 in v.get_neighbours()


def test_get_weight():
    """Check the method get_weight."""
    v = Vertex(1, {})

    v2 = Vertex(2, {})
    v.add_neighbor(v2, 100)
    assert v.get_weight(v2) == 100

    # v3 is not in any relatioship with v
    with pytest.raises(Exception):
        v3 = Vertex(3, {})
        assert v.get_weight(v3) == 100


def test_properties():
    """Check methods get_prop_value and set_prop_value."""
    v = Vertex(1, {})

    with pytest.raises(Exception):
        assert v.get_prop_value("something") is None

    v.set_prop_value("name", "value")
    assert v.get_prop_value("name") == "value"

    with pytest.raises(Exception):
        # this statement still should raise an exception
        assert v.get_prop_value("something") is None


def test_string_representation_1():
    """Check special method __str__ for simple vertex."""
    v = Vertex(1, {})
    s = str(v)
    assert s == """
            Vertex: 1
            Neighbours: []
            Properties: {}
            """


def test_string_representation_2():
    """Check special method __str__ for simple vertex."""
    v = Vertex(100, {})
    s = str(v)
    assert s == """
            Vertex: 100
            Neighbours: []
            Properties: {}
            """


def test_string_representation_4():
    """Check special method __str__ for vertices with properies."""
    v = Vertex(1, {})
    v.set_prop_value("name", "value")
    s = str(v)
    assert s == """
            Vertex: 1
            Neighbours: []
            Properties: {'name': 'value'}
            """

    v = Vertex(2, {})
    v.set_prop_value("other", "XXX")
    s = str(v)
    assert s == """
            Vertex: 2
            Neighbours: []
            Properties: {'other': 'XXX'}
            """


def test_string_representation_5():
    """Check special method __str__ for vertices with neighbours."""
    v = Vertex(100, {})
    v2 = Vertex(2, {})
    v.add_neighbor(v2, 200)
    s = str(v)
    assert s == """
            Vertex: 100
            Neighbours: [2]
            Properties: {}
            """

    v3 = Vertex(3, {})
    v.add_neighbor(v3, 300)
    s = str(v)
    assert s == """
            Vertex: 100
            Neighbours: [2, 3]
            Properties: {}
            """ or s == """
            Vertex: 100
            Neighbours: [3, 2]
            Properties: {}
            """
