import numpy as np
import pandas as pd
import random
import time
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def perform_pca_binning(df, feature_importances, seed=12345):
    np.random.seed(seed)

    # Ensure num_pcs does not exceed the number of columns in df
    num_pcs = min(feature_importances.shape[0], df.shape[1])

    def create_bins_and_digitize(data, n_bins):
        edges = np.linspace(data.min(), data.max(), n_bins + 1)
        bins = np.digitize(data, edges)
        return bins

    def compute_sample_bins(df, bin_sizes):
        bins = [create_bins_and_digitize(df.iloc[:, i], bin_sizes[i]) for i in range(num_pcs)]
        df['grid_cell'] = list(zip(*bins))

    compute_sample_bins(df, feature_importances)
    return


def adjust_feature_importances(pca, top_features=19, constant=2):
    n_features = len(pca.explained_variance_ratio_)
    print(f'Number of features is {n_features}.')
    if n_features < 2 * top_features:
        out = np.ceil(pca.explained_variance_ratio_ * 100).astype(int)
    else:
        # multiplier = (1.0 * constant) / pca.explained_variance_ratio_[top_features]
        # out = np.ceil(pca.explained_variance_ratio_ * multiplier).astype(int)
        out = np.ceil(pca.explained_variance_ratio_ * 100).astype(int)
        
    out = out[out > constant] # this line is added to improve the performance
    l = len(out)
    print(f'Number of features after adjustment is {l}.')
    return out


def find_threshold_index(sorted_grid_cells, threshold):
    cumulative = 0
    for index, frequency in sorted_grid_cells.value_counts().sort_index().items():
        cumulative += index * frequency
        if cumulative >= threshold:
            return index
    return None


def accumulate_indices_until_threshold(df, threshold, seed=1234):
    random.seed(seed)
    grid_cell_counts = df['grid_cell'].value_counts()
    sorted_grid_cells = grid_cell_counts.sort_values()
    threshold_index = find_threshold_index(sorted_grid_cells, threshold)
    print(f'Threshold index is: {threshold_index}')
    
    grouped_df = df.groupby('grid_cell')
    accumulated_indices = []
    accumulated_count = 0
    remaining_indices = []

    for grid_cell in sorted_grid_cells.index:
        group_indices = grouped_df.get_group(grid_cell).index.tolist()
        if len(group_indices) < threshold_index:
            accumulated_indices.extend(group_indices)
            accumulated_count += len(group_indices)
        elif len(group_indices) == threshold_index:
            remaining_indices.extend(group_indices)
        else:
            break

    remaining_count = threshold - accumulated_count
    print(f'Remaining count is: {remaining_count}')
    
    accumulated_indices.extend(random.sample(remaining_indices, remaining_count))
    return accumulated_indices
