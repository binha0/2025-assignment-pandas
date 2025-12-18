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
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")
    referendum = pd.read_csv("data/referendum.csv", sep =';')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_df = pd.merge(regions, departments, "right", left_on='code',
                         right_on='region_code')
    merged_df = merged_df.set_index('id_x')[['code_x', 'name_x', 'code_y', 'name_y']]
    merged_df.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    def correction_dep(x):
        if x.startswith("0"):
            return x.split("0")[1]
        else:
            return x
    regions_and_departments['code_dep'] = regions_and_departments['code_dep'].apply(correction_dep)

    mask_z = referendum['Department code'].astype(str).str.startswith('Z')
    referendum = referendum.loc[~mask_z].copy()

    merged_df = pd.merge(referendum, regions_and_departments,
                         how='left', left_on='Department code', right_on='code_dep')
    merged_df = merged_df.dropna()
    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    aux = referendum_and_areas[['code_reg', 'name_reg', 'Registered',
                                'Abstentions', 'Null', 'Choice A', 'Choice B']]

    results = aux.groupby('code_reg').agg({
        'name_reg': 'first',
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    })

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

    ref_map.columns = ['code_reg', 'nom', 'geometry']

    if 'code_reg' not in referendum_result_by_regions.columns:
        referendum_result_by_regions = referendum_result_by_regions.reset_index()

    merged_results = ref_map.merge(referendum_result_by_regions, on='code_reg', how='left')

    remove = ['Guadeloupe', 'Martinique', 'Guyane', 'La Réunion', 'Mayotte']
    merged_results = merged_results[~merged_results['nom'].isin(remove)].copy()

    denom = merged_results['Choice A'] + merged_results['Choice B']
    merged_results['ratio'] = merged_results['Choice A'] / denom

    merged_results.plot(column='ratio', cmap='OrRd', legend=True,
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

    plot_referendum_map(referendum_results)
    plt.savefig('referendum_map.png')
