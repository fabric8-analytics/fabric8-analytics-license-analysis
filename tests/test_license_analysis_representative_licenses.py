"""Unit tests for the LicenseAnalyzer module."""

from src.license_analysis import LicenseAnalyzer
from src.util.data_store.local_filesystem import LocalFileSystem


def test_compute_representative_license_no_licenses():
    """Test the method LicenseAnalyzer.compute_representative_license() - none licenses found."""
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


def test_compute_representative_license_one_license():
    """Test the method LicenseAnalyzer.compute_representative_license() - one license found."""
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)

    list_licenses = ['This software released into the public domain. Anyone is free to copy']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'public domain'

    list_licenses = ['PD', 'MIT']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'mit'

    list_licenses = ['PD', 'MIT', 'ISC']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'ISC'

    list_licenses = ['MIT', 'BSD', 'PD']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'bsd-new'

    list_licenses = ['MIT', 'W3C', 'APACHE', 'BOUNCYCASTLE']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'apache 2.0'

    list_licenses = ['CPAL', 'CPL', 'EPL', 'MIT']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'epl 1.0'


def test_compute_representative_license_outlier_licenses():
    """Test the method LicenseAnalyzer.compute_representative_license() - outlier licenses."""
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)

    list_licenses = ['MIT', 'BSD', 'PD', 'APACHE', 'CDDL 1.0']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'epl 1.0'
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
    assert output['representative_license'] == 'epl 1.0'
    assert set(output['outlier_licenses']) == set(['lgplv2.1', 'lgplv3+'])


def test_compute_representative_license_unknown():
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
    assert set(output['unknown_licenses']) == set(['some_junk_lic'])
    assert output['reason'] == 'Some unknown licenses found'
    assert not output['conflict_licenses']
    assert not output['outlier_licenses']


def test_compute_representative_license_no_conflict():
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


def test_compute_representative_license_no_conflict_2():
    """Test method LicenseAnalyzer.compute_representative_license() for non-conflicting licenses."""
    src_dir = "license_graph"
    graph_store = LocalFileSystem(src_dir=src_dir)
    synonyms_dir = "synonyms"
    synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
    license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
    list_licenses = ['MIT', 'APACHE', 'MPL 1.1', 'lgplv2.1', 'lgplv3+']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] == 'Successful'
    assert output['representative_license'] == 'epl 1.0'


def test_compute_representative_license_conflict_1():
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


def test_compute_representative_license_conflict_2():
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
    assert 'gplv2' in conflicts[0] and 'gplv3+' in conflicts[0]
    # assert 'apache 2.0' in conflicts[0] or 'apache 2.0' in conflicts[1]
    # assert 'gplv3+' in conflicts[1] or 'gplv3+' in conflicts[0]


def test_compute_representative_license_conflict_3():
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


def test_compute_representative_license_repeating_licenses():
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
