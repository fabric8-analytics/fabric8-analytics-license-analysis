# fabric8-analytics-license-analysis
License Analysis Service analyzes the given stack and returns the following:
 - unknown licenses, if any
 - conflicting licenses, if any
 - license based outlier packages, if any
 - stack level license, if possible


## How to test locally:

*  `./run-test-local.sh`

    * To run with different threshold `./run-test-local.sh -t <[0-1]>`


## How to run the API locally:

* `./run-api-local.sh`

    * To run on different port `./run-api-local.sh -p <Port>`

    * To run with different threshold `./run-test-local.sh -t <[0-1]>`

    * To run with different port and threshold `./run-api-local.sh -p <Port> -t <[0-1]>`

* curl localhost:<SERVICE_PORT> should return `{status: ok}`


## Notes:

* By default the value of `MAJORITY_THRESHOLD` used is 0.6. If you wish to use any other value, modifications in the test cases will be required to reflect the new outliers.

* To run tests the the value of `DATA_DIR` is set to `.`

* To run the API locally the value of `DATA_DIR` is to `tests


## Sample License analysis request input
```
ENDPOINT: /api/vi/stack_license
BODY: JSON data
[
    "packages": [
            {
                "package": "p1",
                "version": "1.1",
                "licenses": ["APACHE", "EPL 1.0"]
            }
        ]
]
```
