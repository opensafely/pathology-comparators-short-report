# Import functions

from cohortextractor import (
    patients,
    codelist,
)

# Import codelists

from codelists import *


def make_variable(code, index_date):
    return {
        # numeric value of each test
        f"value_{code}": (
            patients.with_these_clinical_events(
                codelist([code], system="snomed"),
                between=["index_date", "index_date + 6 days"],
                returning="numeric_value",
                find_last_match_in_period=True,
                return_expectations={
                    "incidence": 0.2,
                    "float": {"distribution": "normal", "mean": 50, "stddev": 3},
                },
            )
        ),
        
        # comparator ('<', '>', '=', etc) returned with test result
        f"comparator_{code}": (
            patients.comparator_from(
                f"value_{code}",
                return_expectations={
                    "rate": "universal",
                    "category": {
                        "ratios": {  # ~, =, >= , > , < , <=
                            None: 0.10,
                            "~": 0.05,
                            "=": 0.65,
                            ">=": 0.05,
                            ">": 0.05,
                            "<": 0.05,
                            "<=": 0.05}
                    },
                    "incidence": 0.80,
                },
            )
        ),

        # simplified comparators
        f"comparator_simple_{code}":(
            patients.categorised_as(
                {
                "=": "DEFAULT",
                ">=": f'comparator_{code} = ">" OR comparator_{code} = ">="',
                "<=": f'comparator_{code} = "<" OR comparator_{code} = "<="',
                },
                return_expectations={
                    "incidence": 0.9,
                    "category": {
                        "ratios": {
                            "=": 0.8,
                            ">=": 0.1,
                            "<=": 0.1}
                        },
                },
            )
        ),

        # binary flag for comparator > or >=
        f"comparator_gt_{code}":(
            patients.satisfying(
                f"comparator_simple_{code}='>='",
                return_expectations={
                    "incidence": 0.1,
                },
            )
        ),

        # binary flag for comparator < or <=
        f"comparator_lt_{code}":(
            patients.satisfying(
                f"comparator_simple_{code}='<='",
                return_expectations={
                    "incidence": 0.1,
                },
            )
        ),

        # binary flag for any comparator
        f"comparator_flag_{code}":(
            patients.satisfying(
                f"comparator_gt_{code} OR comparator_lt_{code}",
                return_expectations={
                    "incidence": 0.1,
                },
            )
        ),

        # binary flag for No comparator
        f"no_comparator_flag_{code}":(
            patients.satisfying(
                f"NOT comparator_flag_{code}",
                return_expectations={
                    "incidence": 0.9,
                },
            )
        ),

        # binary flag for having each test (with numeric result)
        f"flag_{code}":(
            patients.satisfying(
                f"value_{code}",
                return_expectations={
                    "incidence": 0.2,
                },
            )
        )
    }
