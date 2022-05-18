''' Import the processed files for visualisation'''

from pathlib import Path
from codelists import path_tests
import pandas as pd
import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"

# import path test codelist to get code descriptions
path_tests = pd.read_csv(os.path.join(f'codelists/user-helen-curtis-tests-with-comparators.csv'))
# replace very long names with shorter ones
path_tests.loc[path_tests["code"]==1011481000000105, "term"] = "EGFR calculated using creatinine CKDEC equation"
path_tests.loc[path_tests["code"]==1020291000000106, "term"] = "GFR calculated by abbreviated MDRD"
#measures_df = measures_df.merge(path_tests, on="code")

# # 1. comparator_rate_per_test
#def simple_plot(factor=None):
# # load data 
# df = pd.read_csv(os.path.join(OUTPUT_DIR, 'comparator_rate_per_test.csv')).sort_values(by="denominator", ascending=False)

# fig, ax1 = plt.subplots()
# # plot numerator and denominator as bars
# ax1.bar(df["description"], df["denominator"])
# ax1.bar(df["description"], df["numerator"])
# ax1.set_ylabel("N")
# ax1.legend(title='Legend', labels=["Without comparators", "With comparators"], bbox_to_anchor=(1.1, 0.5))

# ax2 = ax1.twinx()
# ax2.scatter(df["description"], df["rate"], c='k', marker='x')
# ax2.set_ylim([0, 1])
# ax2.set_ylabel("proportion with comparator")
# plt.xticks(rotation=45)
# plt.savefig(os.path.join(OUTPUT_DIR, 'comparator_rate_per_test.png'))


# 2. comparator_rate_per_test by region
# load data 
def rate_breakdown(factor="region", indices=2):
    '''Produce a chart by tests and by specified factor (region, comparator,)'''

    df = pd.read_csv(os.path.join(OUTPUT_DIR, f'comparator_rate_by_{factor}_per_test.csv'), index_col=[0,1])
    #flatten index
    df.index = df.index.map('{0[0]}|{0[1]}'.format) 
    
    #df = df.set_index("item", append=True)
    df.index = df.index.rename("item")
    print(df)
    
    # keep "rate" only (i.e. proportion with comparators) and rearrange dataframe
    idx = pd.IndexSlice
    df = df.loc[idx[:, 'rate'], :]
    df = df.stack().unstack(1).reset_index()
    df = df.rename(columns={'level_1':factor})
    
    # count tests and number of different values for specified factor
    ntests = df["test"].nunique()
    length = df[factor].nunique()

    fig, ax = plt.subplots(figsize=(15,8))

    # create a number sequence with the number of points on x axis required (allowing for space between groups)
    ind = np.arange(0,df["test"].count()+ df["test"].nunique()-1)
    # create a sequence of the positions where no data will be plotted (ie. the gaps between categories)
    spaces = np.arange(length,len(ind), length+1)
    new_ind = np.delete(ind, spaces)

    width = 0.5 # bar width
    
    for n, r in enumerate(df[factor].unique()):
        # filter df
        dfp = df.loc[df[factor]==r]

        # starting from n, plot data every 'n'th position
        locs = new_ind[n::length]
        # plot chart
        plt.bar(locs, dfp["value"], width, label=r)

    plt.legend(loc="lower right")
    plt.xticks(new_ind[4::length], path_tests, size=8, rotation=45)
    plt.xlabel("Test code", size=20)
    plt.ylabel("Proportion with comparators", size=16)


    plt.savefig(os.path.join(OUTPUT_DIR, f'comparator_rate_per_{factor}_per_test.png'))

rate_breakdown(factor="region")
#rate_breakdown(factor="value")
#rate_breakdown(factor="comparator")



