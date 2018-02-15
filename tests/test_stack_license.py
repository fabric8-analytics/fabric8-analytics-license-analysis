"""Unit tests for the StackLicenseAnalyzer module."""

from src.stack_license import StackLicenseAnalyzer


# single instance of stack license analyzer
stack_license_analyzer = StackLicenseAnalyzer()


def test_input_sanity_checks():
    """Check if the method compute_stack_license perform input sanity checking."""
    payload = {
        'packages': []
    }
    output = stack_license_analyzer.compute_stack_license(payload=payload)
    assert output is not None
    assert output['status'] == 'Failure'
    assert output['message'] == 'Input was invalid'


def test_component_license_conflict():
    """Check if the conflict between licenses is detected properly."""
    payload = {
        'packages': [
            {
                'package': 'p1',
                'version': '1.1',
                'licenses': ['APACHE', 'PD']
            },
            {
                'package': 'p2',
                'version': '1.1',
                'licenses': ['GPL V3+', 'GPL V2']
            }
        ]
    }
    output = stack_license_analyzer.compute_stack_license(payload=payload)
    assert output is not None
    assert output['status'] == 'ComponentConflict'
    assert output['stack_license'] is None


def test_stack_license_conflict():
    """Check if the conflict between representative licenses is detected properly."""
    payload = {
        'packages': [
            {
                'package': 'p1',
                'version': '1.1',
                'licenses': ['APACHE', 'GPL V3+']
            },
            {
                'package': 'p2',
                'version': '1.1',
                'licenses': ['BSD', 'GPL V2']
            }
        ]
    }
    output = stack_license_analyzer.compute_stack_license(payload=payload)
    assert output is not None
    assert output['status'] == 'StackConflict'
    assert output['stack_license'] is None


def test_stack_license_successful():
    """Test if the representative license can be found."""
    payload = {
        'packages': [
            {
                'package': 'p1',
                'version': '1.1',
                'licenses': ['MIT', 'PD']
            },
            {
                'package': 'p2',
                'version': '1.1',
                'licenses': ['BSD', 'GPL V2']
            }
        ]
    }
    output = stack_license_analyzer.compute_stack_license(payload=payload)
    assert output is not None
    assert output['status'] == 'Successful'
    assert output['stack_license'] == 'gplv2'


def test_stack_license_filter():
    """Test if the representative licenses are computed correctly."""
    payload = {
        'packages': [
            {
                'package': 'p1',
                'version': '1.1',
                'licenses': ['MIT', 'PD']
            },
            {
                'package': 'p2',
                'version': '1.1',
                'licenses': ['BSD', 'GPL V2']
            }
        ],
        'alternate_packages': [
            {
                'package': 'p11',
                'version': '1.1',
                'licenses': ['APACHE']
            },
            {
                'package': 'p21',
                'version': '1.1',
                'licenses': ['BSD', 'GPL V2']
            },
            {
                'package': 'p31',
                'version': '1.1',
                'licenses': ['ABCD', 'XYZ']
            }
        ]
    }
    output = stack_license_analyzer.compute_stack_license(payload=payload)
    assert output is not None
    assert output['status'] == 'Successful'
    assert output['stack_license'] == 'gplv2'


def test_component_license_unknown():
    """Test if unknown license is detected properly."""
    payload = {
        'packages': [
            {
                'package': 'p1',
                'version': '1.1',
                'licenses': ['MIT', 'SOME_JUNK']
            },
            {
                'package': 'p2',
                'version': '1.1',
                'licenses': ['BSD', 'GPL V2']
            }
        ]
    }
    output = stack_license_analyzer.compute_stack_license(payload=payload)
    assert output is not None
    assert output['status'] == 'Unknown'
    assert output['stack_license'] is None


def test_component_license_failure():
    """Test how the package w/o any license is handled."""
    payload = {
        'packages': [
            {
                'package': 'p1',
                'version': '1.1',
                'licenses': []
            }
        ]
    }
    output = stack_license_analyzer.compute_stack_license(payload=payload)
    assert output is not None
    assert output['status'] == 'Failure'
    assert output['stack_license'] is None


def test_check_compatibility():
    """Test the method _check_compatibility."""
    packages = [{
                'package': 'p1',
                'version': '1.1',
                'licenses': ['GPL V2']
                }]
    output = stack_license_analyzer._check_compatibility('GPL V2', packages)
    assert output['compatible_packages'] == ['p1']
    assert not output['unknown_license_packages']
    assert not output['conflict_packages']

    packages = [{
                'package': 'p1',
                'version': '1.1',
                'licenses': ['GPL V2']
                },
                {
                'package': 'p2',
                'version': '1.1',
                'licenses': ['GPL V2']
                }]
    output = stack_license_analyzer._check_compatibility('GPL V2', packages)
    assert 'p1' in output['compatible_packages']
    assert 'p2' in output['compatible_packages']
    assert not output['unknown_license_packages']
    assert not output['conflict_packages']


def test_check_compatibility_conflicts():
    """Test the method _check_compatibility in case some licenses are in conflict."""
    packages = [{
                'package': 'p1',
                'version': '1.1',
                'licenses': ['GPL V2']
                },
                {
                'package': 'p2',
                'version': '1.1',
                'licenses': ['GPL V2']
                }]
    output = stack_license_analyzer._check_compatibility('GPL V3+', packages)
    assert not output['compatible_packages']
    assert not output['unknown_license_packages']
    assert 'p1' in output['conflict_packages']
    assert 'p2' in output['conflict_packages']

    packages = [{
                'package': 'p1',
                'version': '1.1',
                'licenses': ['GPL V2']
                },
                {
                'package': 'p2',
                'version': '1.1',
                'licenses': ['GPL V3+']
                }]
    output = stack_license_analyzer._check_compatibility('GPL V3+', packages)
    print(output)
    assert 'p2' in output['compatible_packages']
    assert 'p1' in output['conflict_packages']
    assert not output['unknown_license_packages']
