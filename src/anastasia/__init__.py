"""
Anastasia: A framework for adding temporal functionality to objects.

This package provides a comprehensive system for enabling time-travel capabilities
in Python objects through the use of descriptors, context managers, and decorators.

Classes:
    Anastasia: Main mixin class providing temporal functionality
    TemporalAttribute: Descriptor managing individual attribute history  
    TemporalValue: Wrapper enabling seamless value operations with snapshot access

Example:
    >>> from anastasia import Anastasia
    >>> import datetime
    >>> 
    >>> class Company(Anastasia):
    ...     @Anastasia.temporal_attribute
    ...     def credit_rating(self):
    ...         return "AAA"
    ...
    >>> company = Company()
    >>> company.credit_rating.set_snapshot("BB+")
    >>> timestamp = datetime.datetime.now()
    >>> company.credit_rating.set_snapshot("CCC")
    >>> with company.context(timestamp):
    ...     print(company.credit_rating)  # "BB+"
"""

from .anastasia import Anastasia, TemporalAttribute, TemporalValue

__version__ = "1.0.0"
__author__ = "Nick Ostermayer"
__email__ = "nick@nickostermayer.com"
__all__ = ["Anastasia", "TemporalAttribute", "TemporalValue"]