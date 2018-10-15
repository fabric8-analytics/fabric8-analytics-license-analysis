"""Class representing stack license analyzer."""

import os
import requests
import json
import flask

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from src.license_analysis import LicenseAnalyzer
import logging
import traceback
import semantic_version as sv
from src.config import DATA_DIR
from src.utils import http_error
from src.util.data_store.local_filesystem import LocalFileSystem

_logger = logging.getLogger(__name__)

possible_affected_licenses = ["GNU Lesser General Public License", "Version 2.1", "Version 1.1",
                              "Apache Software License", "The Apache Software License",
                              "Eclipse Public License", "Version 1.0", "Version 2.0",
                              "Mozilla Public License", "Apache License", "version 2.0",
                              "GNU General Public License", "Version 3", "Version 2",
                              "GNU Affero General Public License", "The Apache License",
                              "The GNU Lesser General Public License", "version 3",
                              "The GNU General Public License"]


def get_session_retry(retries=3, backoff_factor=0.2, status_forcelist=(404, 500, 502, 504),
                      session=None):
    """Set HTTP Adapter with retries to session."""
    session = session or requests.Session()
    retry = Retry(total=retries, read=retries, connect=retries,
                  backoff_factor=backoff_factor, status_forcelist=status_forcelist)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    return session


def convert_version_to_proper_semantic(version):
    """Needed for maven version correction."""
    version = version.replace('.', '-', 3)
    version = version.replace('-', '.', 2)
    return version


def filter_incorrect_splitting(package_licenses):
    """Filter incorrect splitting of license."""
    affected_licenses = list(set(package_licenses) & set(possible_affected_licenses))
    affected_licenses = sorted(affected_licenses)
    assert len(affected_licenses) == 2
    package_licenses = list(set(package_licenses) - set(affected_licenses))
    package_licenses.append(affected_licenses[0] + ', ' + affected_licenses[1])

    return package_licenses


