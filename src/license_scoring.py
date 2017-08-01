from abc import ABCMeta, abstractmethod
import pickle
import itertools
import pandas as pd


available_licenses = [
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
    'AGPL V3+']


license_master_df = pd.DataFrame({"license": [],
                       "category": [],
                        "cat_rank": []})

def license_master_add_df(name, category, rank,  license_master_df):
    df_to_append = pd.DataFrame({"license": name,
                                     "category": category,
                                 "cat_rank": rank
                                })

    df = pd.concat([license_master_df, df_to_append], ignore_index=True)

    return df

license_master_df = license_master_add_df(['PD'], ['P'], [1], license_master_df)
license_master_df = license_master_add_df(['MIT'], ['P'], [1], license_master_df)
license_master_df = license_master_add_df(['BSD'], ['P'], [1], license_master_df)
license_master_df = license_master_add_df(['APACHE'], ['P'], [1], license_master_df)
license_master_df = license_master_add_df(['LGPL V2.1'], ['WP'], [2], license_master_df)
license_master_df = license_master_add_df(['LGPL V2.1+'], ['WP'], [2], license_master_df)
license_master_df = license_master_add_df(['LGPL V3+'], ['WP'], [2], license_master_df)
license_master_df = license_master_add_df(['MPL 1.1'], ['WP'], [2], license_master_df)
license_master_df = license_master_add_df(['GPL V2'], ['SP'], [3], license_master_df)
license_master_df = license_master_add_df(['GPL V2+'], ['SP'], [3], license_master_df)
license_master_df = license_master_add_df(['GPL V3+'], ['SP'], [3], license_master_df)
license_master_df = license_master_add_df(['AGPL V3+'], ['NP'], [4], license_master_df)


class AbstractGnosis(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def train(cls, data_store):
        """
        Trains/De-dupes Gnosis from gnosis files, which should in the following json format:

        :param data_store: data store where various input gnosis files are stored
        :return: Gnosis object
        """
        return

    @abstractmethod
    def load(cls, data_store, filename):
        """
        Loads already saved Gnosis
        """
        return

    @abstractmethod
    def save(self, data_store, filename):
        """
        Saves the Gnosis in data_store
        """
        return



class LicenseVertex:
    def __init__(self, arg_list):
        self.id = arg_list[0]
        self.license_type = arg_list[1]
        self.adjacent = dict()

    def __str__(self):
        return str(self.id) + ' adjacent: ' + str([x.id for x in self.adjacent])

    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def get_connections(self):
        return self.adjacent.keys()

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]



class GnosisLicense(AbstractGnosis):
    def __init__(self):
        self.vert_dict = dict()
        self.num_vertices = 0
        self.license_type_tuple = ('P', 'WP', 'SP', 'NP')

    def __iter__(self):
        return iter(self.vert_dict.values())

    def add_vertex(self, node):
        self.num_vertices = self.num_vertices + 1
        self.vert_dict[node.id] = node
        return node

    def get_vertex(self, n):
        if n in self.vert_dict:
            return self.vert_dict[n]
        else:
            return None

    def add_edge(self, frm, to, cost=0):
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)

    def get_vertices(self):
        return self.vert_dict.keys()

    def get_reachable_vertices(self, node):
        reachable_node_list = node.get_connections()
        for vertex in reachable_node_list:
            temp_list = vertex.get_connections()
            for temp_vertex in temp_list:
                if temp_vertex not in reachable_node_list:
                    reachable_node_list.append(temp_vertex)
        return [node] + reachable_node_list

    def get_license_vertex_by_id(self, id_name):
        for vertex in self.get_vertices():
            if vertex.id is id_name:
                return vertex
        return None

    def get_common_destination_license_vertex(self, list_of_licenses):
        reachable_vertex_list = None
        for i in xrange(0, len(list_of_licenses)):
            vertex = self.get_vertex(list_of_licenses[i])
            reachable_vertices = self.get_reachable_vertices(vertex)
            reachable_licenses = [x.id for x in reachable_vertices]
            if reachable_vertex_list is None:
                reachable_vertex_list = reachable_vertices
            else:
                reachable_vertex_list = [license_vertex for license_vertex in reachable_vertex_list if
                                         license_vertex.id in reachable_licenses]

        common_destination = None
        if len(reachable_vertex_list) > 0:
            for license_vertex in reachable_vertex_list:
                if license_vertex.id in list_of_licenses:
                    common_destination = [license_vertex]

            if common_destination is None:
                for license_type in self.license_type_tuple:
                    common_destination = [x for x in reachable_vertex_list if x.license_type is license_type]
                    if len(common_destination) > 0:
                        break
        return common_destination

    def train(cls, data_store):
        """
        Trains/De-dupes Gnosis from gnosis files, which should in the following json format:

        :param data_store: data store where various input gnosis files are stored
        :return: Gnosis object
        """
        return

    def load(cls, data_store, filename):
        """
        Loads already saved Gnosis
        """
        return

    def save(self, data_store, filename):
        """
        Saves the Gnosis in data_store
        """
        return



