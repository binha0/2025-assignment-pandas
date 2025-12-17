"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    regions = pd.read_csv("data/regions.csv",sep=",",index_col='id')
    regions.columns = ['code_reg','name_reg','slug']
    departments = pd.read_csv("data/departments.csv",sep=",",index_col='id')
    departments.columns = ['code_reg','code_dep','name_dep','slug']
    referendum = pd.read_csv("data/referendum.csv",sep =';')
    referendum.columns = ['code_dep', 'Department name', 'Town code', 'Town name',
                            'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    # print(regions.head(4))
    # print(departments.head(4))
    # print(referendum)
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_df = pd.merge(regions,departments,"left",'code_reg')
    # merged_df = pd.concat([regions,departments])
    # print(merged_df)
    return merged_df[['code_reg','name_reg','code_dep','name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    ind = np.where(referendum['code_dep'].str.startswith("Z"))[0]
    referendum = referendum.drop(ind)
    merged_df = pd.merge(referendum,regions_and_departments,"left",'code_dep')
    # print(merged_df.columns)
    # print(merged_df)
    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    aux = referendum_and_areas[['code_reg','name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]
    results = aux.groupby('code_reg').sum()
    return results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    ref_map = gpd.read_file('data/regions.geojson') # load geodata

    ref_map.columns = ['code_reg','nom','geometry']
    ind = np.where(ref_map['nom'].isin(['Guadeloupe','Martinique','Guyane','La Réunion','Mayotte']))[0] # remove non metropolitan france states
    # merging results and geographic data 
    merged_results = pd.merge(ref_map,referendum_result_by_regions,'left','code_reg')
    merged_results = merged_results.drop(ind)
    print(merged_results)

    choiceA = merged_results.apply(lambda x: x['Choice A']/x['Registered'],axis=1)
    merged_results['Ratio A'] = choiceA

    merged_results.plot(column='Ratio A', cmap='OrRd', legend=True,
                        legend_kwds={'label': "Ratio of Choice A by region",
                                    'orientation': "horizontal"})

    return merged_results


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    # plt.show()
    plt.savefig('referendum_map.png')
