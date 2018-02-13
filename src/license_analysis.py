"""Class that encapsulates license analysis logic."""

from math import ceil

import itertools

from src.directed_graph import DirectedGraph
from src.config import MAJORITY_THRESHOLD


class LicenseAnalyzer(object):
    """Class that encapsulates license analysis logic.

    Mainly it offers the following:
    - identifies representative license for the given set of licenses
    - finds conflicting licenses
    - locates outlier licenses
    - flags unknown licenses
    """

    def __init__(self, graph_store, synonyms_store):
        """Initialize the analyzer and read known synonyms."""
        # load graph from given data store
        self.g = DirectedGraph.read_from_json(graph_store)
        self.known_licenses = [
            'public domain',
            'mit',
            'bsd-new',
            'bsd-simplified',
            'apache 2.0',
            'lgplv2.1',
            'lgplv2.1+',
            'lgplv3+',
            'mpl 1.1',
            'gplv2',
            'gplv2+',
            'gplv3+',
            'affero gplv3',
            'epl 1.0',
            'cddlv1.1+',
            'mpl 2.0',
            'w3c',
            'bouncycastle',
            'cc0v1.0',
            'cc-by-3.0',
            'edl',
            'json',
            'postgresql',
            'apache 1.1',
            'cpl 1.0',
            'cpal 1.0'
        ]

        # IMPORTANT: Order matters in the following tuple
        self.license_type_tuple = ('P', 'WP', 'SP', 'NP')

        # read the json that contains known synonyms
        list_synonym_jsons = synonyms_store.list_files()
        for synonym_json in list_synonym_jsons:
            self.syn = synonyms_store.read_json_file(synonym_json)
            break  # currently only one synonym json is supported

        # identify compatibility classes among the licenses in graph
        self.dict_compatibility_classes = {}
        self.dict_type_compatibility_classes = {}

        self._find_compatibility_classes()
        self._find_type_compatibility_classes()

    def find_synonym(self, license_name):
        """Find synomym for given license name."""
        if license_name in self.known_licenses:
            return license_name

        synonym = self.syn.get(license_name)
        if synonym in self.known_licenses:
            return synonym  # return known synonym
        else:
            return license_name  # return unknown license itself

    # This function is not in use currently
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

        g.add_edge(pd.id, mit.id)
        g.add_edge(mit.id, bsd.id)
        g.add_edge(bsd.id, apache.id)
        g.add_edge(bsd.id, mpl.id)
        g.add_edge(bsd.id, lgpl2.id)
        g.add_edge(bsd.id, lgpl22.id)
        g.add_edge(bsd.id, lgpl3.id)
        g.add_edge(apache.id, lgpl3.id)
        g.add_edge(lgpl22.id, lgpl2.id)
        g.add_edge(lgpl22.id, lgpl3.id)
        g.add_edge(lgpl2.id, gpl2.id)
        g.add_edge(lgpl2.id, gpl22.id)
        g.add_edge(lgpl22.id, gpl22.id)
        g.add_edge(lgpl3.id, gpl3.id)
        g.add_edge(gpl22.id, gpl2.id)
        g.add_edge(gpl22.id, gpl3.id)
        g.add_edge(gpl3.id, agpl3.id)

        return g

    @staticmethod
    def _print_license_vertex(vertex):
        """Print the given license vertex.

        :param vertex: license vertex to be printed
        :return: None
        """
        print("Vertex {}: license: {} Type: {}".format(vertex.id,
                                                       vertex.get_prop_value(
                                                           'license'),
                                                       vertex.get_prop_value('type')))
        for n in vertex.get_neighbours():
            print("> Neighbour {}: license: {} Type: {}".format(n.id,
                                                                n.get_prop_value(
                                                                    'license'),
                                                                n.get_prop_value('type')))

        print("")

    def print_license_graph(self):
        """Print the license graph.

        :return: None
        """
        for lic in self.known_licenses:
            v = self.g.find_vertex(prop_name='license', prop_value=lic)
            self._print_license_vertex(v)

    def _find_walks_within_type(self, v, lic_type, current_walk):
        """Find all possible walks of license vertices within the scope of given license-type.

        These walks will help identify compatibility classes
        for given license-type.

        IMPORTANT: It is assumed that license graph is a DAG i.e. no cycles.

        Please note that this function has a side effect i.e. its output is
        stored in the object variable 'dict_type_compatibility_classes'.

        :param v: root vertex from where walks will start
        :param lic_type: type of license that defines scope for walks
        :param current_walk: book keeping variable
        :return: None
        """
        current_walk.append(v)

        neighbours = v.get_neighbours()
        neighbours = [x for x in neighbours if x.get_prop_value('type') == lic_type]

        if neighbours is None or len(neighbours) == 0:
            lic_walk = [x.get_prop_value('license') for x in current_walk]
            # print(', '.join(lic_walk))

            v_license = v.get_prop_value('license')
            dict_compatibles = self.dict_type_compatibility_classes.get(lic_type, {})
            list_compatibles = dict_compatibles.get(v_license, [])
            list_compatibles += lic_walk
            dict_compatibles[v_license] = list_compatibles
            self.dict_type_compatibility_classes[lic_type] = dict_compatibles
        else:
            for n in neighbours:
                self._find_walks_within_type(n, lic_type, current_walk)
        current_walk.pop()

    def _find_type_compatibility_classes(self):
        """Identify compatibility classes among the license subgraph for each license-type.

        A compatibility class can be defined as a set of mutually compatible
        licenses i.e. there exists a representative license for each pair of
        licenses in a compatibility class.

        A type compatibility class is a compatibility class such that all its
        licenses belong to same license-type and there exists a representative
        license for each pair of licenses in the same license-type.

        Algorithm to find all type compatibility classes is as follows:
          for each license-vertex V:
            enumerate all possible walks starting from V such that
            each vertex in walk has same license-type as V.type

            end-vertex of each walk identifies a compatibility class
            and all the vertices of the walk are members of this class

          for each unique type compatibility class:
            deduplicate the member license-vertices

        At the end of all walk enumeration, the type compatible classes will be
        kept in dict_type_compatible_classes as follows:
          dict_type_compatible_classes:
            license-type:
              class-representative-license: [list of member licenses]
            ...
            license-type:
              class-representative-license: [list of member licenses]

        Note: type compatible classes are useful for identifying license based
        outlier packages.

        :return: None
        """
        for v in self.g.get_vertices():
            lic_type = v.get_prop_value('type')
            self._find_walks_within_type(v, lic_type, [])

        # deduplicate the member licenses of each type compatibility class
        for t in self.dict_type_compatibility_classes.keys():
            dict_compatibles = self.dict_type_compatibility_classes.get(t, {})
            for lic in dict_compatibles.keys():
                list_compatibles = dict_compatibles.get(lic, [])
                list_compatibles = list(set(list_compatibles))
                dict_compatibles[lic] = list_compatibles

    def _find_walks(self, v, current_walk):
        """Find all possible walks of license vertices.

        These walks will help us identify compatibility classes.

        IMPORTANT: It is assumed that license graph is a DAG i.e. no cycles.

        Please note that this function has a side effect i.e. its output is
        stored in the object variable 'dict_compatibility_classes'.

        :param v: root vertex from where walks will start
        :param current_walk: book keeping variable
        :return: None
        """
        current_walk.append(v)
        neighbours = v.get_neighbours()
        if neighbours is None or len(neighbours) == 0:
            lic_walk = [x.get_prop_value('license') for x in current_walk]
            # print(', '.join(lic_walk))
            v_license = v.get_prop_value('license')
            list_compatibles = self.dict_compatibility_classes.get(v_license, [])
            list_compatibles += lic_walk
            self.dict_compatibility_classes[v_license] = list_compatibles
        else:
            for n in neighbours:
                self._find_walks(n, current_walk)

        current_walk.pop()

    def _find_compatibility_classes(self):
        """Identify compatibility classes among the license graph.

        A compatibility class can be defined as a set of mutually compatible
        licenses i.e. there exists a representative license for each pair of
        licenses in a compatibility class.

        Algorithm to find all compatibility classes is as follows:
          enumerate all possible walks starting from 'public domain' vertex

          end-vertex of each walk identifies a compatibility class
          and all the vertices of the walk are members of this class

          for each unique compatibility class:
            deduplicate the member license-vertices

        At the end of all walk enumeration, the compatible classes will be
        kept in dict_compatible_classes as follows:
          dict_compatible_classes:
            class-representative-license: [list of member licenses]
            ...
            class-representative-license: [list of member licenses]

        Note: compatible classes are useful for identifying conflicting licenses

        :return: None
        """
        # find walks in the license graph and compatibility classes will by a
        # by-product
        v_pd = self.g.find_vertex('license', 'public domain')
        self._find_walks(v_pd, [])

        # deduplicate the member licenses of each compatibility class
        for lic in self.dict_compatibility_classes.keys():
            list_compatibles = self.dict_compatibility_classes.get(lic, [])
            list_compatibles = list(set(list_compatibles))
            self.dict_compatibility_classes[lic] = list_compatibles

    def _find_conflict_licenses(self, license_vertices):
        """Identify conflicting licenses among the given list.

        Note that this method assumes that there is a conflict in the input licenses.

        When there is a conflict in the given list of licenses then it is
        guaranteed that all of them cannot be members of the same compatibility class.
        Otherwise, there would have been a representative license identified.

        This method distributes the given licenses into their respective compatibility
        classes and then prepares output with each pair of conflicting licenses.

        :param license_vertices: license vertices that have some conflicting licenses
        :return: list of pairs of conflicting licenses
        """
        # first, let us find out compatibility classes for each vertex
        vertex2groups = {}
        for v in license_vertices:
            for item in self.dict_compatibility_classes.items():
                if v.get_prop_value('license') in item[1]:
                    vertex_groups = vertex2groups.get(v, [])
                    vertex_groups.append(item[0])
                    vertex2groups[v] = vertex_groups

        # also, we need to gather total unique classes for input vertices
        list_groups = []
        for v in license_vertices:
            vertex_groups = vertex2groups[v]
            list_groups += vertex_groups

        # create a dictionary to store vertex licenses per compatibility class
        list_groups = list(set(list_groups))
        assert(len(list_groups) > 1)

        list_items = [(x, []) for x in list_groups]
        map_groups = dict(list_items)
        # insert each vertex license into appropriate class
        for v in license_vertices:
            license = v.get_prop_value('license')
            vertex_groups = vertex2groups[v]
            # ignore vertex if it falls into every class
            if set(vertex_groups) != set(list_groups):
                for g in vertex_groups:
                    map_groups[g].append(license)

        # prepare output i.e. list of tuples with two conflicting licenses
        output = []
        for c1, c2 in itertools.combinations(list_groups, 2):  # nC2
            list1 = map_groups[c1]  # list of licenses in one class
            list2 = map_groups[c2]  # list of licenses in the other class
            common = set(list1).intersection(set(list2))
            list1 = list(set(list1) - common)
            list2 = list(set(list2) - common)
            for l1 in list1:
                for l2 in list2:
                    output.append(tuple(sorted((l1, l2))))

        # deduplicate the output tuples
        output = list(set(output))
        return output

    def _is_license_stricter(self, lic_type_a, lic_type_b):
        return self.license_type_tuple.index(lic_type_a) > \
               self.license_type_tuple.index(lic_type_b)

    def _is_license_stricter_or_same(self, lic_type_a, lic_type_b):
        return self.license_type_tuple.index(lic_type_a) >= \
               self.license_type_tuple.index(lic_type_b)

    def _find_outlier_licenses(self, license_vertices, stack_license_type):
        """Identify outlier packages based on licenses.

        A package is license based outlier, if
          - its license is in minority
          - it is not type-compatible with the licenses in majority.
          - its license is not less restrictive than licenses in majority

        Algorithm is as follows:
          for each type-compatible class, count how many input licenses fall there

          find the type-compatible class that has majority ( e.g. 60% ) of input licenses

          if stack license type is stricter than major type compatibility class then
            find all those licenses those fall into same or stricter type
            return them outlier licenses

        :param license_vertices: license vertices that have some conflicting licenses
        :param stack_license_type: stack license type
        :return:
        """
        # first, find how many vertices fall into each type-compatibility-class
        dict_tcc_count = {}
        dict_tcc_type = {}
        dict_tcc_licenses = {}
        for v in license_vertices:
            for t in self.dict_type_compatibility_classes.keys():
                dict_compatibles = self.dict_type_compatibility_classes.get(t, {
                })
                for item in dict_compatibles.items():
                    if v.get_prop_value('license') in item[1]:
                        dict_tcc_type[item[0]] = t

                        cnt = dict_tcc_count.get(item[0], 0)
                        cnt += 1
                        dict_tcc_count[item[0]] = cnt

                        list_licenses = dict_tcc_licenses.get(item[0], [])
                        list_licenses.append(v.get_prop_value('license'))
                        dict_tcc_licenses[item[0]] = list_licenses
        # check if there is a type-compatibility-class with majority
        majority = ceil(len(license_vertices) *
                        float(MAJORITY_THRESHOLD))
        major_tcc_lic = None
        for lic in dict_tcc_count.keys():
            if dict_tcc_count[lic] >= majority:
                major_tcc_lic = lic
                break

        if major_tcc_lic is not None:
            v = self.g.find_vertex('license', major_tcc_lic)
            major_tcc_type = v.get_prop_value('type')
            if self._is_license_stricter(stack_license_type, major_tcc_type):
                # find all the licenses that fall into same or stricter types
                items = [x for x in dict_tcc_type.items() if
                         self._is_license_stricter_or_same(x[1], major_tcc_type) and
                         x[0] != major_tcc_lic]
                list_outliers = []
                for i in items:
                    list_outliers += dict_tcc_licenses[i[0]]
                return list_outliers

        return []

    # TODO: needs refactoring
    def compute_representative_license(self, input_licenses):
        """Compute representative license for given list of licenses.

        First, it tries to identify the input licenses by using known synonyms.
        If there exists at least one unknown license, this method gives up.

        It makes use of a very popular license graph available in [1]. After
        identifying license vertices in the graph, it tries to find the
        common reachable vertex from the input license vertices.

        If a common reachable vertex is not possible then there is a conflict
        and all pairs of conflicting licenses are identified by using the
        concept of compatibility classes.

        If a common reachable vertex is available, then its license becomes
        representative license. Note that we also try to find outlier
        licenses when representative license is available.

        [1] https://www.dwheeler.com/essays/floss-license-slide.html

        :param input_licenses: list of input licenses
        :return: representative license with supporting information
        """
        output = {
            'status': 'Failure',
            'reason': 'Input is invalid',
            'representative_license': None,
            'unknown_licenses': [],
            'conflict_licenses': [],
            'outlier_licenses': [],
            'synonyms': {}
        }
        if input_licenses is None:
            return output
        if len(input_licenses) == 0:
            return output

        # Find synonyms
        input_lic_synonyms = [self.find_synonym(y) for y in input_licenses]
        output['synonyms'] = dict(list(zip(input_licenses, input_lic_synonyms)))

        # Check if all input licenses are known
        if len(set(input_lic_synonyms) - set(self.known_licenses)) > 0:
            output['status'] = 'Unknown'
            output['reason'] = 'Some unknown licenses found'
            output['unknown_licenses'] = list(
                set(input_lic_synonyms) - set(self.known_licenses))
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

            rep_lic_vertex = self.g.find_vertex('license', output['representative_license'])
            rep_lic_type = rep_lic_vertex.get_prop_value('type')
            output['outlier_licenses'] = self._find_outlier_licenses(license_vertices, rep_lic_type)
            return output

        # If one of the input licenses is NOT the representative one, then
        # let us pick up the least restrictive one
        for license_type in self.license_type_tuple:
            list_common_destinations = [
                x
                for x in reachable_vertices
                if x.get_prop_value(prop_name='type') == license_type
            ]
            if len(list_common_destinations) > 0:
                output['status'] = 'Successful'
                output['reason'] = 'Representative license found'
                output['representative_license'] = \
                    list_common_destinations[0].get_prop_value(prop_name='license')

                rep_lic_vertex = self.g.find_vertex('license', output['representative_license'])
                rep_lic_type = rep_lic_vertex.get_prop_value('type')
                output['outlier_licenses'] = self._find_outlier_licenses(license_vertices,
                                                                         rep_lic_type)
                return output

        # We should have returned by now ! Returning from here is unexpected !
        output['status'] = 'Failure'
        output['reason'] = 'Something unexpected happened!'
        output['representative_license'] = None
        return output

    def _get_compatibility_classes(self, input_license):
        list_comp_classes = []
        for comp_class, comp_licenses in self.dict_compatibility_classes.items():
            if input_license in comp_licenses:
                list_comp_classes.append(comp_class)

        return list_comp_classes

    def check_compatibility(self, lic_a, list_lic_b):
        """Check the compatibility of two licenses."""
        output = {
            'status': 'Failure',
            'reason': 'Input is invalid',
            'unknown_licenses': [],
            'conflict_licenses': [],
            'compatible_licenses': [],
            'synonyms': []
        }
        if lic_a is None or not list_lic_b:
            return output

        # find synonyms
        lic_a = self.find_synonym(lic_a)
        list_lic_b_synonyms = [self.find_synonym(y) for y in list_lic_b]
        output['synonyms'] = dict(list(zip(list_lic_b, list_lic_b_synonyms)))

        # check if all input licenses are known
        if len(set(list_lic_b_synonyms) - set(self.known_licenses)) > 0:
            output['unknown_licenses'] = list(set(list_lic_b_synonyms) - set(self.known_licenses))
            list_lic_b_synonyms = list(set(list_lic_b_synonyms).intersection(set(
                self.known_licenses)))

            if len(list_lic_b_synonyms) == 0:
                output['status'] = 'Failure'
                output['reason'] = 'All the input licenses are unknown!'
                return output

        # we will now work with the synonyms
        list_lic_b = list_lic_b_synonyms

        # now, we need to find compatibility class for lic_b and every lic_b
        lic_a_group = self._get_compatibility_classes(lic_a)
        assert(len(lic_a_group) > 0)
        lic_b_groups = {lic_b: self._get_compatibility_classes(lic_b) for lic_b in list_lic_b}

        # initialize dict that maps every lic_b to one of lic_a's compatibility classes
        map_compatibility = {x: [] for x in lic_a_group}

        # create groups of licenses that are compatible with the given input license
        list_conflicting_licenses = []
        for lic_b in list_lic_b:
            common_groups = set(lic_b_groups[lic_b]).intersection(lic_a_group)
            if len(common_groups) > 0:
                for g in common_groups:
                    map_compatibility[g].append(lic_b)
            else:
                list_conflicting_licenses.append(lic_b)

        # deduplicate the list of lists of compatible licenses
        list_compatible_licenses = [
            x for x in map_compatibility.values() if len(x) > 0]
        set_compatible_licenses = set(tuple(x)
                                      for x in list_compatible_licenses)
        list_compatible_licenses = [list(x) for x in set_compatible_licenses]

        output['status'] = 'Successful'
        output['reason'] = 'Compatibility and/or conflict identified'
        output['conflict_licenses'] = list_conflicting_licenses
        output['compatible_licenses'] = list_compatible_licenses

        return output
