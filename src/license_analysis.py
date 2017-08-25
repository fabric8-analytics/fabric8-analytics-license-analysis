from directed_graph import Vertex, DirectedGraph, DAGExplorer
from src.util import data_store


class LicenseAnalyzer(object):
    def __init__(self, graph_store, synonyms_store):
        # self.g = self._create_graph()
        self.g = DirectedGraph.read_from_json(graph_store)
        self.known_licenses = [
            'public domain',
            'mit',
            'bsd-new',
            'apache 2.0',
            'lgplv2.1',
            'lgplv2.1+',
            'lgplv3+',
            'mpl 1.1',
            'gplv2',
            'gplv2+',
            'gplv3+',
            'affero gplv3'
        ]

        # IMPORTANT: Order matters in the following tuple
        self.license_type_tuple = ('P', 'WP', 'SP', 'NP')

        list_synonym_jsons = synonyms_store.list_files()
        for synonym_json in list_synonym_jsons:
            self.syn = synonyms_store.read_json_file(synonym_json)
            break  # currently only one synonym json is supported

        # compatibility classes
        self.dict_compatibility_classes = {}
        self.dict_type_compatibility_classes = {}

        self._find_compatibility_classes()
        self._find_type_compatibility_classes()

    def find_synonym(self, license_name):
        if license_name in self.known_licenses:
            return license_name

        synonym = self.syn.get(license_name)
        if synonym in self.known_licenses:
            return synonym  # return known synonym
        else:
            return license_name  # return unknown license itself

    @staticmethod
    def _create_graph():
        g = DirectedGraph()
        pd = g.add_vertex(vertex_props={'license': 'public domain', 'type': 'P'})
        mit = g.add_vertex(vertex_props={'license': 'mit', 'type': 'P'})
        bsd = g.add_vertex(vertex_props={'license': 'bsd-new', 'type': 'P'})
        apache = g.add_vertex(vertex_props={'license': 'apache 2.0', 'type': 'P'})
        lgpl2 = g.add_vertex(vertex_props={'license': 'lgplv2.1', 'type': 'WP'})
        lgpl22 = g.add_vertex(vertex_props={'license': 'lgplv2.1+', 'type': 'WP'})
        lgpl3 = g.add_vertex(vertex_props={'license': 'lgplv3+', 'type': 'WP'})
        mpl = g.add_vertex(vertex_props={'license': 'mpl 1.1', 'type': 'WP'})
        gpl2 = g.add_vertex(vertex_props={'license': 'gplv2', 'type': 'SP'})
        gpl22 = g.add_vertex(vertex_props={'license': 'gplv2+', 'type': 'SP'})
        gpl3 = g.add_vertex(vertex_props={'license': 'gplv3+', 'type': 'SP'})
        agpl3 = g.add_vertex(vertex_props={'license': 'agplv3', 'type': 'NP'})

        # g.add_edge('PD', 'MIT')
        g.add_edge(pd.id, mit.id)

        # g.add_edge('MIT', 'BSD')
        g.add_edge(mit.id, bsd.id)

        # g.add_edge('BSD', 'APACHE')
        g.add_edge(bsd.id, apache.id)

        # g.add_edge('BSD', 'MPL 1.1')
        g.add_edge(bsd.id, mpl.id)

        # g.add_edge('BSD', 'LGPL V2.1')
        g.add_edge(bsd.id, lgpl2.id)

        # g.add_edge('BSD', 'LGPL V2.1+')
        g.add_edge(bsd.id, lgpl22.id)

        # g.add_edge('BSD', 'LGPL V3+')
        g.add_edge(bsd.id, lgpl3.id)

        # g.add_edge('APACHE', 'LGPL V3+')
        g.add_edge(apache.id, lgpl3.id)

        # g.add_edge('LGPL V2.1+', 'LGPL V2.1')
        g.add_edge(lgpl22.id, lgpl2.id)

        # g.add_edge('LGPL V2.1+', 'LGPL V3+')
        g.add_edge(lgpl22.id, lgpl3.id)

        # g.add_edge('LGPL V2.1', 'GPL V2')
        g.add_edge(lgpl2.id, gpl2.id)

        # g.add_edge('LGPL V2.1', 'GPL V2+')
        g.add_edge(lgpl2.id, gpl22.id)

        # g.add_edge('LGPL V2.1+', 'GPL V2+')
        g.add_edge(lgpl22.id, gpl22.id)

        # g.add_edge('LGPL V3+', 'GPL V3+')
        g.add_edge(lgpl3.id, gpl3.id)

        # g.add_edge('GPL V2+', 'GPL V2')
        g.add_edge(gpl22.id, gpl2.id)

        # g.add_edge('GPL V2+', 'GPL V3+')
        g.add_edge(gpl22.id, gpl3.id)

        # g.add_edge('GPL V3+', 'AGPL V3+')
        g.add_edge(gpl3.id, agpl3.id)

        return g

    @staticmethod
    def _print_license_vertex(vertex):
        print("Vertex {}: license: {} Type: {}".format(vertex.id,
                                                       vertex.get_prop_value('license'),
                                                       vertex.get_prop_value('type')))
        for n in vertex.get_neighbours():
            print("> Neighbour {}: license: {} Type: {}".format(n.id,
                                                                n.get_prop_value('license'),
                                                                n.get_prop_value('type')))

        print("")

    def print_license_graph(self):
        for lic in self.known_licenses:
            v = self.g.find_vertex(prop_name='license', prop_value=lic)
            self._print_license_vertex(v)

    def _find_walks_within_type(self, v, lic_type, current_walk):
        current_walk.append(v)

        neighbours = v.get_neighbours()
        neighbours = filter(lambda x: x.get_prop_value('type') == lic_type, neighbours)

        if neighbours is None or len(neighbours) == 0:
            lic_walk = map(lambda x: x.get_prop_value('license'), current_walk)
            print(', '.join(lic_walk))

            dict_compatibles = self.dict_type_compatibility_classes.get(lic_type, {})
            list_compatibles = dict_compatibles.get(v, [])
            list_compatibles += lic_walk
            dict_compatibles[v] = list_compatibles
            self.dict_type_compatibility_classes[lic_type] = dict_compatibles
        else:
            for n in neighbours:
                self._find_walks_within_type(n, lic_type, current_walk)

        current_walk.pop()

    def _find_type_compatibility_classes(self):
        # find walks in the license graph and compatibility classes will by a by-product
        # v_pd = self.g.find_vertex('license', 'public domain')
        # v_type = v_pd.get_prop_value('type')
        # self._find_walks_within_type(v_pd, v_type, [])
        for v in self.g.get_vertices():
            lic_type = v.get_prop_value('type')
            self._find_walks_within_type(v, lic_type, [])

        for t in self.dict_type_compatibility_classes.keys():
            dict_compatibles = self.dict_type_compatibility_classes.get(t, {})
            for v in dict_compatibles.keys():
                list_compatibles = dict_compatibles.get(v, [])
                list_compatibles = list(set(list_compatibles))
                dict_compatibles[v] = list_compatibles
                print(v.get_prop_value('license'))
                print(list_compatibles)

    def _find_walks(self, v, current_walk):
        current_walk.append(v)

        neighbours = v.get_neighbours()
        if neighbours is None or len(neighbours) == 0:
            lic_walk = map(lambda x: x.get_prop_value('license'), current_walk)
            print(', '.join(lic_walk))
            list_compatibles = self.dict_compatibility_classes.get(v, [])
            list_compatibles += lic_walk
            self.dict_compatibility_classes[v] = list_compatibles
        else:
            for n in neighbours:
                self._find_walks(n, current_walk)

        current_walk.pop()

    def _find_compatibility_classes(self):
        # find walks in the license graph and compatibility classes will by a by-product
        v_pd = self.g.find_vertex('license', 'public domain')
        self._find_walks(v_pd, [])

        for v in self.dict_compatibility_classes.keys():
            list_compatibles = self.dict_compatibility_classes.get(v, [])
            list_compatibles = list(set(list_compatibles))
            self.dict_compatibility_classes[v] = list_compatibles
            print(v.get_prop_value('license'))
            print(list_compatibles)

    @staticmethod
    def _find_conflict_licenses(license_vertices):
        list_groups = []
        for v in license_vertices:
            vertex_groups = v.get_prop_value('group')
            list_groups += vertex_groups

        list_groups = list(set(list_groups))
        list_items = map(lambda x: (x, []), list_groups)
        map_groups = dict(list_items)

        for v in license_vertices:
            license = v.get_prop_value('license')
            vertex_groups = v.get_prop_value('group')
            if set(vertex_groups) != set(list_groups):
                for g in vertex_groups:
                    map_groups[g].append(license)

        output = []
        for l in map_groups.values():
            output.append(list(set(l)))

        return output

    def compute_representative_license(self, input_licenses):
        output = {
            'status': 'Failure',
            'reason': 'Input is invalid',
            'representative_license': None,
            'unknown_licenses': [],
            'conflict_licenses': []
        }
        if input_licenses is None:
            return output
        if len(input_licenses) == 0:
            return output

        # Find synonyms
        input_lic_synonyms = map(lambda y: self.find_synonym(y), input_licenses)

        # Check if all input licenses are known
        if len(set(input_lic_synonyms) - set(self.known_licenses)) > 0:
            output['status'] = 'Unknown'
            output['reason'] = 'Some unknown licenses found'
            output['unknown_licenses'] = list(set(input_lic_synonyms) - set(self.known_licenses))
            output['representative_license'] = None
            return output

        # Let's try to find a representative license
        # First, we need to find vertices for input licenses
        license_vertices = []
        for lic in input_lic_synonyms:
            v = self.g.find_vertex(prop_name='license', prop_value=lic)
            assert v is not None
            license_vertices.append(v)
        assert len(license_vertices) == len(input_lic_synonyms)

        # Find common reachable vertices from input license vertices
        reachable_vertices = DirectedGraph.find_common_reachable_vertices(license_vertices)
        if len(reachable_vertices) == 0:  # i.e. conflict
            output['status'] = 'Conflict'
            output['reason'] = 'Some licenses are in conflict'
            output['conflict_licenses'] = self._find_conflict_licenses(license_vertices)
            output['representative_license'] = None
            return output

        # Some representative license is possible :)
        # Check if one of the input licenses is the representative one
        common_destination = None
        license_vertex_ids = [x.id for x in license_vertices]
        for v in reachable_vertices:
            if v.id in license_vertex_ids:
                common_destination = v  # TODO: should we break after this ?

        if common_destination is not None:
            output['status'] = 'Successful'
            output['reason'] = 'Representative license found'
            output['representative_license'] = \
                common_destination.get_prop_value(prop_name='license')
            return output

        # If one of the input licenses is NOT the representative one, then
        # let us pick up the least restrictive one
        for license_type in self.license_type_tuple:
            list_common_destinations = [
                x
                for x in reachable_vertices
                if x.get_prop_value(prop_name='type') is license_type
            ]
            if len(list_common_destinations) > 0:
                output['status'] = 'Successful'
                output['reason'] = 'Representative license found'
                output['representative_license'] = \
                    list_common_destinations[0].get_prop_value(prop_name='license')
                return output

        # We should have returned by now ! Returning from here is unexpected !
        output['status'] = 'Failure'
        output['reason'] = 'Something unexpected happened!'
        output['representative_license'] = None
        return output

