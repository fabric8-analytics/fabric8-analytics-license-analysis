"""Unit tests for the StackLicenseAnalyzer module."""

from unittest.mock import *
from src.stack_license import *


# single instance of stack license analyzer
stack_license_analyzer = StackLicenseAnalyzer()


def test_input_sanity_checks():
    """Check if the method compute_stack_license perform input sanity checking."""
    payload = None
    output = stack_license_analyzer.compute_stack_license(payload=payload)
    assert output is not None
    assert output['status'] == 'Failure'
    assert output['message'] == 'Input was invalid'

    payload = {}
    output = stack_license_analyzer.compute_stack_license(payload=payload)
    assert output is not None
    assert output['status'] == 'Failure'
    assert output['message'] == 'Input was invalid'

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


# this does not needs to be tested, the special handling code has been commented out in sources
@patch('src.stack_license.len', return_value=0)
def __test_component_license_weird_failure(_mocking_object):
    """Test how the package w/o any license is handled."""
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
    assert output['status'] == 'Failure'
    assert output['stack_license'] is None
    assert output['message'] == 'Something weird happened!'


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
    assert 'p2' in output['compatible_packages']
    assert 'p1' in output['conflict_packages']
    assert not output['unknown_license_packages']


def test_stack_licenses_computation():
    """Check that the stack license is computed."""
    payload = {
        'packages': [
            {
                'package': 'p1',
                'version': '1.1',
                'licenses': ['PD', 'APACHE', 'CDDL 1.0']
            },
            {
                'package': 'p2',
                'version': '1.1',
                'licenses': ['MIT']
            },
            {
                'package': 'p3',
                'version': '1.1',
                'licenses': ['BSD']
            },
        ]
    }
    output = stack_license_analyzer.compute_stack_license(payload=payload)
    assert output is not None
    assert output['status'] == 'Successful'
    assert output['stack_license'] == 'cddlv1.1+'
    assert output["outlier_packages"] == {'p1': 'cddlv1.1+'}


def test_unexpected_exception_handling():
    """Test that the improper payload is process w/o failures."""
    # the payload is not correct so we expect the exception to occur
    payload = {
        'packages': 'garbage'
    }
    output = stack_license_analyzer.compute_stack_license(payload=payload)
    assert output is not None
    assert output['status'] == 'Failure'
    assert output['message'] == "Input was invalid"


def _check_package(package):
    assert "package" in package
    assert package["package"] in set(["package1", "package2"])


def _check_license(package):
    assert "license" in package
    assert package["license"] in set(["license1", "license2"])


def test_extract_component_details():
    """Test the extract_component_details method."""
    component_details = stack_license_analyzer.extract_component_details({})
    assert "ecosystem" in component_details
    assert "name" in component_details
    assert "version" in component_details
    assert "licenses" in component_details
    assert component_details["ecosystem"] == ""
    assert component_details["name"] == ""
    assert component_details["version"] == ""
    assert component_details["licenses"] == []

    component = {
        "version": {
            "declared_licenses": ["license1"],
            "pname": ["The package"],
            "version": ["1.0.0"],
            "pecosystem": ["Maven"]
        }
    }
    component_details = stack_license_analyzer.extract_component_details(component)
    assert "ecosystem" in component_details
    assert "name" in component_details
    assert "version" in component_details
    assert "licenses" in component_details
    assert component_details["ecosystem"] == "Maven"
    assert component_details["name"] == "The package"
    assert component_details["version"] == "1.0.0"
    assert component_details["licenses"] == ["license1"]


def test_extract_license_outliers():
    """Test the _extract_license_outliers method."""
    license_outliers = stack_license_analyzer._extract_license_outliers(None)
    assert license_outliers == []

    data = {
        "outlier_packages": {
            "package1": "license1",
            "package2": "license2"
        }
    }
    license_outliers = stack_license_analyzer._extract_license_outliers(data)
    assert license_outliers is not None
    assert len(license_outliers) == 2
    p1 = license_outliers[0]
    p2 = license_outliers[1]
    _check_license(p1)
    _check_license(p2)
    _check_package(p1)
    _check_package(p2)


class _gremlin_response:

    def __init__(self, status_code, ok, json):
        self.status_code = status_code
        self.ok = ok
        self._json = json

    def post(self, url, data):
        assert url
        assert data
        return self

    def json(self):
        return self._json


def mocked_get_session_retry():
    """Implement mocked function get_session_retry()."""
    return _gremlin_response(200, True, "")


RESOLVED_PACKAGES = [
    {"package": "The package",
     "version": "1.0.0"},
    {"package": None,
     "version": "1.0.0"},
    {"package": "The package 2",
     "version": None}
]


@patch('src.stack_license.get_session_retry', side_effect=mocked_get_session_retry)
def test_get_depencency_data(_mock_get_session_retry):
    """Test the get_dependency_data method."""
    resolved = RESOLVED_PACKAGES
    depencency_data = stack_license_analyzer.get_dependency_data(resolved, "Maven")
    assert depencency_data is not None
    assert "result" in depencency_data
    assert depencency_data["result"] == []


