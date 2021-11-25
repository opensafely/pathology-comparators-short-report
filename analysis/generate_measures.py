from codelists import path_tests
from cohortextractor import Measure

# # Create measures
measures = list()

for code in path_tests:
    m = Measure(
        # 1. Overall rate of comparators being present for each test:
        id=f'{code}_comparator_rate',
        numerator=f"comparator_flag_{code}",
        denominator=f"flag_{code}",
        group_by="population",
        #small_number_suppression=apply_suppression
    )
    measures.append(m)

    m = Measure(
        # 2. Overall rate of comparators being present for each test, split by region:
        id=f'{code}_comparator_rate_by_region',
        numerator=f"comparator_flag_{code}",
        denominator=f"flag_{code}",
        group_by="region",
        #small_number_suppression=apply_suppression
    )
    measures.append(m)

    m = Measure(
        # 3. rate of comparators being present for each test, split by comparator (simplified):
        id=f'{code}_comparator_rate_by_comparator',
        numerator=f"comparator_flag_{code}", # this won't produce a figure for "=" but we can calculate by subtraction
        denominator=f"flag_{code}",  ###### could use smaller denominator here...
        group_by=f"comparator_simple_{code}",
        #small_number_suppression=apply_suppression
    )
    measures.append(m)

    m = Measure(
        # 4.a rate of comparators being present for each test, split by comparator and numeric value:
        # NB produces very long df because every possible value is repeated for each comparator
        id=f'{code}_comparator_rate_by_value',
        numerator=f"flag_{code}", # here we have same num and denom but we just need one count for further processing
        denominator=f"flag_{code}",
        group_by=[f"comparator_simple_{code}", f"value_{code}"],
        #small_number_suppression=apply_suppression
    )
    measures.append(m)

