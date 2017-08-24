from src.license_analysis import LicenseAnalyzer
from src.util.data_store.local_filesystem import LocalFileSystem


def test_print_graph():
    src_dir = "/Users/hmistry/work/license_analysis/src/fabric8-analytics-license-analysis/tests/license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "/Users/hmistry/work/license_analysis/src/fabric8-analytics-license-analysis/tests/synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    license_analyzer.print_license_graph()


def test_compute_rep_license_successful():
    src_dir = "/Users/hmistry/work/license_analysis/src/fabric8-analytics-license-analysis/tests/license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "/Users/hmistry/work/license_analysis/src/fabric8-analytics-license-analysis/tests/synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    output = license_analyzer.compute_representative_license(input_licenses=None)
    assert output['status'] is 'Failure'
    assert output['representative_license'] is None

    output = license_analyzer.compute_representative_license(input_licenses=[])
    assert output['status'] is 'Failure'
    assert output['representative_license'] is None

    list_licenses = ['This software released into the public domain. Anyone is free to copy']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] is 'Successful'
    assert output['representative_license'] == 'public domain'

    list_licenses = ['PD', 'MIT']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] is 'Successful'
    assert output['representative_license'] == 'mit'

    list_licenses = ['MIT', 'BSD', 'PD']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] is 'Successful'
    assert output['representative_license'] == 'bsd-new'


def test_compute_rep_license_unknown():
    src_dir = "/Users/hmistry/work/license_analysis/src/fabric8-analytics-license-analysis/tests/license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "/Users/hmistry/work/license_analysis/src/fabric8-analytics-license-analysis/tests/synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    list_licenses = ['SOME_JUNK_LIC']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] is 'Unknown'
    assert output['representative_license'] is None
    assert set(output['unknown_licenses']) == set(['SOME_JUNK_LIC'])


def test_compute_rep_license_conflict():
    src_dir = "/Users/hmistry/work/license_analysis/src/fabric8-analytics-license-analysis/tests/license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "/Users/hmistry/work/license_analysis/src/fabric8-analytics-license-analysis/tests/synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    list_licenses = ['APACHE', 'MPL 1.1']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] is 'Conflict'
    assert output['representative_license'] is None
    expected_conflict_licenses = [['apache 2.0'], ['mpl 1.1']]
    assert len(expected_conflict_licenses) == len(output['conflict_licenses'])
    for l in output['conflict_licenses']:
        assert l in expected_conflict_licenses


def test_compatibility_classes():
    src_dir = "/Users/hmistry/work/license_analysis/src/fabric8-analytics-license-analysis/tests/license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "/Users/hmistry/work/license_analysis/src/fabric8-analytics-license-analysis/tests/synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    license_analyzer.compute_compatibility_classes()

