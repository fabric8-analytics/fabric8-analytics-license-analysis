# fabric8-analytics-license-analysis
License Analysis Service analyzes the given stack and returns the following:
 - unknown licenses, if any
 - conflicting licenses, if any
 - license based outlier packages, if any
 - stack level license, if possible

## How to run the API locally:

* Set the value of `MAJORITY_THRESHOLD` and `SERVICE_PORT` in the env.

* set export PYTHONPATH=`pwd`/src

* gunicorn -b 0.0.0.0:$SERVICE_PORT rest_api:app

* curl localhost:<SERVICE_PORT> returns `{status: ok}`


## How to test locally:

* Set the value of `MAJORITY_THRESHOLD` in the env.

* `cp src/config.py.template src/config.py`

*  `cd tests`

*  `pytest . -v`


Notes: 

* By default the value of `MAJORITY_THRESHOLD` used is 0.6. If you wish to use any other value, modifications in the test cases will be required to reflect the new outliers.

* For running tests set the the value of `DATA_DIR` to `.`

* For running the API locally set the value of `DATA_DIR` to `tests`