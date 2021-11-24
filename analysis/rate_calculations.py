from pathlib import Path
import pandas as pd
import os

# from codelists import path_tests
path_tests = pd.read_csv(os.path.join(f'codelists/user-helen-curtis-tests-with-comparators.csv'))
print(path_tests)

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"

print(path_tests)

summary = pd.DataFrame(columns=["description", "numerator", "denominator", "rate"])

for code, term in zip(path_tests.code, path_tests.term):
    
    df = pd.read_csv(os.path.join(OUTPUT_DIR, f'measure_{code}_comparator_rate.csv'), parse_dates=['date']).sort_values(by='date')
    
    # sum numerators and denominators across each week (denominator is no of tests each week not population, so can be summed)
    total = df.sum()
    summary.loc[code] = [term,
                        total[f"comparator_flag_{code}"], 
                        total[f"flag_{code}"], 
                        total[f"comparator_flag_{code}"]/total[f"flag_{code}"]]

summary.to_csv(os.path.join(OUTPUT_DIR, f'comparator_rates_per_test.csv'))
