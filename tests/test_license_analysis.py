from src.license_scoring import license_scoring


def test_scenario_1():
    input_payload = {
        "packages": [
            {
                "package": "pkg1",
                "version": "ver-1.1",
                "license": ["MIT"]
            },
            {
                "package": "pkg2",
                "version": "ver-0.4",
                "license": ["LGPL V2.1"]
            }
        ]
    }

    actual_output = license_scoring(payload=input_payload)

    expected_output = {
        "dependencies": [
            {
                "package": "pkg1",
                "version": "ver-1.1",
                "license_conflict": False,
                "license_outlier": False,
                "unknown_licenses": []
            },
            {
                "package": "pkg2",
                "version": "ver-0.4",
                "license_conflict": False,
                "license_outlier": False,
                "unknown_licenses": []
            }
        ],
        "recommended_stack_licenses": [],
        "stack_license_conflict_exists": False,
        "stack_unknown_licenses": [None]
    }

    assert(actual_output['recommended_stack_licenses'] ==
           expected_output['recommended_stack_licenses'])

