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