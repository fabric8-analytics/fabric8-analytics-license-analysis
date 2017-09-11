
class Vertex(object):
    def __init__(self, vertex_id, dict_props):
        self.id = vertex_id
        self.props = dict_props
        self.neighbours = dict()

    def __str__(self):
        neighbour_ids = [x.id for x in self.neighbours]
        str_vertex = \
        """
        Vertex: {}
        Neighbours: {}
        Properties: {}
        """.format(self.id, neighbour_ids, self.props)
        return str_vertex

    def add_neighbor(self, vertex, weight=0):
        self.neighbours[vertex] = weight

    def get_neighbours(self):
        return list(self.neighbours.keys())

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.neighbours[neighbor]

    def get_prop_value(self, prop_name):
        return self.props[prop_name]

    def set_prop_value(self, prop_name, prop_value):
        self.props[prop_name] = prop_value

    def get_reachable_vertices(self):
        list_reachable_vertices = self.get_neighbours()
        for vertex in list_reachable_vertices:
            temp_list = vertex.get_neighbours()
            for temp_vertex in temp_list:
                if temp_vertex not in list_reachable_vertices:
                    list_reachable_vertices.append(temp_vertex)
        return [self] + list_reachable_vertices


class DirectedGraph(object):
    def __init__(self):
        self.vertex_dict = dict()
        self.num_vertices = 0

    def __iter__(self):
        return iter(list(self.vertex_dict.values()))

    def add_vertex(self, vertex_props):
        v = Vertex(vertex_id=self.num_vertices, dict_props=vertex_props)
        self.num_vertices = self.num_vertices + 1
        self.vertex_dict[v.id] = v
        return v

    def get_vertex(self, vertex_id):
        if vertex_id in self.vertex_dict:
            return self.vertex_dict[vertex_id]
        else:
            return None

    def add_edge(self, from_id, to_id, cost=0):
        assert(from_id in self.vertex_dict)
        assert(to_id in self.vertex_dict)
        self.vertex_dict[from_id].add_neighbor(self.vertex_dict[to_id], cost)

    def get_vertex_ids(self):
        return list(self.vertex_dict.keys())

    def get_vertices(self):
        return list(self.vertex_dict.values())

    def find_vertex(self, prop_name, prop_value):
        for vertex in self.get_vertices():
            if vertex.get_prop_value(prop_name) == prop_value:
                return vertex
        return None

    @staticmethod
    def find_common_reachable_vertices(input_vertices):
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
        list_vertex_files = data_store.list_files()

        g = DirectedGraph()
        file2vertex = {}
        file2id = {}
        # let us first read all vertices
        for vertex_file in list_vertex_files:
            v = data_store.read_json_file(vertex_file)
            file2vertex[vertex_file] = v

        # add vertex and store corresponding id
        for k in file2vertex.keys():
            v = file2vertex[k]
            v_id = g.add_vertex(vertex_props=v)
            file2id[k] = v_id

        # add edge by using 'neighbours' property of a vertex
        for k in file2vertex.keys():
            v = file2vertex[k]
            from_vertex = file2id[k]
            for n in v['neighbours']:
                # Note: each neighbour property points to a vertex file
                to_vertex = file2id[n + '.json']
                g.add_edge(from_id=from_vertex.id, to_id=to_vertex.id)

        return g
