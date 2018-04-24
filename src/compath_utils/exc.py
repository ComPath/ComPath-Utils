# -*- coding: utf-8 -*-

__all__ = [
    'CompathManagerPathwayModelError',
    'CompathManagerPathwayIdentifierError',
    'CompathManagerProteinModelError',
]


class CompathManagerPathwayModelError(TypeError):
    """Raised when trying to instantiate a ComPath manager that hasn't been implemented with an appropriate
    pathway_model class variable"""


class CompathManagerPathwayIdentifierError(TypeError):
    """Raised when trying to instantiate a ComPath manager that hasn't been implemented with an appropriate
    pathway_model_standard_identifer class variable"""


class CompathManagerProteinModelError(TypeError):
    """Raised when trying to instantiate a ComPath manager that hasn't been implemented with an appropriate
    protein_model class variable"""
