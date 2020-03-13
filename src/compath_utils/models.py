# -*- coding: utf-8 -*-

"""An abstract pathway for a ComPath repository."""

from __future__ import annotations

from abc import abstractmethod
from typing import List, Set

from sqlalchemy import Column

import pybel.dsl

__all__ = [
    'CompathPathwayMixin',
    'CompathProteinMixin',
]


class CompathPathwayMixin:
    """This is the abstract class that the Pathway model in a ComPath repository should extend."""

    name: Column
    proteins: List[CompathProteinMixin]

    @abstractmethod
    def get_gene_set(self):
        """Return the genes associated with the pathway (gene set).

        Note this function restricts to HGNC symbols genes.

        :return: Return a set of protein models that all have names
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def resource_id(self) -> str:
        """Return the database-specific resource identifier (will be a SQLAlchemy Column instance)."""
        raise NotImplementedError

    @property
    @abstractmethod
    def url(self) -> str:
        """Return the URL to the resource, usually based in the identifier for this pathway.

        Example for WikiPathways:

        .. code-block:: python

            >>> @property
            >>> def url(self):
            >>>     return f'https://www.wikipathways.org/index.php/Pathway:{self.wikipathways_id}'
        """
        raise NotImplementedError

    @abstractmethod
    def to_pybel(self) -> pybel.dsl.BiologicalProcess:
        """Serialize this pathway to a PyBEL node."""
        raise NotImplementedError

    def add_to_bel_graph(self, graph: pybel.BELGraph) -> Set[str]:
        """Add the pathway to a BEL graph."""
        pathway_node = self.to_pybel()
        return {
            graph.add_part_of(protein.to_pybel(), pathway_node)
            for protein in self.proteins
        }


class CompathProteinMixin:
    """This is an abstract class that the Protein model in a ComPath repository should extend."""

    hgnc_symbol: Column

    @abstractmethod
    def get_pathways_ids(self):
        """Get the identifiers of the pathways associated with this protein."""
        raise NotImplementedError

    @abstractmethod
    def to_pybel(self) -> pybel.dsl.Protein:
        """Serialize this protein to a PyBEL node."""
        raise NotImplementedError
