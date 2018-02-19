"""Unit tests for the LicenseAnalyzer module."""

from src.license_analysis import LicenseAnalyzer
from src.util.data_store.local_filesystem import LocalFileSystem


def test_print_graph():
    """Check the method print_license_graph."""
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    # TODO does not check the actual output!
    license_analyzer.print_license_graph()


def test_compute_rep_license_successful():
    """Test the method LicenseAnalyzer.compute_representative_license()."""
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

    list_licenses = ['epl 1.0', 'lgplv3+']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'lgplv3+'

    list_licenses = ['MIT', 'BSD', 'PD']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'bsd-new'

    list_licenses = ['MIT', 'W3C', 'APACHE', 'BOUNCYCASTLE']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'apache 2.0'

    list_licenses = ['GPL 2', 'W3C', 'APACHE', 'BOUNCYCASTLE', 'CDDL 2', 'CPAL']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'gplv2'

    list_licenses = ['CPAL', 'CPL', 'EPL', 'MIT']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'mpl 2.0'

    list_licenses = ['MIT', 'BSD', 'PD', 'APACHE', 'CDDL 1.0']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'cddlv1.1+'
    assert set(output['outlier_licenses']) == set(['cddlv1.1+'])

    list_licenses = ['MIT', 'BSD', 'PD', 'MPL 1.1']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'mpl 1.1'
    assert set(output['outlier_licenses']) == set(['mpl 1.1'])

    list_licenses = ['MIT', 'BSD', 'MPL 2.0']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'mpl 2.0'
    assert set(output['outlier_licenses']) == set(['mpl 2.0'])

    list_licenses = ['MIT', 'BSD', 'PD', 'lgplv2.1', 'lgplv3+']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'gplv3+'
    assert set(output['outlier_licenses']) == set(['lgplv2.1', 'lgplv3+'])


def test_compute_rep_license_unknown():
    """Test the method LicenseAnalyzer.compute_representative_license() for unknown license."""
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
    assert output['reason'] == 'Some unknown licenses found'
    assert not output['conflict_licenses']
    assert not output['outlier_licenses']


def test_compute_rep_license_no_conflict():
    """Test method LicenseAnalyzer.compute_representative_license() for non-conflicting licenses."""
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    list_licenses = ['APACHE', 'MPL 2.0']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'mpl 2.0'
    assert "conflict_licenses" in output
    assert not output['conflict_licenses']
    assert not output['outlier_licenses']


def test_compute_rep_license_no_conflict_2():
    """Test method LicenseAnalyzer.compute_representative_license() for non-conflicting licenses."""
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    list_licenses = ['MIT', 'APACHE', 'MPL 1.1', 'lgplv2.1', 'lgplv3+']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'gplv3+'
    assert "conflict_licenses" in output
    assert output['conflict_licenses'] == []


def test_compute_rep_license_conflict_1():
    """Test the method LicenseAnalyzer.compute_representative_license() for conflicting licenses."""
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    list_licenses = ['gplv2', 'gplv3+']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Conflict'
    assert output['representative_license'] is None
    assert "conflict_licenses" in output
    conflicts = output["conflict_licenses"]
    assert len(conflicts) == 1
    assert 'gplv2' in conflicts[0]
    assert 'gplv3+' in conflicts[0]


def test_compute_rep_license_conflict_2():
    """Test the method LicenseAnalyzer.compute_representative_license() for conflicting licenses."""
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    list_licenses = ['gplv2', 'gplv3+', 'MIT', 'APACHE']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Conflict'
    assert output['representative_license'] is None
    assert "conflict_licenses" in output
    conflicts = output["conflict_licenses"]
    assert len(conflicts) == 1
    assert 'gplv2' in conflicts[0]
    assert 'gplv3+' in conflicts[0]


def test_compute_rep_license_conflict_3():
    """Test the method LicenseAnalyzer.compute_representative_license() for conflicting licenses."""
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    list_licenses = ['affero gplv3', 'gplv3+', 'gplv2']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Conflict'
    assert output['representative_license'] is None
    assert "conflict_licenses" in output
    conflicts = output["conflict_licenses"]
    assert len(conflicts) == 2
    assert 'gplv2' in conflicts[0]
    assert 'gplv2' in conflicts[1]
    assert 'gplv3+' in conflicts[0] or 'gplv3+' in conflicts[1]
    assert 'affero gplv3' in conflicts[0] or 'affero gplv3' in conflicts[1]