def create_license_graph():
    g = GnosisLicense()
    pd = LicenseVertex(['PD', 'P'])
    mit = LicenseVertex(['MIT', 'P'])
    bsd = LicenseVertex(['BSD', 'P'])
    apache = LicenseVertex(['APACHE', 'P'])
    lgpl2 = LicenseVertex(['LGPL V2.1', 'WP'])
    lgpl22 = LicenseVertex(['LGPL V2.1+', 'WP'])
    lgpl3 = LicenseVertex(['LGPL V3+', 'WP'])
    mpl = LicenseVertex(['MPL 1.1', 'WP'])
    gpl2 = LicenseVertex(['GPL V2', 'SP'])
    gpl22 = LicenseVertex(['GPL V2+', 'SP'])
    gpl3 = LicenseVertex(['GPL V3+', 'SP'])
    agpl3 = LicenseVertex(['AGPL V3+', 'NP'])

    g.add_vertex(pd)
    g.add_vertex(mit)
    g.add_vertex(bsd)
    g.add_vertex(apache)
    g.add_vertex(lgpl2)
    g.add_vertex(lgpl22)
    g.add_vertex(lgpl3)
    g.add_vertex(mpl)
    g.add_vertex(gpl2)
    g.add_vertex(gpl22)
    g.add_vertex(gpl3)
    g.add_vertex(agpl3)

    g.add_edge('PD', 'MIT')
    g.add_edge('MIT', 'BSD')
    g.add_edge('BSD', 'APACHE')
    g.add_edge('BSD', 'MPL 1.1')
    g.add_edge('BSD', 'LGPL V2.1')
    g.add_edge('BSD', 'LGPL V2.1+')
    g.add_edge('BSD', 'LGPL V3+')
    g.add_edge('APACHE', 'LGPL V3+')
    g.add_edge('LGPL V2.1+', 'LGPL V2.1')
    g.add_edge('LGPL V2.1+', 'LGPL V3+')
    g.add_edge('LGPL V2.1', 'GPL V2')
    g.add_edge('LGPL V2.1', 'GPL V2+')
    g.add_edge('LGPL V2.1+', 'GPL V2+')
    g.add_edge('LGPL V3+', 'GPL V3+')
    g.add_edge('GPL V2+', 'GPL V2')
    g.add_edge('GPL V2+', 'GPL V3+')
    g.add_edge('GPL V3+', 'AGPL V3+')

    return g



def get_conflict_licenses(license_graph, list_of_licenses):
    conflict_licenses = []

    for lic1, lic2 in itertools.combinations(list_of_licenses, 2):
        combination_license = license_graph.get_common_destination_license_vertex(list_of_licenses)

        if combination_license is None:
            conflict_licenses.append(lic1)
            conflict_licenses.append(lic2)

    return list(set(conflict_licenses))



def licenses_avl(list_of_licenses):
    license_diff = list(set(list_of_licenses) - set(available_licenses))
    if len(license_diff) > 0:
        print
        "The following licenses aren't available. Please check back later"
        print
        license_diff
        return 1
    else:
        return 0



def create_df(payload):
    df = pd.DataFrame({"package": [],
                       "version": [],
                       "license": []})

    for pkg in payload["packages"]:
        df_to_append = pd.DataFrame({"package": [pkg["package"]],
                                     "version": [pkg["version"]],
                                     "license": [pkg["license"][0]]})

        df = pd.concat([df, df_to_append], ignore_index=True)

    return df



