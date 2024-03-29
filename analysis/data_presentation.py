''' Import the processed files for visualisation'''

from pathlib import Path
from codelists import path_tests
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt


custom_sort = ["Glomerular filtration rate",
                "GFR calculated by abbreviated MDRD",
                "EGFR calculated using creatinine CKDEC equation",
                "Nucleated red blood cell count",
                "Rheumatoid factor",
                "Tissue transglutaminase immunoglobulin A level",
                "Plasma C reactive protein",
                "Urine albumin level",
                "Urine microalbumin level",
                "Quantitative faecal immunochemical test",
                "Faecal calprotectin content"]

BASE_DIR = Path(__file__).parents[1]
INPUT_DIR = BASE_DIR / "released_outputs"
OUTPUT_DIR = BASE_DIR / "publication_outputs" 
if not os.path.exists(OUTPUT_DIR):
   os.makedirs(OUTPUT_DIR)

# import path test codelist to get code descriptions
path_tests = pd.read_csv(os.path.join(f'codelists/user-helen-curtis-tests-with-comparators.csv')).set_index("code")
# replace very long names with shorter ones
path_tests.loc[1011481000000105, "term"] = "EGFR calculated using creatinine CKDEC equation"
path_tests.loc[1020291000000106, "term"] = "GFR calculated by abbreviated MDRD"

# # 1. comparator_rate_per_test
# # load data 
df = pd.read_csv(os.path.join(INPUT_DIR, 'comparator_rate_per_test.csv'), index_col=0).sort_values(by="denominator", ascending=False)
df = df.join(path_tests)
df.to_csv(os.path.join(OUTPUT_DIR, 'comparator_rate_per_test_with_names.csv'))



# 2. comparator_rate_per_test by region
# load data 
def rate_breakdown(factor="region", indices=2):
    '''Produce a chart by tests and by specified factor (region, comparator,)'''

    df = pd.read_csv(os.path.join(INPUT_DIR, f'comparator_rate_by_{factor}_per_test.csv'), index_col=[0,1])
    df = df.stack().unstack(level=1).rename(columns={"flag":"total"})
    df = df.join(path_tests, on=None)

    # filter tests to only keep regions with >=100 tests
    df = df.loc[df["total"]>=100]
    df.to_csv(os.path.join(OUTPUT_DIR, f'comparator_rate_by_{factor}_per_test_with_names.csv'))

    df2 = df.copy()[["rate","term"]].reset_index().drop("code", 1)
    df2 = df2.rename(columns={"level_1":factor})
    df2 = df2.set_index(["term",factor]).unstack()
    df2.columns = df2.columns.droplevel()
    #df2["max"] = df2.max(axis=1)

    # sort tests:
    #df2 = df2.sort_values(by="max").drop("max", axis=1)
    df2 = df2.transpose()[custom_sort].transpose()
    
    print(df2)

    # plot heatmap    
    fig, ax = plt.subplots(figsize=(15,8))
    plt.imshow(df2, cmap='autumn_r', interpolation='nearest')
    
    plt.xticks(np.arange(0,9), df2.columns, size=8, rotation=90)
    plt.yticks(np.arange(0,len(df2.index)), df2.index, size=8)
    plt.colorbar()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f'comparator_rate_per_{factor}_per_test.png'))
    plt.show()


rate_breakdown(factor="region")


######### Comparators
df = pd.read_csv(os.path.join(INPUT_DIR, f'comparator_rate_by_comparator_per_test.csv'), index_col=0)
df = df.join(path_tests) # join test names
df = df[["term", "<=_rate", ">=_rate"]]
df.to_csv(os.path.join(OUTPUT_DIR, f'comparator_rate_by_comparator_per_test_with_names.csv'))


######### Values
df = pd.read_csv(os.path.join(INPUT_DIR, f'comparator_rate_by_value_per_test.csv'), index_col=[0,1])
df = df.join(path_tests) # join test names

# make two different output dfs (one for tests with mostly greater-than comparators, and one for less-than)
df_out_gt = pd.DataFrame(columns=["num_value","term","total",">=",">=_rate"])
df_out_lt = pd.DataFrame(columns=["num_value","term","total","<=","<=_rate"])

for n, t in enumerate(custom_sort):
    if n<3:
        # for GFR tests include only greater-than comparators
        main_comparator = ">="
    else:
        main_comparator = "<="

    main_comparator_rate = f"{main_comparator}_rate"
    comparator_subset = [main_comparator_rate,"="]
    df_t = df.loc[df["term"]==t].sort_values(by=main_comparator_rate)
    df_t = df_t[["term", "total", main_comparator, main_comparator_rate]]
    
    # filter out low count values / those not associated with comparators
    df_t = df_t.loc[(df_t["total"]>=100)]
    df_t = df_t.loc[(df_t[main_comparator_rate]>0)]
    df_t = df_t.reset_index().set_index("code")

    if n<3:
        df_out_gt = df_out_gt.append(df_t)
    else:
        df_out_lt = df_out_lt.append(df_t)

df_out_gt.to_csv(os.path.join(OUTPUT_DIR, f'gfr_tests_comparator_associated_values_with_names.csv'), index=False)
df_out_lt.to_csv(os.path.join(OUTPUT_DIR, f'all_non_gfr_tests_comparator_associated_values_with_names.csv'), index=False)




######### Upper and lower limits (reference values returned alongside tests)
for limit in ["upper", "lower"]:
    df = pd.read_csv(os.path.join(INPUT_DIR, f'{limit}_bound_rate_per_test.csv'), index_col=[0,1])
    df = df.join(path_tests) # join test names

    # calculate rank for each limit value to find top 2 only
    df = df.reset_index()
    df["rank"] = df.groupby('code')['rate'].rank(method='dense', ascending=False).astype(int)
    df = df[["code","term","rank",limit,"rate"]].loc[df["rank"]<3]
    df = df.set_index(["code","term","rank"]).stack().unstack(level=2).unstack()
    
    df.to_csv(os.path.join(OUTPUT_DIR, f'all_tests_{limit}_limit_with_names.csv'))