def select_latest_version(input_version='0.0.0', libio='0.0.0', anitya='0.0.0'):
    """Return the latest version of packages."""
    libio_latest_version = convert_version_to_proper_semantic(libio)
    anitya_latest_version = convert_version_to_proper_semantic(anitya)
    input_version = convert_version_to_proper_semantic(input_version)

    try:
        latest_version = libio_latest_version
        return_version = libio
        if sv.SpecItem('<' + anitya_latest_version).match(sv.Version(libio_latest_version)):
            latest_version = anitya_latest_version
            return_version = anitya
        if sv.SpecItem('<' + input_version).match(sv.Version(latest_version)):
            # User provided version is higher. Do not show the latest version in the UI
            return_version = ''
    except ValueError:
        # In case of failure let's not show any latest version at all
        return_version = ''
        pass

    return return_version


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

    def get_outlier_packages(self, la_output, dict_lic_pkgs):
        """Get outlier packages."""
        if len(la_output['outlier_licenses']) > 0:
            outlier_pkg = {}
            for lic in la_output['outlier_licenses']:
                for pkg in dict_lic_pkgs[lic]:
                    outlier_pkg[pkg] = lic
            return outlier_pkg
        else:
            return {}

    def get_conflict_packages(self, la_output, dict_lic_pkgs):
        """Get conflict packages."""
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
        return list_conflict_pkg

    # TODO needs refactoring
    # TODO: reduce cyclomatic complexity
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
        if not payload or not payload.get('packages') or type(payload.get('packages')) != list:
            output = {
                'status': 'Failure',
                'message': 'Input was invalid'
            }
            logging.debug("stack license analysis input is invalid")
            return output

        for pkg in payload['packages']:
            if pkg.get('package') is None or pkg.get('version') is None:
                output = {
                    'status': 'Failure',
                    'message': 'Either component name or component version is missing'
                }
                return output
        # payload = filter_incorrect_splitting(payload)
        output = payload  # output info will be inserted inside payload structure
        count_comp_no_license = 0  # keep track of number of component with no license
        output['conflict_packages'] = []
        output['outlier_packages'] = {}
        output['distinct_licenses'] = []

        synonyms_dir = os.path.join(DATA_DIR, "synonyms")
        synonyms_store = LocalFileSystem(src_dir=synonyms_dir)
        list_synonym_jsons = synonyms_store.list_files()
        for synonym_json in list_synonym_jsons:
            syn = synonyms_store.read_json_file(synonym_json)
            break
        for pkg in output['packages']:
            if not pkg['licenses']:
                output['packages'].remove(pkg)
        try:
            # First, let us try to compute representative license for each component
            list_comp_rep_licenses = []
            distinct_licenses = set()
            is_stack_license_possible = True
            for pkg in output['packages']:
                list_of_licenses = []
                for license in pkg.get('licenses', []):
                    if license.startswith('version') or license.startswith('Version'):
                        pkg['licenses'] = filter_incorrect_splitting(pkg['licenses'])
                        break
                la_output = self.license_analyzer.compute_representative_license(
                    pkg.get('licenses', []))
                for lic in pkg.get('licenses', []):
                    s = syn.get(lic)
                    if s:
                        list_of_licenses.append(s)
                        distinct_licenses.add(s)
                    else:
                        list_of_licenses.append(lic)
                        distinct_licenses.add(lic)

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
                    output['message'] = 'Cannot calculate stack license due to unknown' \
                                        'dependencies or license not supported.'
                    is_stack_license_possible = False
                elif la_output['status'] == 'Conflict':
                    output['status'] = 'ComponentConflict'
                    output['message'] = 'Cannot calculate stack license due to component' \
                                        ' conflict.'
                    is_stack_license_possible = False
                elif la_output['status'] == 'Unknown':
                    output['status'] = 'Unknown'
                    output['message'] = 'Cannot calculate stack license due to unknown' \
                                        'dependencies or license not supported.'
                    is_stack_license_possible = False

                if la_output['representative_license'] is None:
                    # This will later indicate that no need to compute stack license
                    is_stack_license_possible = False
                else:
                    list_comp_rep_licenses.append(la_output['representative_license'])
            output['distinct_licenses'] = output['distinct_licenses'] + \
                list(distinct_licenses)
            # Return if we could not compute license for some component
            if is_stack_license_possible is False:
                # output['status'] should have been set already
                output['stack_license'] = None
                return output

            # INFO: the following check is not necessary because the control
            # flow newer reach to this block

            # If there is no component license then something unexpected happened
            # if len(list_comp_rep_licenses) == 0:
            #    output['status'] = 'Failure'
            #    output['stack_license'] = None
            #    output['message'] = "Something weird happened!"
            #    return output

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
                output['conflict_packages'] = self.get_conflict_packages(la_output, dict_lic_pkgs)
                output['status'] = 'StackConflict'
                output['message'] = 'Cannot calculate stack license due to stack conflict.'

            output['outlier_packages'] = self.get_outlier_packages(la_output, dict_lic_pkgs)

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

    def extract_component_details(self, component):
        """Extract component details."""
        licenses = component.get("version", {}).get("declared_licenses", [])
        name = component.get("version", {}).get("pname", [""])[0]
        version = component.get("version", {}).get("version", [""])[0]
        ecosystem = component.get("version", {}).get("pecosystem", [""])[0]
        component_summary = {
            "ecosystem": ecosystem,
            "name": name,
            "version": version,
            "licenses": licenses
        }

        return component_summary

    def get_dependency_data(self, resolved, ecosystem):
        """Get packages data form graph DB."""
        result = []
        URL = "http://{host}:{port}".format(
            host=os.environ.get("BAYESIAN_GREMLIN_HTTP_SERVICE_HOST", "localhost"),
            port=os.environ.get("BAYESIAN_GREMLIN_HTTP_SERVICE_PORT", "8182"))
        for elem in resolved:
            if elem["package"] is None or elem["version"] is None:
                _logger.warning("Either component name or component version is missing")
                continue
            qstring = \
                "g.V().has('pecosystem', '{}').has('pname', '{}').has('version', '{}')"\
                .format(ecosystem, elem["package"], elem["version"]) + \
                ".as('version').in('has_version').as('package')" + \
                ".select('version','package').by(valueMap());"

            # qstring = \
            #     "g.V().has('pecosystem', '{}').has('pname', '{}').has('version', '{}')" \
            #         .format(ecosystem, elem["package"], elem["version"]) + \
            #     ".valueMap('pecosystem', 'pname', 'version', 'declared_licenses')"
            payload = {'gremlin': qstring}

            try:
                graph_req = get_session_retry().post(URL, data=json.dumps(payload))

                if graph_req.status_code == 200:
                    graph_resp = graph_req.json()
                    if 'result' not in graph_resp:
                        continue
                    if len(graph_resp['result']['data']) == 0:
                        continue

                    result.append(graph_resp["result"])
                else:
                    _logger.error("Failed retrieving dependency data.")
                    continue
            except Exception:
                _logger.exception("Error retrieving dependency data!")
                continue

        return {"result": result}

    def extract_user_stack_package_licenses(self, resolved, ecosystem):
        """Extract packages details from graph result."""
        user_stack = self.get_dependency_data(resolved, ecosystem)
        list_package_licenses = []
        if user_stack is not None:
            for component in user_stack.get('result', []):
                data = component.get("data", None)
                if data:
                    component_data = self.extract_component_details(data[0])
                    license_scoring_input = {
                        'package': component_data['name'],
                        'version': component_data['version'],
                        'licenses': component_data['licenses']
                    }
                    list_package_licenses.append(license_scoring_input)
        analyzed_pkg = [x.get('package') for x in list_package_licenses]
        for pk in resolved:
            if not pk.get('licenses'):
                pk.update({'licenses': list()})
            if pk.get('package') not in analyzed_pkg:
                list_package_licenses.append(pk)

        return list_package_licenses

    def _extract_conflict_packages(self, license_service_output):
        """
        Extract conflict packages from response.

        It returns a list of pairs of packages whose licenses are in conflict.
        Note that this information is only available when each component license
        was identified ( i.e. no unknown and no component level conflict ) and
        there was a stack level license conflict.

        :param license_service_output: output of license analysis REST service
        :return: list of pairs of packages whose licenses are in conflict
        """
        license_conflict_packages = []
        if not license_service_output:
            return license_conflict_packages

        conflict_packages = license_service_output.get('conflict_packages', [])
        for conflict_pair in conflict_packages:
            list_pkgs = list(conflict_pair.keys())
            assert len(list_pkgs) == 2
            d = {
                "package1": list_pkgs[0],
                "license1": conflict_pair[list_pkgs[0]],
                "package2": list_pkgs[1],
                "license2": conflict_pair[list_pkgs[1]]
            }
            license_conflict_packages.append(d)

        return license_conflict_packages

    def _extract_unknown_licenses(self, license_service_output):
        """
        Extract unknown licenses from response.

        At the moment, there are two types of unknowns:

        a. really unknown licenses: those licenses, which are not understood by our system.
        b. component level conflicting licenses: if a component has multiple licenses
            associated then license analysis service tries to identify a representative
            license for this component. If some licenses are in conflict, then its
            representative license cannot be identified and this is another type of
            'unknown' !

        This function returns both types of unknown licenses.

        :param license_service_output: output of license analysis REST service
        :return: list of packages with unknown licenses and/or conflicting licenses
        """
        really_unknown_licenses = []
        lic_conflict_licenses = []
        if not license_service_output:
            return really_unknown_licenses

        if license_service_output.get('status', '') == 'Unknown':
            list_components = license_service_output.get('packages', [])
            for comp in list_components:
                license_analysis = comp.get('license_analysis', {})
                if license_analysis.get('status', '') == 'Unknown':
                    pkg = comp.get('package', 'Unknown')
                    comp_unknown_licenses = license_analysis.get('unknown_licenses', [])
                    for lic in comp_unknown_licenses:
                        really_unknown_licenses.append({
                            'package': pkg,
                            'license': lic
                        })

        if license_service_output.get('status', '') == 'ComponentLicenseConflict':
            list_components = license_service_output.get('packages', [])
            for comp in list_components:
                license_analysis = comp.get('license_analysis', {})
                if license_analysis.get('status', '') == 'Conflict':
                    pkg = comp.get('package', 'Unknown')
                    d = {
                        "package": pkg
                    }
                    comp_conflict_licenses = license_analysis.get('conflict_licenses', [])
                    list_conflicting_pairs = []
                    for pair in comp_conflict_licenses:
                        assert (len(pair) == 2)
                        list_conflicting_pairs.append({
                            'license1': pair[0],
                            'license2': pair[1]
                        })
                    d['conflict_licenses'] = list_conflicting_pairs
                    lic_conflict_licenses.append(d)

        output = {
            'really_unknown': really_unknown_licenses,
            'component_conflict': lic_conflict_licenses
        }
        return output

    def _extract_license_outliers(self, license_service_output):
        """
        Extract outliers from response.

        :param license_service_output: output of license analysis REST service
        :return: list of license outlier packages
        """
        outliers = []
        if not license_service_output:
            return outliers

        outlier_packages = license_service_output.get('outlier_packages', {})
        for pkg in outlier_packages.keys():
            outliers.append({
                'package': pkg,
                'license': outlier_packages.get(pkg, 'Unknown')
            })

        return outliers

    def license_recommender(self, input):
        """
        Perform a detailed license analysis for the given list of packages.

        It first identifies representative license for each package. Then, it
        computes representative license for the entire stack itself.

        If there is any unknown license, this function will give up.

        If there is any conflict then it returns pairs of conflicting licenses.

        If a representative stack-license is possible, then it tries to identify
        license based outlier packages.

        :param payload: Input list of package information
        :return: Detailed license analysis output
        """
        if input.get('_resolved') is None or input.get('ecosystem') is None:
            return http_error("Either list of packages or ecosystem value is missing "
                              "from payload"), 400

        else:
            for pkg in input.get('_resolved'):
                if pkg.get('package') is None or pkg.get('version') is None:
                    return http_error("Either component name or component version is missing "
                                      "from payload"), 400
            resolved = input['_resolved']
            ecosystem = input['ecosystem']
            user_stack_packages = self.extract_user_stack_package_licenses(resolved, ecosystem)
            payload = {
                "packages": user_stack_packages
            }
            resp = self.compute_stack_license(payload=payload)
            output = resp
            output['conflict_packages'] = self._extract_conflict_packages(resp)
            output['outlier_packages'] = self._extract_license_outliers(resp)
            output['unknown_licenses'] = self._extract_unknown_licenses(resp)

            return flask.jsonify(output)
