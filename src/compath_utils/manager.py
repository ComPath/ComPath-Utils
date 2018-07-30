# -*- coding: utf-8 -*-

"""This module contains the abstract manager that all ComPath managers should extend."""

from collections import Counter
import itertools as itt
import logging
import os

from bio2bel import AbstractManager
import click
from compath_utils.exc import CompathManagerPathwayModelError, CompathManagerProteinModelError
from compath_utils.utils import write_dict

__all__ = [
    'CompathManager',
]

log = logging.getLogger(__name__)


class CompathManager(AbstractManager):
    """This is the abstract class that all ComPath managers should extend."""

    #: The standard pathway SQLAlchemy model
    pathway_model = None

    #: Put the standard database identifier (ex wikipathways_id or kegg_id)
    pathway_model_identifier_column = None

    #: The standard protein SQLAlchemy model
    protein_model = None

    def __init__(self, *args, **kwargs):
        """Doesn't let this class get instantiated if the pathway_model."""
        if self.pathway_model is None:
            raise CompathManagerPathwayModelError('did not set class-level variable pathway_model')

        # TODO use hasattr on class for checking this
        # if self.pathway_model_identifier_column is None:
        #     raise CompathManagerPathwayIdentifierError(
        #         'did not set class-level variable pathway_model_standard_identifer')

        if self.protein_model is None:
            raise CompathManagerProteinModelError('did not set class-level variable protein_model')

        super().__init__(*args, **kwargs)

    def is_populated(self):
        """Check if the database is already populated."""
        return 0 < self._count_model(self.pathway_model)

    def _query_proteins_in_hgnc_list(self, gene_set):
        """Return the proteins in the database within the gene set query.

        :param list[str] gene_set: hgnc symbol lists
        :return: list of proteins models
        """
        return self.session.query(self.protein_model).filter(self.protein_model.hgnc_symbol.in_(gene_set)).all()

    def query_protein_by_hgnc(self, hgnc_symbol):
        """Return the proteins in the database matching a hgnc symbol.

        :param str hgnc_symbol: hgnc symbol
        :return: Optional[models.Protein]
        """
        return self.session.query(self.protein_model).filter(
            self.protein_model.hgnc_symbol == hgnc_symbol).all()

    def query_similar_hgnc_symbol(self, hgnc_symbol, top=None):
        """Filter genes by hgnc symbol.

        :param str hgnc_symbol: hgnc_symbol to query
        :param int top: return only X entries
        :return: Optional[models.Pathway]
        """
        similar_genes = self.session.query(self.protein_model).filter(
            self.protein_model.hgnc_symbol.contains(hgnc_symbol)).all()

        if top:
            return similar_genes[:top]

        return similar_genes

    def query_similar_pathways(self, pathway_name, top=None):
        """Filter pathways by name.

        :param str pathway_name: pathway name to query
        :param int top: return only X entries
        :return: Optional[models.Pathway]
        """
        similar_pathways = self.session.query(self.pathway_model).filter(
            self.pathway_model.name.contains(pathway_name)).all()

        similar_pathways = [
            (pathway.resource_id, pathway.name)
            for pathway in similar_pathways
        ]

        if top:
            return similar_pathways[:top]

        return similar_pathways

    def query_gene(self, gene):
        """Return the pathways associated with a gene.

        :param str gene: HGNC gene symbol
        :rtype: dict[str,dict]
        :return: Optional[list] associated with the gene
        """
        genes = self.query_protein_by_hgnc(gene)

        if not genes:
            return None

        pathways_lists = [
            gene.get_pathways_ids()
            for gene in genes
        ]

        # Flat lists
        pathways_lists = itt.chain(*pathways_lists)

        enrichment_results = []

        for pathway_id in pathways_lists:
            pathway = self.get_pathway_by_id(pathway_id)

            pathway_gene_set = pathway.get_gene_set()  # Pathway gene set

            enrichment_results.append(
                (pathway_id, pathway.name, len(pathway_gene_set))
            )

        return enrichment_results

    def query_gene_set(self, gene_set):
        """Calculate the pathway counter dictionary.

        :param iter[str] gene_set: An iterable of HGNC gene symbols to be queried
        :rtype: dict[str,dict]
        :return: Enriched pathways with mapped pathways/total
        """
        proteins = self._query_proteins_in_hgnc_list(gene_set)

        pathways_lists = [
            protein.get_pathways_ids()
            for protein in proteins
        ]

        # Flat the pathways lists and applies Counter to get the number matches in every mapped pathway
        pathway_counter = Counter(itt.chain(*pathways_lists))

        enrichment_results = dict()

        for pathway_id, proteins_mapped in pathway_counter.items():
            pathway = self.get_pathway_by_id(pathway_id)

            pathway_gene_set = pathway.get_gene_set()  # Pathway gene set

            enrichment_results[pathway_id] = {
                "pathway_id": pathway_id,
                "pathway_name": pathway.name,
                "mapped_proteins": proteins_mapped,
                "pathway_size": len(pathway_gene_set),
                "pathway_gene_set": pathway_gene_set,
            }

        return enrichment_results

    @classmethod
    def _standard_pathway_identifier_filter(cls, pathway_id):
        """Get a SQLAlchemy filter for the standard pathway identifier.

        :param str pathway_id:
        """
        return cls.pathway_model_identifier_column == pathway_id

    def get_pathway_by_id(self, pathway_id):
        """Get a pathway by its database-specific identifier. Not to be confused with the standard column called "id".

        :param pathway_id: Pathway identifier
        :rtype: Optional[Pathway]
        """
        return self.session.query(self.pathway_model).filter(
            self._standard_pathway_identifier_filter(pathway_id)).one_or_none()

    def get_pathway_by_name(self, pathway_name):
        """Get a pathway by its database-specific name.

        :param pathway_name: Pathway name
        :rtype: Optional[Pathway]
        """
        pathways = self.session.query(self.pathway_model).filter(self.pathway_model.name == pathway_name).all()

        if not pathways:
            return None

        return pathways[0]

    def get_all_pathways(self):
        """Get all pathways stored in the database.

        :rtype: list[Pathway]
        """
        return self.session.query(self.pathway_model).all()

    def get_all_pathway_names(self):
        """Get all pathway names stored in the database.

        :rtype: list[str]
        """
        return [
            pathway.name
            for pathway in self.session.query(self.pathway_model).all()
        ]

    def get_all_hgnc_symbols(self):
        """Return the set of genes present in all Pathways.

        :rtype: set
        """
        return {
            gene.hgnc_symbol
            for pathway in self.get_all_pathways()
            for gene in pathway.proteins
            if pathway.proteins
        }

    def get_pathway_size_distribution(self):
        """Return pathway sizes.

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
        """Return all pathways having the query in their names.

        :param query: query string
        :param Optional[int] limit: limit result query
        :rtype: list[Pathway]
        """
        q = self.session.query(self.pathway_model).filter(self.pathway_model.name.contains(query))

        if limit:
            q = q.limit(limit)

        return q.all()

    def export_gene_sets(self):
        """Return the pathway - genesets mapping."""
        return {
            pathway.name: {
                protein.hgnc_symbol
                for protein in pathway.proteins
            }
            for pathway in self.session.query(self.pathway_model).all()
        }

    def get_gene_distribution(self):
        """Return the proteins in the database within the gene set query.

        :rtype: collections.Counter
        :return: pathway sizes
        """
        return Counter(
            gene.hgnc_symbol
            for pathway in self.get_all_pathways()
            if pathway.proteins
            for gene in pathway.proteins
        )

    @staticmethod
    def _add_cli_export(main):
        """Add the pathway export function to the CLI."""
        @main.command()
        @click.option('-d', '--directory', default=os.getcwd(), help='Defaults to CWD')
        @click.pass_obj
        def export_gene_sets(manager, directory):
            """Export all pathway - gene info to a excel file."""
            # https://stackoverflow.com/questions/19736080/creating-dataframe-from-a-dictionary-where-entries-have-different-lengths
            gene_sets_dict = manager.export_gene_sets()
            write_dict(gene_sets_dict, directory, manager.module_name)

        return main

    @classmethod
    def get_cli(cls):
        """Get a :mod:`click` main function to use as a command line interface.

        :rtype: click.core.Group
        """
        main = super().get_cli()
        cls._add_cli_export(main)
        return main
