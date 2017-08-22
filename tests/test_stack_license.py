from src.stack_license import compute_stack_license


def test_component_license_conflict():
    payload = {
        'packages': [
            {
                'name': 'p1',
                'version': '1.1',
                'licenses': ['APACHE', 'PD']
            },
            {
                'name': 'p2',
                'version': '1.1',
                'licenses': ['APACHE', 'GPL V2']
            }
        ]
    }
    output = compute_stack_license(payload=payload)
    assert output is not None
    assert output['status'] is 'ComponentLicenseConflict'
    assert output['stack_license'] is None


def test_stack_license_conflict():
    payload = {
        'packages': [
            {
                'name': 'p1',
                'version': '1.1',
                'licenses': ['APACHE', 'PD']
            },
            {
                'name': 'p2',
                'version': '1.1',
                'licenses': ['BSD', 'GPL V2']
            }
        ]
    }
    output = compute_stack_license(payload=payload)
    assert output is not None
    assert output['status'] is 'StackLicenseConflict'
    assert output['stack_license'] is None


def test_stack_license_successful():
    payload = {
        'packages': [
            {
                'name': 'p1',
                'version': '1.1',
                'licenses': ['MIT', 'PD']
            },
            {
                'name': 'p2',
                'version': '1.1',
                'licenses': ['BSD', 'GPL V2']
            }
        ]
    }
    output = compute_stack_license(payload=payload)
    assert output is not None
    assert output['status'] is 'Successful'
    assert output['stack_license'] == 'gplv2'


def test_component_license_unknown():
    payload = {
        'packages': [
            {
                'name': 'p1',
                'version': '1.1',
                'licenses': ['MIT', 'SOME_JUNK']
            },
            {
                'name': 'p2',
                'version': '1.1',
                'licenses': ['BSD', 'GPL V2']
            }
        ]
    }
    output = compute_stack_license(payload=payload)
    assert output is not None
    assert output['status'] is 'Unknown'
    assert output['stack_license'] is None
