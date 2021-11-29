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
    
    # 1. basic measure 
    if measure == "comparator_rate":
        # create empty df for results
        summary = pd.DataFrame(columns=["description", "numerator", "denominator", "rate"])
        
        for code, term, numerator in zip(measures_filtered.code, measures_filtered.term, measures_filtered.numerator):
                    
            # load measures data
            df = pd.read_csv(os.path.join(OUTPUT_DIR, f'measure_{code}_{measure}.csv'), parse_dates=['date']).sort_values(by='date')
 
            # sum numerators and denominators across each week (denominator is no of tests each week not population, so can be summed)
            total = df.sum()
            summary.loc[code] = [term,
                                total[numerator], 
                                total[f"flag_{code}"], # all measures have same denominator
                                total[numerator]/total[f"flag_{code}"]]

    # 2. Overall rate of comparators being present for each test, split by region:
    elif measure == "comparator_rate_by_region":

        # create empty df for results - import a random file to get list of regions
        df = pd.read_csv(os.path.join(OUTPUT_DIR, f'measure_{measures_df["code"].iloc[0]}_{measure}.csv'), parse_dates=['date'])
        regions = df.fillna("Unknown").region.drop_duplicates()
        
        summary = pd.DataFrame(columns=regions)
        summary['code'] = None
        summary['item'] = None
        summary = summary.set_index(['code', 'item'])


        for code, term, numerator in zip(measures_filtered.code, measures_filtered.term, measures_filtered.numerator):
        
            # load measures data
            df = pd.read_csv(os.path.join(OUTPUT_DIR, f'measure_{code}_{measure}.csv'), parse_dates=['date']).sort_values(by='date')
            df = df.fillna("Unknown") # fill any missing regions

            # sum numerators and denominators for each comparator across each week (denominator is no of tests each week not population, so can be summed)
            total = df.groupby("region").sum().fillna(0).astype(int)
            total["value"] = total[numerator]/total[f"flag_{code}"]
            total = total.transpose()

            # reorganise index
            total.index = total.index.str.replace(f"_{code}","")
            total = pd.concat({code: total}, names=['code']) # add new index
            
            # concatenate results
            summary = summary.append(total)


    # 3. by comparator
    elif measure == "comparator_rate_by_comparator":
        # create empty df for results
        summary = pd.DataFrame(columns=["<=", "=", ">="])

        for code, term in zip(measures_filtered.code, measures_filtered.term):
        
            # load measures data
            df = pd.read_csv(os.path.join(OUTPUT_DIR, f'measure_{code}_{measure}.csv'), parse_dates=['date']).sort_values(by='date')
            df = df.fillna("=") # fill any missing comparators

            # sum numerators and denominators for each comparator across each week (denominator is no of tests each week not population, so can be summed)
            total = df.groupby(f"comparator_simple_{code}")[f"flag_{code}"].sum().fillna(0).astype(int)
            # keep only test code from series name ("flag_{code}")
            total = total.rename(total.name[5:])
            
            # concatenate results
            summary = summary.append(total)


    # 4. Rate of comparators being present for each test, split by comparator and numeric value:
    elif measure == "comparator_rate_by_value":
        # create empty df for results
        summary = pd.DataFrame(columns=["code", "value", "<=", ">="])
        summary = summary.set_index(['code', 'value'])

        for code, term in zip(measures_filtered.code, measures_filtered.term):
        
            # load measures data
            df = pd.read_csv(os.path.join(OUTPUT_DIR, f'measure_{code}_{measure}.csv'), parse_dates=['date']).sort_values(by='date')
            # filter to comparators (should affect dummy data only)
            df = df.loc[df[f"comparator_simple_{code}"].isin(["<=", ">="])] 

            # sum denominators for each comparator across each week (denominator is no of tests each week not population, so can be summed)
            total = df.groupby([f"comparator_simple_{code}",f"value_{code}"])[f"comparator_flag_{code}"].sum().fillna(0).astype(int)
            total = total.unstack(level=0) # make comparators the columns
            total = total.loc[total.sum(axis=1)>0] # remove rows with no data (because of how measures are produced, 
                                                    # each value will be repeated for each comparator even if no occurrences)
            
            total = pd.concat({code: total}, names=['code']) # add new index

            # load no-comparators data 
            df = pd.read_csv(os.path.join(OUTPUT_DIR, f'measure_{code}_no_{measure}.csv'), parse_dates=['date']).sort_values(by='date')
           
            # sum denominators across each week 
            total2 = df.groupby([f"value_{code}"])[f"no_comparator_flag_{code}"].sum().fillna(0).astype(int)
            total2 = total2.rename("=")
            
            total2 = pd.concat({code: total2}, names=['code']) # add new index            
            
            total = total.join(total2, how="outer").fillna(0).astype(int)
            
            # concatenate results
            summary = summary.append(total)

        print(summary)

    summary.to_csv(os.path.join(OUTPUT_DIR, f'{measure}_rates_per_test.csv'))
