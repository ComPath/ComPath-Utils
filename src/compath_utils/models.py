# -*- coding: utf-8 -*-

"""An abstract pathway for a ComPath repository."""

from abc import ABC, abstractmethod

from sqlalchemy import Column
from sqlalchemy.ext.declarative import DeclarativeMeta

import pybel.dsl

__all__ = [
    'CompathPathway',
    'CompathProtein',
]


class CompathPathway(ABC, DeclarativeMeta):
    """This is the abstract class that the Pathway model in a ComPath repository should extend."""

    name: Column

    @abstractmethod
    def get_gene_set(self):
        """Return the genes associated with the pathway (gene set).

        Note this function restricts to HGNC symbols genes.

        :return: Return a set of protein models that all have names
        """

    @property
    @abstractmethod
    def resource_id(self):
        """Return the database-specific resource identifier (will be a SQLAlchemy Column instance)."""

    @property
    @abstractmethod
    def url(self):
        """Return the URL to the resource, usually based in the identifier for this pathway.

        :rtype: str

        Example for WikiPathways:

        .. code-block:: python

            >>> @property
            >>> def url(self):
            >>>     return 'https://www.wikipathways.org/index.php/Pathway:{}'.format(self.wikipathways_id)
        """

    @abstractmethod
    def to_pybel(self) -> pybel.dsl.BiologicalProcess:
        """Serialize this pathway to a PyBEL node."""


class CompathProtein(ABC, DeclarativeMeta):
    """This is an abstract class that the Protein model in a ComPath repository should extend."""

    hgnc_symbol: Column

    @abstractmethod
    def get_pathways_ids(self):
        """Get the identifiers of the pathways associated with this protein."""

    @abstractmethod
    def to_pybel(self) -> pybel.dsl.Protein:
        """Serialize this protein to a PyBEL node."""
