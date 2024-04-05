# Stanard lib
from typing import List, Set, Tuple

# 3rd party
import pandas as pd

            
    
def _get_group_indices(df: pd.DataFrame, group_by: List[str]) -> Set[Tuple]:
    return {tuple(row.array) for _, row in df[group_by].iterrows()}


def add_indices_from_reference(df: pd.DataFrame, reference: pd.DataFrame,
                               group_by: List[str]) -> pd.DataFrame:
    df_indices = _get_group_indices(df, group_by)
    reference_indices = _get_group_indices(reference, group_by)

    for index in reference_indices:
        if index not in df_indices:
            row = pd.DataFrame({k: v for k, v in zip(group_by, index)}, index=[0])
            df = pd.concat([df, row], axis=0, ignore_index=True)
    
    return df.fillna(0)


def count_column(df, column:str, group_by: List[str],
                 filter: List[str]=None) -> pd.DataFrame:
    # Drop all non-relevant columns
    df = df[group_by + [column]]
    
    # Create an empty frame with a multi index over the columns
    # listed in group_by. We will copy the counts onto this frame
    # to avoid dropping indices when the count is zero.
    unique = []
    for col in group_by:
        group_unique = set(df[col].unique())
        unique.append(group_unique)
    index = pd.MultiIndex.from_product(unique,
                                       names=group_by
                                       ).to_frame(index=False)

    # Apply filter over column
    if filter is not None:
        df = df[df[column].isin(filter)]

    # Group the DataFrame. This will drop the indices where the
    # count is zero.
    grouped_df = df.groupby(group_by) \
            .count() \
            .reset_index()
    
    # Merge the grouped frame onto the multi index frame
    merged_df = pd.merge(index, grouped_df, on=group_by,
                         how="left")
    
    # Fill undefined cells with 0
    return merged_df.fillna(0)


def count_cves(df: pd.DataFrame, group_by=None) -> pd.DataFrame:
    if group_by is None:
        group_by = ["publisher", "application"]
    df_total = count_column(df, "severity", group_by)
    df_severe = count_column(df, "severity", group_by, filter=["critical", "high"])
    df_merged = pd.merge(df_total, df_severe, on=group_by, how="left")
    return df_merged.rename({
        "severity_x": "total_cves",
        "severity_y": "severe_cves"
    }, axis=1)

def count_components(df: pd.DataFrame) -> pd.DataFrame:
    return count_column(df, "_type", ["publisher", "application"])
