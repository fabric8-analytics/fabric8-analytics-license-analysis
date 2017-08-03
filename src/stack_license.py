from license_analysis import LicenseAnalyzer


def compute_stack_license(payload):
    if payload is None:
        return None
    if len(payload['packages']) == 0:
        return None

    output = payload  # output info will be inserted inside payload structure
    output['status'] = 'Successful'
    output['conflict_packages'] = {}  # place holder for future
    list_comp_rep_licenses = []
    is_stack_license_possible = True

    # First, let us try to compute representative license for each component
    license_analyzer = LicenseAnalyzer()
    for pkg in output['packages']:
        la_output = license_analyzer.compute_representative_license(pkg.get('licenses', []))

        pkg['license'] = {
            'status': la_output['status'],
            '_representative_licenses': la_output['representative_license'],
            'conflict_licenses': [], # place holder for future
            'unknown_licenses': [] # place holder for future
        }

        if la_output['status'] is 'Conflict':
            output['status'] = 'ComponentLicenseConflict'
            is_stack_license_possible = False
        elif la_output['status'] is 'Unknown':
            output['status'] = 'Unknown'
            is_stack_license_possible = False

        if la_output['representative_license'] is None:
            # This will later indicate that no need to compute stack license
            is_stack_license_possible = False
        else:
            list_comp_rep_licenses.append(la_output['representative_license'])

    # Return if we could not compute license for some component
    if is_stack_license_possible is False:
        output['stack_license'] = None
        return output

    # If status is still successful and there is no component license then
    # something unexpected happened
    if len(list_comp_rep_licenses) == 0:
        output['status'] = 'Failure'
        output['stack_license'] = None

    # If we reach here, then that means we are all set to compute stack license !
    la_output = license_analyzer.compute_representative_license(list_comp_rep_licenses)
    output['status'] = la_output['status']
    output['stack_license'] = la_output['representative_license']
    if la_output['status'] is 'Conflict':
        output['status'] = 'StackLicenseConflict'

    return output
