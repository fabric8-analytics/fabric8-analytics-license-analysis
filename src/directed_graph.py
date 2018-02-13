"""Implementation of directed graph and vertex classes."""


class Vertex(object):
    """Class representing vertex in a directed graph."""

    def __init__(self, vertex_id, dict_props):
        """Initialize the Vertex object with no neighbours."""
        self.id = vertex_id
        self.props = dict_props
        self.neighbours = dict()

    def __str__(self):
        """Generate textual representation of the Vertex object."""
        neighbour_ids = [x.id for x in self.neighbours]
        str_vertex = \
            """
            Vertex: {}
            Neighbours: {}
            Properties: {}
            """.format(self.id, neighbour_ids, self.props)
        return str_vertex

    def add_neighbor(self, vertex, weight=0):
        """Add a neighbours node to the current vertex."""
        self.neighbours[vertex] = weight

    def get_neighbours(self):
        """Get all neighbours vertices."""
        return list(self.neighbours.keys())

    def get_id(self):
        """Get id of the current vertex."""
        return self.id

    def get_weight(self, neighbor):
        """Get weight of given neighbor vertex."""
        return self.neighbours[neighbor]

    def get_prop_value(self, prop_name):
        """Get value of given property."""
        return self.props[prop_name]

    def set_prop_value(self, prop_name, prop_value):
        """Set the property."""
        self.props[prop_name] = prop_value

    def get_reachable_vertices(self):
        """Retrieve all reachable vertices."""
        list_reachable_vertices = self.get_neighbours()
        for vertex in list_reachable_vertices:
            temp_list = vertex.get_neighbours()
            for temp_vertex in temp_list:
                if temp_vertex not in list_reachable_vertices:
                    list_reachable_vertices.append(temp_vertex)
        return [self] + list_reachable_vertices


class DirectedGraph(object):
    """An implementation of directed graph."""

    def __init__(self):
        """Construct empty directed graph."""
        self.vertex_dict = dict()
        self.num_vertices = 0

    def __iter__(self):
        """Return iterator for all vertices."""
        return iter(list(self.vertex_dict.values()))

    def add_vertex(self, vertex_props):
        """Add a new vertex into directed graph."""
        v = Vertex(vertex_id=self.num_vertices, dict_props=vertex_props)
        self.num_vertices = self.num_vertices + 1
        self.vertex_dict[v.id] = v
        return v

    def get_vertex(self, vertex_id):
        """Retrieve the vertex with given ID from graph."""
        if vertex_id in self.vertex_dict:
            return self.vertex_dict[vertex_id]
        else:
            return None

    def add_edge(self, from_id, to_id, cost=0):
        """Add an edget between two vertices."""
        assert(from_id in self.vertex_dict)
        assert(to_id in self.vertex_dict)
        self.vertex_dict[from_id].add_neighbor(self.vertex_dict[to_id], cost)

    def get_vertex_ids(self):
        """Return IDs of all vertices."""
        return list(self.vertex_dict.keys())

    def get_vertices(self):
        """Return list with all vertices."""
        return list(self.vertex_dict.values())

    def find_vertex(self, prop_name, prop_value):
        """Find the first vertex that have a selected property set to given value."""
        for vertex in self.get_vertices():
            if vertex.get_prop_value(prop_name) == prop_value:
                return vertex
        return None

    @staticmethod
    def find_common_reachable_vertices(input_vertices):
        """Find all common vertices that are reachable from the given list of input vertices."""
        if input_vertices is None:
            return None
        if len(input_vertices) == 0:
            return None

        list_reachable_vertices = None
        for vertex in input_vertices:
            cur_reachable_vertices = vertex.get_reachable_vertices()
            cur_reachable_vertex_ids = [x.id for x in cur_reachable_vertices]
            if list_reachable_vertices is None:  # initialize
                list_reachable_vertices = cur_reachable_vertices
            else:  # keep on doing intersection
                list_reachable_vertices = [
                    reachable_vertex
                    for reachable_vertex in list_reachable_vertices
                    if reachable_vertex.id in cur_reachable_vertex_ids
                ]

        return list_reachable_vertices

    @staticmethod
    def read_from_json(data_store):
        """Construct directed graph using data read from JSON file."""
        list_vertex_files = data_store.list_files()

        g = DirectedGraph()
        file2vertex = {}
        file2id = {}
        # let us first read all vertices
        for vertex_file in list_vertex_files:
            v = data_store.read_json_file(vertex_file)
            file2vertex[vertex_file] = v

        # add vertex and store corresponding id
        for k, v in file2vertex.items():
            v_id = g.add_vertex(vertex_props=v)
            file2id[k] = v_id

        # add edge by using 'neighbours' property of a vertex
        for k, v in file2vertex.items():
            from_vertex = file2id[k]
            for n in v['neighbours']:
                # Note: each neighbour property points to a vertex file
                to_vertex = file2id[n + '.json']
                g.add_edge(from_id=from_vertex.id, to_id=to_vertex.id)

        return g
