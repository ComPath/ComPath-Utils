# -*- coding: utf-8 -*-

"""An abstract pathway for a ComPath repository."""

from abc import abstractmethod
from typing import Set

from sqlalchemy import Column

import pybel.dsl

__all__ = [
    'CompathPathway',
    'CompathProtein',
]


class CompathPathway:
    """This is the abstract class that the Pathway model in a ComPath repository should extend."""

    name: Column

    def get_gene_set(self) -> Set['CompathProtein']:
        """Return the genes associated with the pathway (gene set).

        Note this function restricts to HGNC symbols genes.

        :return: Return a set of protein models that all have names
        """
        raise NotImplementedError

    @property
    def resource_id(self):
        """Return the database-specific resource identifier (will be a SQLAlchemy Column instance)."""
        raise NotImplementedError

    @property
    def url(self):
        """Return the URL to the resource, usually based in the identifier for this pathway.

        :rtype: str

        Example for WikiPathways:

        .. code-block:: python

            >>> @property
            >>> def url(self):
            >>>     return 'https://www.wikipathways.org/index.php/Pathway:{}'.format(self.wikipathways_id)
        """
        raise NotImplementedError

    def to_pybel(self) -> pybel.dsl.BiologicalProcess:
        """Serialize this pathway to a PyBEL node."""
        raise NotImplementedError


class CompathProtein:
    """This is an abstract class that the Protein model in a ComPath repository should extend."""

    hgnc_symbol: Column

    def get_pathways_ids(self):
        """Get the identifiers of the pathways associated with this protein."""
        raise NotImplementedError

    @abstractmethod
    def to_pybel(self) -> pybel.dsl.Protein:
        """Serialize this protein to a PyBEL node."""
        raise NotImplementedError
