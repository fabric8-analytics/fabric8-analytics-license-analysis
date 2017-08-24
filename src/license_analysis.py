from directed_graph import Vertex, DirectedGraph
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

    @staticmethod
    def _print_list_vertices(list_vertices):
        str_vertices = ""
        for v in list_vertices:
            str_vertices += v.get_prop_value('license') + ', '

        print(str_vertices)

    def compute_compatibility_classes(self):
        v_pd = self.g.find_vertex('license', 'public domain')
        dfs_path = [v_pd]
        dfs_stack = [v_pd]
        dict_visited = {}
        dict_classes = {}
        list_leaf_vertices = []
        while len(dfs_stack) > 0:
            top = dfs_stack[len(dfs_stack) - 1]
            visited = dict_visited.get(top, False)

            if top.get_prop_value('license') != dfs_path[len(dfs_path)-1].get_prop_value('license'):
                dfs_path.append(top)
            print('------------------------------------------------------------------')
            print('Input stack')
            self._print_list_vertices(dfs_stack)
            print('Input path')
            self._print_list_vertices(dfs_path)

            if not visited:
                dict_visited[top] = True

                # push children, if any
                children = top.get_neighbours()
                if children is None or len(children) == 0:
                    list_leaf_vertices.append(top)

                    list_vertices = dict_classes.get(top, [])
                    dict_classes[top] = list_vertices + dfs_path

                    print("Extending the class")
                    print(top.get_prop_value('license'))
                    self._print_list_vertices(dict_classes[top])

                    dfs_stack.pop()
                    dfs_path.pop()
                else:
                    print('Pushing children...{')
                    for c in children:
                        # if not dict_visited.get(c, False):
                        print(c.get_prop_value('license'))
                        dfs_stack.append(c)
                    print('...}')
            else:
                list_vertices = dict_classes.get(top, [])
                dict_classes[top] = list_vertices + dfs_path

                dfs_stack.pop()
                dfs_path.pop()

            print('Output stack')
            self._print_list_vertices(dfs_stack)
            print('Output path')
            self._print_list_vertices(dfs_path)
            print('------------------------------------------------------------------')

        # make all the lists unique
        list_leaf_vertices = list(set(list_leaf_vertices))
        for v in dict_classes.keys():
            l = list(set(dict_classes[v]))
            dict_classes[v] = l

        # each leaf node represents a compatibility class
        for leaf in list_leaf_vertices:
            list_leaf_compatibles = dict_classes[leaf]
            for v in list_leaf_compatibles:
                if v.get_prop_value('license') != leaf.get_prop_value('license'):
                    list_nonleaf_compatibles = dict_classes[v]




        print('------------------------------------------------------------------')
        print('Classes')
        print('------------------------------------------------------------------')
        for v in dict_classes.keys():
            print(v.get_prop_value('license'))
            l = list(set(dict_classes[v]))
            self._print_list_vertices(l)
            print(' ')


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

