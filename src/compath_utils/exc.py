# -*- coding: utf-8 -*-

__all__ = [
    'CompathManagerPathwayModelError',
]

class CompathManagerPathwayModelError(TypeError):
    """Raised when trying to instantiate a ComPath manager that hasn't been implemented with an appropriate
    pathway_model class variable"""
