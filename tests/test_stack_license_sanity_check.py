"""Unit tests for the StackLicenseAnalyzer module."""

from src.stack_license import StackLicenseAnalyzer


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
