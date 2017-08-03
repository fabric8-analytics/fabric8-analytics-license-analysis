from directed_graph import Vertex, DirectedGraph


class LicenseAnalyzer(object):
    def __init__(self):
        self.g = self._create_graph()
        self.known_licenses = [
            'PD',
            'MIT',
            'BSD',
            'APACHE',
            'LGPL V2.1',
            'LGPL V2.1+',
            'LGPL V3+',
            'MPL 1.1',
            'GPL V2',
            'GPL V2+',
            'GPL V3+',
            'AGPL V3+'
        ]

        # IMPORTANT: Order matters in the following tuple
        self.license_type_tuple = ('P', 'WP', 'SP', 'NP')

    @staticmethod
    def _create_graph():
        g = DirectedGraph()
        pd = g.add_vertex(vertex_props={'license': 'PD', 'type': 'P'})
        mit = g.add_vertex(vertex_props={'license': 'MIT', 'type': 'P'})
        bsd = g.add_vertex(vertex_props={'license': 'BSD', 'type': 'P'})
        apache = g.add_vertex(vertex_props={'license': 'APACHE', 'type': 'P'})
        lgpl2 = g.add_vertex(vertex_props={'license': 'LGPL V2.1', 'type': 'WP'})
        lgpl22 = g.add_vertex(vertex_props={'license': 'LGPL V2.1+', 'type': 'WP'})
        lgpl3 = g.add_vertex(vertex_props={'license': 'LGPL V3+', 'type': 'WP'})
        mpl = g.add_vertex(vertex_props={'license': 'MPL 1.1', 'type': 'WP'})
        gpl2 = g.add_vertex(vertex_props={'license': 'GPL V2', 'type': 'SP'})
        gpl22 = g.add_vertex(vertex_props={'license': 'GPL V2+', 'type': 'SP'})
        gpl3 = g.add_vertex(vertex_props={'license': 'GPL V3+', 'type': 'SP'})
        agpl3 = g.add_vertex(vertex_props={'license': 'AGPL V3+', 'type': 'NP'})

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

    def compute_representative_license(self, input_licenses):
        output = {
            'status': 'Failure',
            'reason': 'Input is invalid',
            'representative_license': None
        }
        if input_licenses is None:
            return output
        if len(input_licenses) == 0:
            return output

        # Check if all input licenses are known
        if len(set(input_licenses) - set(self.known_licenses)) > 0:
            output['status'] = 'Unknown'
            output['reason'] = 'Some unknown licenses found'
            output['representative_license'] = None
            return output

        # Let's try to find a representative license
        # First, we need to find vertices for input licenses
        license_vertices = []
        for lic in input_licenses:
            v = self.g.find_vertex(prop_name='license', prop_value=lic)
            assert v is not None
            license_vertices.append(v)
        assert len(license_vertices) == len(input_licenses)

        # Find common reachable vertices from input license vertices
        reachable_vertices = DirectedGraph.find_common_reachable_vertices(license_vertices)
        if len(reachable_vertices) == 0:  # i.e. conflict
            output['status'] = 'Conflict'
            output['reason'] = 'Some licenses are in conflict'
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

