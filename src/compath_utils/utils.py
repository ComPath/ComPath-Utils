# -*- coding: utf-8 -*-

"""Utilities for ComPath Utilities (yo dawg)."""

import logging
from typing import Mapping

from pandas import DataFrame, Series

logger = logging.getLogger(__name__)


def dict_to_df(data: Mapping) -> DataFrame:
    """Convert a dictionary to a DataFrame."""
    return DataFrame({
        key: Series(list(values))
        for key, values in data.items()
    })


def write_dict(data: Mapping, path: str) -> None:
    """Write a dictionary to a file as an Excel document."""
    gene_sets_df = dict_to_df(data)
    gene_sets_df.to_excel(path, index=False)
    logger.info("Gene sets exported to %s", path)
