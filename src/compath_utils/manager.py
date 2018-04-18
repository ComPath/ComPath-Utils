# -*- coding: utf-8 -*-

"""This module contains the abstract manager that all ComPath managers should extend"""

from abc import abstractmethod

from bio2bel import AbstractManager
from compath_utils.exc import CompathManagerPathwayModelError

__all__ = [
    'CompathManager',
]


class CompathManager(AbstractManager):
    """This is the abstract class that all ComPath managers should extend"""

    # This needs to be defined
    pathway_model = None

    def __init__(self, *args, **kwargs):
        """Doesn't let this class get instantiated if the pathway_model"""
        if self.pathway_model is None:
            raise CompathManagerPathwayModelError('did not set class-level variable pathway_model')

        super().__init__(*args, **kwargs)

    @abstractmethod
    def get_pathway_by_id(self, pathway_id):
        """Gets a pathway by its database-specific identifier. Not to be confused with the standard column called "id"

        :param pathway_id: Pathway identifier
        :rtype: Optional[Pathway]
        """

    @abstractmethod
    def get_pathway_names_to_ids(self):
        """Returns a dictionary of pathway names to ids

        :rtype: dict[str,str]
        """

    @abstractmethod
    def query_gene_set(self, gene_set):
        """Returns pathway counter dictionary

        :param iter[str] gene_set: An iterable of HGNC gene symbols to be queried
        :rtype: dict[str,dict]
        :return: Enriched pathways with mapped pathways/total
        """

    def get_pathway_by_name(self, pathway_name):
        """Gets a pathway by its database-specific name

        :param pathway_name: Pathway name
        :rtype: Optional[Pathway]
        """
        pathways = self.session.query(self.pathway_model).filter(self.pathway_model.name == pathway_name).all()

        if not pathways:
            return None

        return pathways[0]

    def get_all_pathways(self):
        """Gets all pathways stored in the database

        :rtype: list[Pathway]
        """
        return self.session.query(self.pathway_model).all()

    def get_all_hgnc_symbols(self):
        """Returns the set of genes present in all Pathways

        :rtype: set
        """
        return {
            gene.hgnc_symbol
            for pathway in self.get_all_pathways()
            for gene in pathway.proteins
            if pathway.proteins
        }

    def get_pathway_size_distribution(self):
        """Returns pathway sizes

        :rtype: dict
        :return: pathway sizes
        """

        pathways = self.get_all_pathways()

        return {
            pathway.name: len(pathway.proteins)
            for pathway in pathways
            if pathway.proteins
        }

    def query_pathway_by_name(self, query, limit=None):
        """Returns all pathways having the query in their names

        :param query: query string
        :param Optional[int] limit: limit result query
        :rtype: list[Pathway]
        """

        q = self.session.query(self.pathway_model).filter(self.pathway_model.name.contains(query))

        if limit:
            q = q.limit(limit)

        return q.all()

    def export_genesets(self):
        """Returns pathway - genesets mapping"""
        return {
            pathway.name: {
                protein.hgnc_symbol
                for protein in pathway.proteins
            }
            for pathway in self.session.query(self.pathway_model).all()
        }
