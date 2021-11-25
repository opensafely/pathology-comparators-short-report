from pathlib import Path
import pandas as pd
import os
from generate_measures import measures

measures_df = pd.DataFrame(columns=["code","numerator", "measure_no_code"])

for m in measures:
    start = m.id.find('_') # extract snomed code from beginning of string
    measures_df.loc[m.id] = [int(m.id[:start]), m.numerator, m.id[start+1:]]

# make list of distinct measures without test codes included
measures_no_codes = measures_df.measure_no_code.drop_duplicates().values

# import path test codelist to get code descriptions
path_tests = pd.read_csv(os.path.join(f'codelists/user-helen-curtis-tests-with-comparators.csv'))
# replace very long names with shorter ones
path_tests.loc[path_tests["code"]==1011481000000105, "term"] = "EGFR calculated using creatinine CKDEC equation"
path_tests.loc[path_tests["code"]==1020291000000106, "term"] = "GFR calculated by abbreviated MDRD"

# add code descriptions to measures df
measures_df = measures_df.reset_index().rename(columns={"index":"measure"})
measures_df = measures_df.merge(path_tests, on="code")

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"


for measure in measures_no_codes:
    measures_filtered = measures_df.loc[measures_df["measure_no_code"]==measure]
    
    # create empty df for results
    summary = pd.DataFrame(columns=["description", "measure", "numerator", "denominator", "rate"])
        
    for code, term, numerator in zip(measures_filtered.code, measures_filtered.term, measures_filtered.numerator):
        
        
        # load measures data
        df = pd.read_csv(os.path.join(OUTPUT_DIR, f'measure_{code}_{measure}.csv'), parse_dates=['date']).sort_values(by='date')
        
        # sum numerators and denominators across each week (denominator is no of tests each week not population, so can be summed)
        total = df.sum()
        summary.loc[f"{code}_{measure}"] = [code, term,
                                            total[numerator], 
                                            total[f"flag_{code}"], # all measures have same denominator
                                            total[numerator]/total[f"flag_{code}"]]

    summary.to_csv(os.path.join(OUTPUT_DIR, f'{measure}_rates_per_test.csv'))
