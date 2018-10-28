# -*- coding: utf-8 -*-

"""Tests errors thrown for improperly implemented ComPath managers."""

import unittest

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from bio2bel.testing import AbstractTemporaryCacheClassMixin
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


TABLE_PREFIX = 'test'
BAD_PATHWAY_TABLE_NAME = f'{TABLE_PREFIX}_bad_pathway'
PATHWAY_TABLE_NAME = f'{TABLE_PREFIX}_pathway'
PATHWAY_TABLE_HIERARCHY = f'{TABLE_PREFIX}_pathway_hierarchy'
BAD_PROTEIN_TABLE_NAME = f'{TABLE_PREFIX}_bad_protein'
PROTEIN_TABLE_NAME = f'{TABLE_PREFIX}_protein'
PROTEIN_PATHWAY_TABLE = f'{TABLE_PREFIX}_protein_pathway'

protein_pathway = Table(
    PROTEIN_PATHWAY_TABLE,
    Base.metadata,
    Column('protein_id', Integer, ForeignKey(f'{PROTEIN_TABLE_NAME}.id'), primary_key=True),
    Column('pathway_id', Integer, ForeignKey(f'{PATHWAY_TABLE_NAME}.id'), primary_key=True)
)


class BadTestProtein(Base):
    """A test protein class."""

    __tablename__ = BAD_PROTEIN_TABLE_NAME

    id = Column(Integer, primary_key=True)
    hgnc_symbol = Column(String(255), doc='HGNC gene symbol of the protein')


class TestProtein(CompathProtein, Base):
    """A test protein class."""

    __tablename__ = PROTEIN_TABLE_NAME
    id = Column(Integer, primary_key=True)
    hgnc_symbol = Column(String(255), doc='HGNC gene symbol of the protein')

class BadTestPathway(Base):
    """A test pathway class."""

    __tablename__ = BAD_PATHWAY_TABLE_NAME
    id = Column(Integer, primary_key=True)

class TestPathway(CompathPathway, Base):
    """A test pathway class."""

    __tablename__ = PATHWAY_TABLE_NAME
    id = Column(Integer, primary_key=True)

    test_id = Column(String(255), unique=True, nullable=False, index=True, doc='Test identifier of the pathway')
    name = Column(String(255), doc='pathway name')

    proteins = relationship(
        TestProtein,
        secondary=protein_pathway,
        backref='pathways'
    )


class ManagerMissingProtein(ManagerMissingPathway):
    """A bad implementation of a manager that is missing the protein model."""

    pathway_model = TestPathway


class ManagerBadProtein(ManagerMissingProtein):
    """An example of a manager with a bad protein."""

    protein_model = BadTestProtein


class ManagerOkay(ManagerMissingProtein):
    """An example of a good implementation of a manager."""

    protein_model = TestProtein


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

    def test_bad_protein_model_error(self):
        """Test an error is thrown when a bad protein model is defined."""
        with self.assertRaises(TypeError):
            ManagerBadProtein()


class TestManager(AbstractTemporaryCacheClassMixin):
    """Tests for good managers."""

    Manager = ManagerOkay
    manager: ManagerOkay

    @classmethod
    def populate(cls):
        """Populate the database."""
        p1, p2, p3, p4 = [
            TestProtein(hgnc_symbol=f'HGNC:{i}')
            for i in range(4)
        ]

        b1, b2 = [
            TestPathway(
                test_id=f'test:{i}',
                name=f'Pathway {i}',
            )
            for i in range(2)
        ]
        b1.proteins = [p1, p2, p3]
        b2.proteins = [p3, p4]

        cls.manager.session.add_all([p1, p2, p3, p4, b1, b2])
        cls.manager.session.commit()

    def test_counts(self):
        """Test counting content in the database."""
        self.assertEqual(4, self.manager.count_proteins())
        self.assertEqual(2, self.manager.count_pathways())
