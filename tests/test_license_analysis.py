from src.license_analysis import LicenseAnalyzer


def test_print_graph():
    license_analyzer = LicenseAnalyzer()
    license_analyzer.print_license_graph()


def test_compute_rep_license_successful():
    license_analyzer = LicenseAnalyzer()
    output = license_analyzer.compute_representative_license(input_licenses=None)
    assert output['status'] is 'Failure'
    assert output['representative_license'] is None

    output = license_analyzer.compute_representative_license(input_licenses=[])
    assert output['status'] is 'Failure'
    assert output['representative_license'] is None

    list_licenses = ['PD']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] is 'Successful'
    assert output['representative_license'] is 'PD'

    list_licenses = ['PD', 'MIT']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] is 'Successful'
    assert output['representative_license'] is 'MIT'

    list_licenses = ['MIT', 'BSD', 'PD']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] is 'Successful'
    assert output['representative_license'] is 'BSD'


def test_compute_rep_license_unknown():
    license_analyzer = LicenseAnalyzer()
    list_licenses = ['SOME_JUNK_LIC']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] is 'Unknown'
    assert output['representative_license'] is None


def test_compute_rep_license_conflict():
    license_analyzer = LicenseAnalyzer()
    list_licenses = ['APACHE', 'MPL 1.1']
    output = license_analyzer.compute_representative_license(list_licenses)
    assert output['status'] is 'Conflict'
    assert output['representative_license'] is None
