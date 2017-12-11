from src.license_analysis import LicenseAnalyzer
from src.util.data_store.local_filesystem import LocalFileSystem


def test_print_graph():
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    license_analyzer.print_license_graph()


def test_compute_rep_license_successful():
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)

    output = license_analyzer.compute_representative_license(
        input_licenses=None)
    assert output['status'] == 'Failure'
    assert output['representative_license'] is None

    output = license_analyzer.compute_representative_license(input_licenses=[])
    assert output['status'] == 'Failure'
    assert output['representative_license'] is None

    list_licenses = ['This software released into the public domain. Anyone is free to copy']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'public domain'

    list_licenses = ['PD', 'MIT']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'mit'

    list_licenses = ['MIT', 'BSD', 'PD']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'bsd-new'

    list_licenses = ['MIT', 'BSD', 'PD', 'MPL 1.1']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'mpl 1.1'
    assert set(output['outlier_licenses']) == set(['mpl 1.1'])

    list_licenses = ['MIT', 'BSD', 'PD', 'lgplv2.1', 'lgplv3+']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'gplv3+'
    assert set(output['outlier_licenses']) == set(['lgplv2.1', 'lgplv3+'])


def test_compute_rep_license_unknown():
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    list_licenses = ['SOME_JUNK_LIC']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Unknown'
    assert output['representative_license'] is None
    assert set(output['unknown_licenses']) == set(['SOME_JUNK_LIC'])


def test_compute_rep_license_conflict():
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    list_licenses = ['APACHE', 'MPL 1.1']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'epl 1.0'

def test_compute_rep_license_conflict_2():
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    list_licenses = ['MIT', 'APACHE', 'MPL 1.1', 'lgplv2.1', 'lgplv3+']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Conflict'
    assert output['representative_license'] is None
    expected_conflict_licenses = [('apache 2.0', 'lgplv2.1'),
                                  ('lgplv2.1', 'mpl 1.1'),
                                  ('lgplv3+', 'mpl 1.1')]
    assert set(expected_conflict_licenses) == set(output['conflict_licenses'])

def test_compute_rep_license_conflict_3():
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    list_licenses = ['epl 1.0', 'lgplv3+']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Conflict'
    assert output['representative_license'] is None
    expected_conflict_licenses = [('epl 1.0', 'lgplv3+')]
    assert set(expected_conflict_licenses) == set(output['conflict_licenses'])

def test_check_compatibility():
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)

    lic_a = 'APACHE'
    list_lic_b = []
    output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    assert output['status'] == 'Failure'
    assert output['reason'] == 'Input is invalid'

    lic_a = 'APACHE'
    list_lic_b = ['abcd', 'xyz']  # some unknown
    output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    assert output['status'] == 'Failure'
    assert output['reason'] == 'All the input licenses are unknown!'
    unknown_licenses = set(output['unknown_licenses'])
    assert unknown_licenses == set(['abcd', 'xyz'])

    lic_a = 'APACHE'
    list_lic_b = ['PD', 'MIT', 'BSD']  # all permissive
    output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    assert output['status'] == 'Successful'
    assert len(output['compatible_licenses']) == 1
    compatible_licenses = set(output['compatible_licenses'][0])
    assert compatible_licenses == set(['public domain', 'mit', 'bsd-new'])

    lic_a = 'PD'
    list_lic_b = ['PD', 'MIT', 'BSD']  # all permissive
    output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    assert output['status'] == 'Successful'
    assert len(output['compatible_licenses']) == 1
    compatible_licenses = set(output['compatible_licenses'][0])
    assert compatible_licenses == set(['public domain', 'mit', 'bsd-new'])

    lic_a = 'PD'
    list_lic_b = ['APACHE', 'MIT']
    output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    assert output['status'] == 'Successful'
    assert len(output['compatible_licenses']) == 2
    compatible_licenses1 = set(output['compatible_licenses'][0])
    compatible_licenses2 = set(output['compatible_licenses'][1])
    assert (compatible_licenses2 == set(['mit', 'apache 2.0']) or
            compatible_licenses1 == set(['mit', 'apache 2.0']))
    assert (compatible_licenses2 == set(['mit']) or compatible_licenses1 == set(['mit']))

    lic_a = 'APACHE'
    list_lic_b = ['MIT', 'lgplv2.1', 'MPL 1.1']
    output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    assert output['status'] == 'Successful'
    assert len(output['compatible_licenses']) == 1
    compatible_licenses = set(output['compatible_licenses'][0])
    assert compatible_licenses == set(['mit', 'lgplv2.1'])
    assert len(output['conflict_licenses']) == 1
    conflict_licenses = set(output['conflict_licenses'][0])
    assert conflict_licenses == set('mpl 1.1')

