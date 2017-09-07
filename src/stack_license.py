import os

from src.license_analysis import LicenseAnalyzer
import logging
import traceback

from src import config
from src.util.data_store.local_filesystem import LocalFileSystem


def compute_stack_license(payload):
    """
    Function to perform a detailed license analysis for the given list of
    packages.

    It first identifies representative license for each package. Then, it
    computes representative license for the entire stack itself.

    If there is any unknown license, this function will give up.

    If there is any conflict then it returns pairs of conflicting licenses.

    If a representative stack-license is possible, then it tries to identify
    license based outlier packages.

    :param payload: Input list of package information
    :return: Detailed license analysis output
    """
    output = payload  # output info will be inserted inside payload structure
    output['conflict_packages'] = []
    output['outlier_packages'] = {}

    try:
        # Check input
        if payload is None or len(payload['packages']) == 0:
            output['status'] = 'Failure'
            output['message'] = 'Input was invalid'
            logging.debug("stack license analysis input is invalid")
            return output

        # Data store where license graph is available
        src_dir = os.path.join(config.DATA_DIR, "license_graph")
        graph_store = LocalFileSystem(src_dir=src_dir)
        synonyms_dir = os.path.join(config.DATA_DIR, "synonyms")
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
                'conflict_licenses': la_output['conflict_licenses'],
                'unknown_licenses': la_output['unknown_licenses'],
                'outlier_licenses': la_output['outlier_licenses'],
                'synonyms': la_output['synonyms'],
                '_message': la_output['reason']
            }

            if la_output['status'] == 'Conflict':
                output['status'] = 'ComponentLicenseConflict'
                is_stack_license_possible = False
            elif la_output['status'] == 'Unknown':
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

        # Prepare a map of license -> package, which is used later to prepare output
        assert(len(output['packages']) == len(list_comp_rep_licenses))
        dict_lic_pkg = {}
        for i, lic in enumerate(list_comp_rep_licenses):
            pkg = output['packages'][i]
            dict_lic_pkg[lic] = pkg.get('package', 'unknown_package')

        # If we reach here, then that means we are all set to compute stack license !
        la_output = license_analyzer.compute_representative_license(list_comp_rep_licenses)
        output['status'] = la_output['status']
        output['stack_license'] = la_output['representative_license']

        if la_output['status'] == 'Conflict':
            list_conflict_lic = la_output['conflict_licenses']
            list_conflict_pkg = []
            for lic_tuple in list_conflict_lic:
                pkg_group = {
                    dict_lic_pkg[lic_tuple[0]]: lic_tuple[0],
                    dict_lic_pkg[lic_tuple[1]]: lic_tuple[1]
                }
                list_conflict_pkg.append(pkg_group)
            output['conflict_packages'] = list_conflict_pkg
            output['status'] = 'StackLicenseConflict'

        if (len(la_output['outlier_licenses'])) > 0:
            outlier_pkg = {}
            for lic in la_output['outlier_licenses']:
                outlier_pkg[dict_lic_pkg[lic]] = lic
            output['outlier_packages'] = outlier_pkg
        else:
            output['outlier_packages'] = {}

    except:  # TODO custom exceptions
        output['status'] = 'Failure'
        output['stack_license'] = None
        output['message'] = "Some unexpected exception happened!"
        msg = traceback.format_exc()
        logging.error("Unexpected error happened!\n{}".format(msg))

    return output
