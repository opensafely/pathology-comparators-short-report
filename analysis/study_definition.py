
# Import functions
from cohortextractor import (
    StudyDefinition, 
    patients, 
    Measure
)

index_date = '2021-10-01'

# Import codelists
from codelists import path_tests

# create new list from codelist for use creating a string to check for any test being present
test_list = [f'flag_{c}' for c in path_tests]

from loop_variables import make_variable

# create function to loop through imported variables for each code in codelist
def loop_over_codes(code_list):
    variables = {}
    for code in code_list:
        variables.update(make_variable(code, index_date))
    return variables

# Specify study definition

study = StudyDefinition(
    index_date=index_date,
    # Configure the expectations framework
    default_expectations={
        "date": {"earliest": index_date, "latest": "index_date + 6 days"},
        "rate": "exponential_increase",
        "incidence": 0.1,
    },
    
    population=patients.satisfying(
        """
        registered AND
        any_test
        """,

        registered=patients.registered_as_of(
            "index_date",
            return_expectations={"incidence": 0.9},
        ),

    ),


    ##### basic demographics ###

    age_band=patients.categorised_as(
        {
            "missing": "DEFAULT",
            "0-19": """ age >= 0 AND age < 20""",
            "20-29": """ age >=  20 AND age < 30""",
            "30-39": """ age >=  30 AND age < 40""",
            "40-49": """ age >=  40 AND age < 50""",
            "50-59": """ age >=  50 AND age < 60""",
            "60-69": """ age >=  60 AND age < 70""",
            "70-79": """ age >=  70 AND age < 80""",
            "80+": """ age >=  80 AND age < 120""",
        },
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "0-19": 0.125,
                    "20-29": 0.125,
                    "30-39": 0.125,
                    "40-49": 0.125,
                    "50-59": 0.125,
                    "60-69": 0.125,
                    "70-79": 0.125,
                    "80+": 0.125,
                }
            },
        },
        age=patients.age_as_of(
            "index_date",
        )
    ),

    sex=patients.sex(
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"M": 0.5, "F": 0.5}},
        }
    ),

    practice=patients.registered_practice_as_of(
        "index_date",
        returning="pseudo_id",
        return_expectations={
            "int": {"distribution": "normal", "mean": 25, "stddev": 5}, "incidence": 0.5}
    ),

    region=patients.registered_practice_as_of(
        "index_date",
        returning="nuts1_region_name",
        return_expectations={"category": {"ratios": {
            "North East": 0.1,
            "North West": 0.1,
            "Yorkshire and the Humber": 0.1,
            "East Midlands": 0.1,
            "West Midlands": 0.1,
            "East of England": 0.1,
            "London": 0.2,
            "South East": 0.2, }}}
    ),
    

    ### COMPARATORS ##### 
    # for each code in codelist we return: 
    #   * numeric 
    #   * comparator
    #   * flag for having a comparator or not
    #   * flag for having test (with numeric value)

    **loop_over_codes(path_tests),

    # flag for any test result present
    any_test=patients.satisfying(
        f"{' OR '.join(test_list)}", # `flag_12345678 OR flag_23456789 .....`
        return_expectations={
            "incidence": 0.5,
                
        },
    ),
    
)

# # Create measures
measures = list()


for code in path_tests:
    
    m = Measure(

        # rate of comparators being present for each test:
        id=f'{code}_comparator_rate',
        numerator=f"comparator_flag_{code}",
        denominator=f"flag_{code}",
        group_by="population",
        #small_number_suppression=apply_suppression
    )
    
    measures.append(m)


    