def mocked_get_session_retry2():
    """Implement mocked function get_session_retry()."""
    return _gremlin_response(404, False, "")


@patch('src.stack_license.get_session_retry', side_effect=mocked_get_session_retry2)
def test_get_depencency_data2(_mock_get_session_retry):
    """Test the get_dependency_data method."""
    resolved = RESOLVED_PACKAGES
    depencency_data = stack_license_analyzer.get_dependency_data(resolved, "Maven")
    assert depencency_data is not None
    assert "result" in depencency_data
    assert depencency_data["result"] == []


def mocked_get_session_retry3():
    """Implement mocked function get_session_retry()."""
    result = {
        "result": {
            "data": []
         }
    }
    return _gremlin_response(200, True, result)


@patch('src.stack_license.get_session_retry', side_effect=mocked_get_session_retry3)
def test_get_depencency_data3(_mock_get_session_retry):
    """Test the get_dependency_data method."""
    resolved = RESOLVED_PACKAGES
    depencency_data = stack_license_analyzer.get_dependency_data(resolved, "Maven")
    assert depencency_data is not None
    assert "result" in depencency_data
    assert depencency_data["result"] == []


def mocked_get_session_retry4():
    """Implement mocked function get_session_retry()."""
    result = {
        "result": {
            "data": ["this is fake result"]
         }
    }
    return _gremlin_response(200, True, result)


@patch('src.stack_license.get_session_retry', side_effect=mocked_get_session_retry4)
def test_get_depencency_data4(_mock_get_session_retry):
    """Test the get_dependency_data method."""
    resolved = RESOLVED_PACKAGES
    depencency_data = stack_license_analyzer.get_dependency_data(resolved, "Maven")
    assert depencency_data is not None
    assert "result" in depencency_data
    assert "data" in depencency_data["result"][0]


def mocked_get_session_retry5():
    """Implement mocked function get_session_retry()."""
    raise Exception("something wrong happened")


@patch('src.stack_license.get_session_retry', side_effect=mocked_get_session_retry5)
def test_get_depencency_data5(_mock_get_session_retry):
    """Test the get_dependency_data method."""
    resolved = RESOLVED_PACKAGES
    depencency_data = stack_license_analyzer.get_dependency_data(resolved, "Maven")
    assert depencency_data is not None
    assert depencency_data is not None
    assert "result" in depencency_data
    assert depencency_data["result"] == []


def mocked_get_session_retry6():
    """Implement mocked function get_session_retry()."""
    result = {
        "result": {
            "data": [{
                "version": {
                    "declared_licenses": ["license1"],
                    "pname": ["The package"],
                    "version": ["1.0.0"],
                    "pecosystem": ["Maven"]
                }}]
         }
    }
    return _gremlin_response(200, True, result)


@patch('src.stack_license.get_session_retry', side_effect=mocked_get_session_retry6)
def test_extract_user_stack_package_licenses(_mock_get_session_retry):
    """Test the extract_user_stack_package_licenses method."""
    resolved = RESOLVED_PACKAGES
    resolved = [
        {"package": "The package",
         "version": "1.0.0"},
        {"package": "The package",
         "version": "2.0.0"},
    ]

    depencency_data = stack_license_analyzer.extract_user_stack_package_licenses(resolved, "Maven")
    assert depencency_data is not None
    dependencies = len(depencency_data)
    assert dependencies == 2

    for i in range(0, dependencies):
        d = depencency_data[0]
        # package check
        assert "package" in d
        assert d["package"] == "The package"
        # licence check
        assert "licenses" in d
        assert len(d["licenses"]) == 1
        assert d["licenses"][0] == "license1"


def test_convert_version_to_proper_semantic():
    """Test the convert_version_to_proper_semantic function."""
    versions = [
        ["1", "1"],
        ["1.2", "1.2"],
        ["1.2.3", "1.2.3"],
        ["1.2.3.4", "1.2.3-4"],
        ["1-2", "1.2"],
        ["1-2-3", "1.2.3"],
        ["1-2-3-4", "1.2.3-4"],
        ["1-2-3-beta", "1.2.3-beta"],
    ]

    for version in versions:
        input = version[0]
        expected = version[1]
        assert convert_version_to_proper_semantic(input) == expected


def test_select_latest_version():
    """Test the select_latest_version function."""
    assert select_latest_version() == "0.0.0"
    assert select_latest_version(input_version="1.0.0") == ""
    assert select_latest_version(input_version="1.0.0", anitya="1.0.0") == "1.0.0"
    assert select_latest_version(input_version="1.0.0", libio="1.0.0") == "1.0.0"

    # error handling
    assert select_latest_version(input_version="") == ""
    assert select_latest_version(anitya="") == ""
    assert select_latest_version(libio="") == ""
