# -*- coding: utf-8 -*-

"""Tests errors thrown for improperly implemented ComPath managers."""

import unittest

from sqlalchemy.ext.declarative import declarative_base

from bio2bel.testing import TemporaryConnectionMethodMixin
from compath_utils import CompathManager, CompathManagerPathwayModelError, CompathManagerProteinModelError
from compath_utils.models import CompathPathway, CompathProtein

Base = declarative_base()


class ManagerMissingFunctions(CompathManager):
    """Test ComPath manager for abstract class."""

    module_name = 'test'

    @property
    def _base(self):
        return Base


class ManagerMissingPathway(ManagerMissingFunctions):
    """A bad implementation of a manager that is missing the pathway model."""

    def get_pathway_by_id(self, pathway_id):
        """Get a pathway by its database identifier."""
        pass

    def get_pathway_names_to_ids(self):
        """Get a dictionary from pathway names to their identifiers."""
        pass

    def populate(self, *args, **kwargs):
        """Populate the database."""
        pass

    def summarize(self):
        """Summarize the database."""
        pass

    def to_bel(self):
        """Export as BEL."""
        pass

    def query_gene_set(self, gene_set):
        """Find pathways with genes in the given set."""
        pass

    def _create_namespace_entry_from_model(self, model, namespace):
        """Create a namespace entry."""
        pass

    @staticmethod
    def _get_identifier(model):
        """Get the identifier from a model."""
        pass


class TestPathway(CompathPathway):
    """A test pathway class."""


class TestProtein(CompathProtein):
    """A test protein class."""


class ManagerMissingProtein(ManagerMissingPathway):
    """A bad implementation of a manager that is missing the protein model."""

    pathway_model = TestPathway


class ManagerOkay(ManagerMissingProtein):
    """An example of a good implementation of a manager."""

    protein_model = TestPathway


class TestManagerFailures(unittest.TestCase):
    """Tests bad implementations of the manager."""

    def test_abstract_methods(self):
        """Test a TypeError is thrown when required functions aren't implemented."""
        with self.assertRaises(TypeError):
            ManagerMissingFunctions()

    def test_pathway_model_error(self):
        """Test an error is thrown when the pathway model is not defined."""
        with self.assertRaises(CompathManagerPathwayModelError):
            ManagerMissingPathway()

    def test_protein_model_error(self):
        """Test an error is thrown when the protein model is not defined."""
        with self.assertRaises(CompathManagerProteinModelError):
            ManagerMissingProtein()


class TestManager(TemporaryConnectionMethodMixin):
    """Tests for good managers."""

    def test_instantiation(self):
        """Test that a good implementation of the manager can be instantiated."""
        ManagerOkay(connection=self.connection)
