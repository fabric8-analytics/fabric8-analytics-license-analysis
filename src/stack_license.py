from license_analysis import LicenseAnalyzer
import logging
import traceback

from util.data_store.local_filesystem import LocalFileSystem


def compute_stack_license(payload):
    output = payload  # output info will be inserted inside payload structure
    output['conflict_packages'] = {}  # place holder for future

    try:
        # Check input
        if payload is None or len(payload['packages']) == 0:
            output['status'] = 'Failure'
            output['message'] = 'Input was invalid'
            logging.debug("stack license analysis input is invalid")
            return output

        # Data store where license graph is available
        src_dir = "/Users/hmistry/work/license_analysis/src/fabric8-analytics-license-analysis/tests/license_graph"
        graph_store = LocalFileSystem(src_dir=src_dir)
        synonyms_dir = "/Users/hmistry/work/license_analysis/src/fabric8-analytics-license-analysis/tests/synonyms"
        synonyms_store = LocalFileSystem(src_dir=synonyms_dir)

        # First, let us try to compute representative license for each component
        license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)
        list_comp_rep_licenses = []
        is_stack_license_possible = True
        for pkg in output['packages']:
            la_output = license_analyzer.compute_representative_license(pkg.get('licenses', []))

            pkg['license_analysis'] = {
                'status': la_output['status'],
                '_representative_licenses': la_output['representative_license'],
                'conflict_licenses': [], # place holder for future
                'unknown_licenses': [], # place holder for future
                '_message': la_output['reason']
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
            # output['status'] should have been set already
            output['stack_license'] = None
            output['message'] = "Component license not available. Cannot compute stack license."
            return output

        # If there is no component license then something unexpected happened
        if len(list_comp_rep_licenses) == 0:
            output['status'] = 'Failure'
            output['stack_license'] = None
            output['message'] = "Something weird happened!"

        # If we reach here, then that means we are all set to compute stack license !
        la_output = license_analyzer.compute_representative_license(list_comp_rep_licenses)
        output['status'] = la_output['status']
        output['stack_license'] = la_output['representative_license']
        if la_output['status'] is 'Conflict':
            output['status'] = 'StackLicenseConflict'

    except:  # TODO custom exceptions
        output['status'] = 'Failure'
        output['stack_license'] = None
        output['message'] = "Some unexpected exception happened!"
        msg = traceback.format_exc()
        logging.error("Unexpected error happened!\n{}".format(msg))

    return output
