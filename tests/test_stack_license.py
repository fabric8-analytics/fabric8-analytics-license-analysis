from src.stack_license import StackLicenseAnalyzer


# single instance of stack license analyzer
stack_license_analyzer = StackLicenseAnalyzer()


def test_component_license_conflict():
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
