[![Build Status](https://ci.centos.org/buildStatus/icon?job=devtools-fabric8-analytics-license-analysis-f8a-build-master)](https://ci.centos.org/job/devtools-fabric8-analytics-license-analysis-f8a-build-master/)

# fabric8-analytics-license-analysis
License Analysis Service analyzes the given stack and returns the following:
 - unknown licenses, if any
 - conflicting licenses, if any
 - license based outlier packages, if any
 - stack level license, if possible

# Test
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
{
    "packages": [
            {
                "package": "p1",
                "version": "1.1",
                "licenses": ["APACHE", "EPL 1.0"]
            }
        ]
}
```


## Tree used for license comparison

![License Diagram](https://user-images.githubusercontent.com/37098367/99516035-bc4d4f00-29b3-11eb-9d01-0d26dbe948d9.png)

### References:

* [The Free-Libre / Open Source Software (FLOSS) License Slide  by by David A. Wheeler](https://www.dwheeler.com/essays/floss-license-slide.pdf)

### Footnotes

#### Check for all possible issues

The script named `check-all.sh` is to be used to check the sources for all detectable errors and issues. This script can be run w/o any arguments:

```
./check-all.sh
```

Expected script output:

```
Running all tests and checkers
  Check all BASH scripts
    OK
  Check documentation strings in all Python source file
    OK
  Detect common errors in all Python source file
    OK
  Detect dead code in all Python source file
    OK
  Run Python linter for Python source file
    OK
  Unit tests for this project
    OK
Done

Overal result
  OK
```

An example of script output when one error is detected:

```
Running all tests and checkers
  Check all BASH scripts
    Error: please look into files check-bashscripts.log and check-bashscripts.err for possible causes
  Check documentation strings in all Python source file
    OK
  Detect common errors in all Python source file
    OK
  Detect dead code in all Python source file
    OK
  Run Python linter for Python source file
    OK
  Unit tests for this project
    OK
Done

Overal result
  One error detected!
```

Please note that the script creates bunch of `*.log` and `*.err` files that are temporary and won't be commited into the project repository.

#### Coding standards

- You can use scripts `run-linter.sh` and `check-docstyle.sh` to check if the code follows [PEP 8](https://www.python.org/dev/peps/pep-0008/) and [PEP 257](https://www.python.org/dev/peps/pep-0257/) coding standards. These scripts can be run w/o any arguments:

```
./run-linter.sh
./check-docstyle.sh
```

The first script checks the indentation, line lengths, variable names, white space around operators etc. The second
script checks all documentation strings - its presence and format. Please fix any warnings and errors reported by these
scripts.

List of directories containing source code, that needs to be checked, are stored in a file `directories.txt`

#### Code complexity measurement

The scripts `measure-cyclomatic-complexity.sh` and `measure-maintainability-index.sh` are used to measure code complexity. These scripts can be run w/o any arguments:

```
./measure-cyclomatic-complexity.sh
./measure-maintainability-index.sh
```

The first script measures cyclomatic complexity of all Python sources found in the repository. Please see [this table](https://radon.readthedocs.io/en/latest/commandline.html#the-cc-command) for further explanation how to comprehend the results.

The second script measures maintainability index of all Python sources found in the repository. Please see [the following link](https://radon.readthedocs.io/en/latest/commandline.html#the-mi-command) with explanation of this measurement.

You can specify command line option `--fail-on-error` if you need to check and use the exit code in your workflow. In this case the script returns 0 when no failures has been found and non zero value instead.

#### Dead code detection

The script `detect-dead-code.sh` can be used to detect dead code in the repository. This script can be run w/o any arguments:

```
./detect-dead-code.sh
```

Please note that due to Python's dynamic nature, static code analyzers are likely to miss some dead code. Also, code that is only called implicitly may be reported as unused.

Because of this potential problems, only code detected with more than 90% of confidence is reported.

List of directories containing source code, that needs to be checked, are stored in a file `directories.txt`

#### Common issues detection

The script `detect-common-errors.sh` can be used to detect common errors in the repository. This script can be run w/o any arguments:

```
./detect-common-errors.sh
```

Please note that only semantical problems are reported.

List of directories containing source code, that needs to be checked, are stored in a file `directories.txt`

#### Check for scripts written in BASH

The script named `check-bashscripts.sh` can be used to check all BASH scripts (in fact: all files with the `.sh` extension) for various possible issues, incompatibilities, and caveats. This script can be run w/o any arguments:

```
./check-bashscripts.sh
```

Please see [the following link](https://github.com/koalaman/shellcheck) for further explanation, how the ShellCheck works and which issues can be detected.


