from codelists import path_tests
from cohortextractor import Measure

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


for code in path_tests:
    m = Measure(
        # rate of comparators being present for each test, split by region:
        id=f'{code}_comparator_rate_by_region',
        numerator=f"comparator_flag_{code}",
        denominator=f"flag_{code}",
        group_by="region",
        #small_number_suppression=apply_suppression
    )
    measures.append(m)

for code in path_tests:
    m = Measure(
        # rate of comparators being present for each test, split by comparator:
        id=f'{code}_comparator_rate_by_comparator',
        numerator=f"comparator_flag_{code}",
        denominator=f"flag_{code}",  ###### could use smaller denominator here...
        group_by=f"comparator_{code}",
        #small_number_suppression=apply_suppression
    )
    measures.append(m)

for code in path_tests:
    m = Measure(
        # rate of comparators being present for each test, split by numeric value:
        id=f'{code}_comparator_rate_by_value',
        numerator=f"comparator_flag_{code}",
        denominator=f"flag_{code}",
        group_by=f"value_{code}",
        #small_number_suppression=apply_suppression
    )
    measures.append(m)

