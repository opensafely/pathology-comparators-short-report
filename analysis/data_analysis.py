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

# # 1. comparator_rate_per_test
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
# plt.savefig(os.path.join(OUTPUT_DIR, 'comparator_rate_per_test.png'))


# 2. comparator_rate_per_test by region
# load data 
df = pd.read_csv(os.path.join(OUTPUT_DIR, 'comparator_rate_by_region_per_test.csv'), index_col=[0,1])

# keep "value" only (i.e. proportion with comparators) and rearrange dataframe
idx = pd.IndexSlice
df = df.loc[idx[:, 'value'], :]
df = df.stack().unstack(1).reset_index()
df = df.rename(columns={'level_1':'region'})

# count tests and regions
ntests = df["code"].nunique()
nregions = df["region"].nunique()

fig, ax = plt.subplots(figsize=(15,8))

# create a number sequence with the number of points on x axis required (allowing for space between groups)
ind = np.arange(0,df["code"].count()+ df["code"].nunique()-1)
# create a sequence of the positions where no data will be plotted (ie. the gaps between categories)
spaces = np.arange(nregions,len(ind),nregions+1)
new_ind = np.delete(ind, spaces)

width = 0.5 # bar width

for n, r in enumerate(df["region"].unique()):
    # filter df
    dfp = df.loc[df["region"]==r]

    # starting from n, plot data every 'n'th position
    locs = new_ind[n::nregions]
    # plot chart
    plt.bar(locs, dfp["value"], width, label=r)

plt.legend(loc="lower right")
plt.xticks(new_ind[4::nregions], path_tests, size=8, rotation=45)
plt.xlabel("Test code", size=20)
plt.ylabel("Proportion with comparators", size=16)


plt.savefig(os.path.join(OUTPUT_DIR, 'comparator_rate_per_region_per_test.png'))