def test_compute_rep_license_repeating_licenses():
    """Test the method LicenseAnalyzer.compute_representative_license() for correct behaviour."""
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    list_licenses = ['gplv2', 'gplv2', 'gplv2']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['reason'] == 'Representative license found'
    assert output['representative_license'] == 'gplv2'
    assert not output['unknown_licenses']
    assert not output['conflict_licenses']
    assert not output['outlier_licenses']
    assert 'gplv2' in output['synonyms']


def test_check_compatibility_input_sanity_checks():
    """Test the method LicenseAnalyzer.check_compatibility(): the input sanity checks."""
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)

    #lic_a = None
    #list_lic_b = []
    #output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    #assert output['status'] == 'Failure'
    #assert output['reason'] == 'Input is invalid'
    #assert not output['unknown_licenses']
    #assert not output['conflict_licenses']
    #assert not output['compatible_licenses']

    #lic_a = None
    #list_lic_b = ["x", "y", "z"]
    #output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    #assert output['status'] == 'Failure'
    #assert output['reason'] == 'Input is invalid'
    #assert not output['unknown_licenses']
    #assert not output['conflict_licenses']
    #assert not output['compatible_licenses']

    #lic_a = 'APACHE'
    #list_lic_b = []
    #output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    #assert output['status'] == 'Failure'
    #assert output['reason'] == 'Input is invalid'
    #assert not output['unknown_licenses']
    #assert not output['conflict_licenses']
    #assert not output['compatible_licenses']


def test_check_compatibility():
    """Test the method LicenseAnalyzer.check_compatibility()."""
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)

    lic_a = 'APACHE'
    list_lic_b = ['abcd', 'xyz']  # some unknown
    output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    assert output['status'] == 'Failure'
    assert output['reason'] == 'All the input licenses are unknown!'
    unknown_licenses = set(output['unknown_licenses'])
    assert unknown_licenses == set(['abcd', 'xyz'])
    assert not output['conflict_licenses']
    assert not output['compatible_licenses']

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
    assert len(output['compatible_licenses']) == 1
    compatible_licenses = set(output['compatible_licenses'][0])
    assert compatible_licenses == set(['apache 2.0', 'mit'])

    lic_a = 'APACHE'
    list_lic_b = ['MIT', 'lgplv2.1', 'MPL 1.1']
    output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    assert output['status'] == 'Successful'
    assert len(output['compatible_licenses']) == 1
    compatible_licenses = set(output['compatible_licenses'][0])
    assert compatible_licenses == set(['mit', 'lgplv2.1', 'mpl 1.1'])

    lic_a = 'CDDL 1.1'
    list_lic_b = ['MIT', 'lgplv2.1', 'MPL 1.1']
    output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    assert output['status'] == 'Successful'
    assert len(output['compatible_licenses']) == 1
    compatible_licenses = set(output['compatible_licenses'][0])
    assert compatible_licenses == set(['lgplv2.1', 'mit', 'mpl 1.1'])

    lic_a = 'PD'
    list_lic_b = ['MIT', 'BSD (2 clause)']
    output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    assert output['status'] == 'Successful'
    assert len(output['compatible_licenses']) == 1
    compatible_licenses = set(output['compatible_licenses'][0])
    assert compatible_licenses == set(['bsd-simplified', 'mit'])

    lic_a = 'CPL'
    list_lic_b = ['MIT', 'CPAL', 'PostgreSQL', 'JSON']
    output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    assert output['status'] == 'Successful'
    assert len(output['compatible_licenses']) == 1
    compatible_licenses = set(output['compatible_licenses'][0])
    assert compatible_licenses == set(['mit', 'postgresql', 'cpal 1.0', 'json'])


def test_check_compatibility_conflicting_licenses():
    """Test the method LicenseAnalyzer.check_compatibility()."""
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)

    lic_a = 'gplv2'
    list_lic_b = ['gplv3+']
    output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    assert output['status'] == 'Successful'
    assert output['reason'] == 'Compatibility and/or conflict identified'
    assert output['conflict_licenses'] == ['gplv3+']


def test_check_compatibility_conflicting_licenses_2():
    """Test the method LicenseAnalyzer.check_compatibility()."""
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)

    lic_a = 'gplv2'
    # the license 'gplv2' is repeated here:
    list_lic_b = ['gplv2', 'gplv3+']
    output = license_analyzer.check_compatibility(lic_a, list_lic_b)
    assert output['status'] == 'Successful'
    assert output['reason'] == 'Compatibility and/or conflict identified'
    assert output['conflict_licenses'] == ['gplv3+']


def test_create_graph():
    """Test the method _create_graph()."""
    # this is quite dummy test, because the method _create_graph is not used ATM
    g = LicenseAnalyzer._create_graph()
    assert g is not None
