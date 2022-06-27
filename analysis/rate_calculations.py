''' Process measure files:
 - aggregate over all weeks; 
 - for each measure, compile all tests into one file with names'''

from pathlib import Path
import pandas as pd
import os
from generate_measures import measures


def calculate_rates(df):
    ''' calculate rates as decimals (num/denom) for each column in a df, where denom is the sum of the column values'''
    summary_cols = df.columns
    df["total"] = df.sum(axis=1)
    df = df.loc[df["total"]>0]
    #print(df["total"])
    for c in summary_cols:
        df[f"{c}_rate"] = (df[c]/df["total"])
    return df



# A measure file has been created for each measure *for each test*, 
# First we create a list of the unique measures (e.g. "comparator_rate_by_region")
# and a list of unique codes by separating test codes from measure names
measures_df = pd.DataFrame(columns=["code","numerator", "measure_no_code"])
for m in measures:
    start = m.id.find('_') # extract snomed code from beginning of string
    measures_df.loc[m.id] = [int(m.id[:start]), m.numerator, m.id[start+1:]]

# make list of distinct measures without test codes included
measures_no_codes = measures_df.measure_no_code.drop_duplicates().values

measures_df = measures_df.reset_index().rename(columns={"index":"measure"})

###### TODO add code descriptions to measures df

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"

for measure in measures_no_codes:
    measures_filtered = measures_df.loc[measures_df["measure_no_code"]==measure]
    
    # 1. basic measure - comparator rate per code
    if measure == "comparator_rate":
        # create empty df for results
        summary = pd.DataFrame(columns=["numerator", "denominator", "rate"])
        print(measure)
        for code, numerator in zip(measures_filtered.code, measures_filtered.numerator):
            # load measures data
            df = pd.read_csv(os.path.join(OUTPUT_DIR, f'measure_{code}_{measure}.csv'), parse_dates=['date']).sort_values(by='date')
            # sum numerators and denominators across each week (denominator is no of tests each week not population, so can be summed)
            total = df.sum()
            # round to nearest 10
            total = 10*((total/10).round(0))
            summary.loc[code] = [total[numerator], 
                                total[f"flag_{code}"], # all measures have same denominator
                                total[numerator]/total[f"flag_{code}"]]

    # 2. by comparator
    elif measure == "comparator_rate_by_comparator":
        print(measure)
        # create empty df for results
        summary = pd.DataFrame(columns=["<=", "=", ">="])

        for code in measures_filtered.code:
        
            # load measures data
            df = pd.read_csv(os.path.join(OUTPUT_DIR, f'measure_{code}_{measure}.csv'), parse_dates=['date']).sort_values(by='date')
            df = df.fillna("=") # fill any missing comparators

            # sum numerators and denominators for each comparator across each week (denominator is no of tests each week not population, so can be summed)
            total = df.groupby(f"comparator_simple_{code}")[f"flag_{code}"].sum().fillna(0).astype(int)
            
            # keep only test code from series name ("flag_{code}")
            total = total.rename(total.name[5:])

            # round to nearest 10
            total = 10*((total/10).round(0))
            
            # concatenate results
            summary = summary.append(total)
        
        # calculate rates
        summary = calculate_rates(summary)


    # 3. Overall rate of comparators being present for each test, split by region or value:
    elif measure in ["comparator_rate_by_region"]:
        print(measure)
        # create empty df for results - import any of the files to get list of regions
        splitter = measure.split("_")[-1] # "region" or (numeric) value
        # use one file to get list of possible values
        df = pd.read_csv(os.path.join(OUTPUT_DIR, f'measure_{measures_df["code"].iloc[0]}_{measure}.csv'), parse_dates=['date'])
        df = df.fillna("Unknown") # fill any missing regions

        column_list = list(df[splitter].drop_duplicates().values)
        column_list.extend(['code', 'item'])
        summary = pd.DataFrame(columns=column_list).set_index(['code', 'item'])

        for code, numerator in zip(measures_filtered.code, measures_filtered.numerator):
            # load measures data
            df = pd.read_csv(os.path.join(OUTPUT_DIR, f'measure_{code}_{measure}.csv'), parse_dates=['date']).sort_values(by='date')
            df = df.drop(columns=["value"])

            df = df.fillna("Unknown") # fill any missing regions                

            # sum numerators and denominators for each comparator across each week (denominator is no of tests each week not population, so can be summed)
            total = df.groupby(splitter).sum().fillna(0).astype(int)
            
            # round to nearest 10
            total = 10*((total/10).round(0))

            # calculate rates
            total["rate"] = total[numerator]/total[f"flag_{code}"]
            total = total.transpose()

            # reorganise index
            total.index = total.index.str.replace(f"_{code}","")
            total = pd.concat({code: total}, names=['code']) # add new index
            
            # concatenate results
            summary = summary.append(total)

    # 4. Rate of comparators being present for each test, split by comparator and numeric value:
    elif measure == "comparator_rate_by_value":
        print(measure)
        # create empty df for results
        summary = pd.DataFrame(columns=["code", "num_value", "<=", ">="])
        summary = summary.set_index(['code', 'num_value'])

        for code in measures_filtered.code:
        
            # load measures data
            df = pd.read_csv(os.path.join(OUTPUT_DIR, f'measure_{code}_{measure}.csv'), parse_dates=['date']).sort_values(by='date')
            # filter to unequal comparators (should affect dummy data only), also where count>0
            df = df.drop(columns=["value"]).loc[df[f"comparator_simple_{code}"].isin(["<=", ">="]) & (df[f"comparator_flag_{code}"]>0)] 

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

            # round to nearest 10
            total = 10*((total/10).round(0))
            
            # concatenate results
            summary = summary.append(total)

        # calculate rates
        summary = calculate_rates(summary)


    print(summary)
    summary.to_csv(os.path.join(OUTPUT_DIR, f'{measure}_per_test.csv'))