def get_outlier_licenses(payload_pd, s_license):
    """
    Given list of licenses, find the license(s) that cause the stack license to become more restrictive
    """
    outlier_license_with_category = pd.merge(payload_pd, 
                                            license_master_df,
                                            how = "inner",
                                            on= "license")
    #print "\n"
    #print outlier_license_with_category
    #print "\n"
    #print "Stack license:", s_license
    
    stack_license_rank = license_master_df.loc[license_master_df.license==s_license, "cat_rank"]
    #print "stack rank:", stack_license_rank.iloc[0]
    #print "\n"
    stack_rank = stack_license_rank.iloc[0]
    
    license_counts = outlier_license_with_category.groupby("cat_rank")["cat_rank"].count()
    license_counts = pd.DataFrame(license_counts)
    license_counts.columns = ["rank_count"]
    license_counts = license_counts.reset_index()
    #print "license counts", license_counts

    #print "\n"
    #print "... \n"
    #print license_counts
    #print "\n"
    #print "Until here its fine", "\n"
    #stack_rank = 5.0  # step introduced for debugging
    stack_license_count_in_stack = license_counts[license_counts.cat_rank==stack_rank].rank_count
    
    if len(stack_license_count_in_stack) > 0:
        stack_license_count = stack_license_count_in_stack.iloc[0]
        max_stack_rank = stack_rank
        max_count = stack_license_count  
        
    else:
        stack_license_count = 0
        max_stack_rank = license_counts["cat_rank"].max()
        max_count = license_counts[license_counts["cat_rank"] == max_stack_rank]["rank_count"].iloc[0]
        

    #print "\n", "stack license count.." , "\n", stack_license_count
    #print "\n", "max count.." , "\n", max_count
    #print "\n", "max stack rank.." , "\n", max_stack_rank
    
    #print "\n Are there outliers?: Quantify \n"
    #print max_count , " divided by ", outlier_license_with_category.shape[0]
    #print "\n"
    #print float(max_count)/outlier_license_with_category.shape[0]
    
    if (float(max_count)/outlier_license_with_category.shape[0]) >= 0.5:
        license_outliers = "None"
    else:
        license_outliers = outlier_license_with_category.loc[outlier_license_with_category.cat_rank == max_stack_rank, ["license", "package", "version"]].to_json(orient="records")
        
    
    #print "\n license outliers \n"
    #print license_outliers
    
    return license_outliers


# This is the main function that does the scoring
def license_scoring_v1(payload):
    """
    Given packages and their respective licenses, return the license of the stack.
    In some cases, the licenses of the packages may cause conflict. If so, return those packages.
    Some packages may cause the license of the stack to become more restrictive. Return those outlier packages
    """

    payload_pd = create_df(payload)
    #print payload_pd
    list_of_licenses = list(payload_pd.license)

    license_graph = create_license_graph()

    # Check if input licenses are present in license graph
    all_licenses_available_in_graph = licenses_avl(list_of_licenses)
    conflict_response = ""

    if all_licenses_available_in_graph == 1:
        # not all licenses are available
        s_license = "None"
        conflict_licenses = "None"
        outliers = "None"

    else:

        stack_license = license_graph.get_common_destination_license_vertex(list_of_licenses)

        conflict_licenses = ""

        if stack_license is None:
            s_license = ''
            conflict_licenses = get_conflict_licenses(license_graph, list_of_licenses)
        else:
            s_license = [i.id for i in stack_license][0]

        #Create response for conflict licenses

        if len(conflict_licenses) > 0:
            conflict_license_records = payload_pd[payload_pd.license.isin(conflict_licenses)].copy()
            conflict_license_records["pkg-ver"] = conflict_license_records.package + "-" + conflict_license_records.version
            conflict_response = conflict_license_records[["pkg-ver", "license"]].to_json(orient="records")

        else:
            conflict_response = "None"

        # Find outliers
        if stack_license is None:
            outliers = ""
        else:
            outliers = get_outlier_licenses(payload_pd, s_license)

    # Create response object
    # Testing integration locally now. Returning dummy results (21-July-2017)
    # Start of test result
    s_license = "MIT License"
    
    conflict_response =  [
    {
      "package": "pkg1",
      "version": "ver1",
      "license": "license1"
    },
    {
      "package": "pkg2",
      "version": "ver2",
      "license": "license2"
    }
    ]

    outliers = [
    {
      "package": "pkg1",
      "version": "ver1",
      "license": "license1"
    },
    {
      "package": "pkg2",
      "version": "ver2",
      "license": "license2"
    }
    ]

    # End of test result


def license_scoring(payload):
    response = {
    "dependencies": [
      {
        "unknown_licenses": [],
        "license_conflict": False,
        "license_outlier": False
      }
    ],
    "recommended_stack_licenses": [],
    "stack_license_conflict_exists": False,
    "stack_unknown_licenses": []
    }

    return response

