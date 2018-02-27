"""Class representing stack license analyzer."""

import os

from src.license_analysis import LicenseAnalyzer
import logging
import traceback

from src.config import DATA_DIR
from src.util.data_store.local_filesystem import LocalFileSystem


class StackLicenseAnalyzer(object):
    """Class representing stack license analyzer."""

    def __init__(self):
        """Initialize stack license analyzer."""
        # Data store where license graph is available
        src_dir = os.path.join(DATA_DIR, "license_graph")
        graph_store = LocalFileSystem(src_dir=src_dir)
        synonyms_dir = os.path.join(DATA_DIR, "synonyms")
        synonyms_store = LocalFileSystem(src_dir=synonyms_dir)

        self.license_analyzer = LicenseAnalyzer(graph_store, synonyms_store)

    def _check_compatibility(self, stack_license, other_packages):
        list_comp_rep_licenses = []
        map_lic2pkg = {}
        unknown_license_packages = []
        conflict_packages = []
        compatible_packages = []
        for pkg in other_packages:
            la_output = self.license_analyzer.compute_representative_license(
                pkg.get('licenses', []))

            pkg['license_analysis'] = {
                'status': la_output['status'],
                '_representative_licenses': la_output['representative_license'],
                'conflict_licenses': la_output['conflict_licenses'],
                'unknown_licenses': la_output['unknown_licenses'],
                'outlier_licenses': la_output['outlier_licenses'],
                'synonyms': la_output['synonyms'],
                '_message': la_output['reason']
            }

            if la_output['status'] == 'Successful':
                pkg_license = la_output['representative_license']
                list_comp_rep_licenses.append(pkg_license)

                list_pkg = map_lic2pkg.get(pkg_license, [])
                list_pkg.append(pkg.get('package', 'unknown_package'))
                map_lic2pkg[pkg_license] = list_pkg
            else:
                unknown_license_packages.append(pkg.get('package', 'unknown_name'))

        # deduplicate
        list_comp_rep_licenses = list(set(list_comp_rep_licenses))
        for k, v in map_lic2pkg.items():
            map_lic2pkg[k] = list(set(v))

        compatibility_output = self.license_analyzer.check_compatibility(
            lic_a=stack_license, list_lic_b=list_comp_rep_licenses)

        # now, map license to packages
        assert len(compatibility_output['unknown_licenses']) == 0

        for lic in compatibility_output['conflict_licenses']:
            conflict_packages += map_lic2pkg[lic]

        for list_lic in compatibility_output['compatible_licenses']:
            list_packages = []
            for lic in list_lic:
                list_packages += map_lic2pkg[lic]
            compatible_packages += list_packages

        output = {
            'unknown_license_packages': unknown_license_packages,
            'conflict_packages': conflict_packages,
            'compatible_packages': compatible_packages
        }
        return output

    # TODO needs refactoring
    def compute_stack_license(self, payload):
        """Perform a detailed license analysis for the given list of packages.

        It first identifies representative license for each package. Then, it
        computes representative license for the entire stack itself.

        If there is any unknown license, this function will give up.

        If there is any conflict then it returns pairs of conflicting licenses.

        If a representative stack-license is possible, then it tries to identify
        license based outlier packages.

        :param payload: Input list of package information
        :return: Detailed license analysis output
        """
        # check input
        if not payload or not payload.get('packages'):
            output = {
                'status': 'Failure',
                'message': 'Input was invalid'
            }
            logging.debug("stack license analysis input is invalid")
            return output

        output = payload  # output info will be inserted inside payload structure
        count_comp_no_license = 0  # keep track of number of component with no license
        output['conflict_packages'] = []
        output['outlier_packages'] = {}

        try:
            # First, let us try to compute representative license for each component
            list_comp_rep_licenses = []
            is_stack_license_possible = True
            for pkg in output['packages']:
                la_output = self.license_analyzer.compute_representative_license(
                    pkg.get('licenses', []))

                pkg['license_analysis'] = {
                    'status': la_output['status'],
                    '_representative_licenses': la_output['representative_license'],
                    'conflict_licenses': la_output['conflict_licenses'],
                    'unknown_licenses': la_output['unknown_licenses'],
                    'outlier_licenses': la_output['outlier_licenses'],
                    'synonyms': la_output['synonyms'],
                    '_message': la_output['reason']
                }

                if la_output['status'] == 'Failure':
                    count_comp_no_license = count_comp_no_license + 1
                    output['status'] = 'Failure'
                    is_stack_license_possible = False
                elif la_output['status'] == 'Conflict':
                    output['status'] = 'ComponentConflict'
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
                output['message'] = "No declared licenses found for {} component(s).". \
                    format(count_comp_no_license)
                return output

            # If there is no component license then something unexpected happened
            if len(list_comp_rep_licenses) == 0:
                output['status'] = 'Failure'
                output['stack_license'] = None
                output['message'] = "Something weird happened!"

            # Prepare a map of license -> package, which is used later to prepare output
            assert (len(output['packages']) == len(list_comp_rep_licenses))
            dict_lic_pkgs = {}
            for i, lic in enumerate(list_comp_rep_licenses):
                pkg = output['packages'][i]
                list_pkg = dict_lic_pkgs.get(lic, [])
                list_pkg.append(pkg.get('package', 'unknown_package'))
                dict_lic_pkgs[lic] = list_pkg

            for lic, value_list in dict_lic_pkgs.items():
                dict_lic_pkgs[lic] = list(set(value_list))

            # If we reach here, then that means we are all set to compute stack license !
            la_output = self.license_analyzer.compute_representative_license(list_comp_rep_licenses)
            output['status'] = la_output['status']
            output['stack_license'] = la_output['representative_license']

            if la_output['status'] == 'Conflict':
                list_conflict_lic = la_output['conflict_licenses']
                list_conflict_pkg = []
                for lic1, lic2 in list_conflict_lic:
                    for pkg1 in dict_lic_pkgs[lic1]:
                        for pkg2 in dict_lic_pkgs[lic2]:
                            pkg_group = {
                                pkg1: lic1,
                                pkg2: lic2
                            }
                            list_conflict_pkg.append(pkg_group)
                output['conflict_packages'] = list_conflict_pkg
                output['status'] = 'StackConflict'

            if (len(la_output['outlier_licenses'])) > 0:
                outlier_pkg = {}
                for lic in la_output['outlier_licenses']:
                    for pkg in dict_lic_pkgs[lic]:
                        outlier_pkg[pkg] = lic
                output['outlier_packages'] = outlier_pkg
            else:
                output['outlier_packages'] = {}

            # Analyze further and generate info for license filters
            # let us try to compute representative license for each alternate component
            if la_output['status'] == 'Successful':
                lic_filter_for_alt = self._check_compatibility(output['stack_license'],
                                                               output.get('alternate_packages', []))

                lic_filter_for_com = self._check_compatibility(output['stack_license'],
                                                               output.get('companion_packages', []))

                output['license_filter'] = {
                    'alternate_packages': lic_filter_for_alt,
                    'companion_packages': lic_filter_for_com
                }

        except Exception:  # TODO custom exceptions
            output['status'] = 'Failure'
            output['stack_license'] = None
            output['message'] = "Some unexpected exception happened!"
            msg = traceback.format_exc()
            logging.error("Unexpected error happened!\n{}".format(msg))

        return output
