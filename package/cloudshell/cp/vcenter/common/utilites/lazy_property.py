"""
@see  'memoized_property' SQLAlchemy SQLAlchemy-0.9.2-py2.7.egg!/sqlalchemy/util/langhelpers.py
as an example
"""


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
### NOT USED:
# class LazyProperty(object):
#     """ A read-only @property which evaluated only once.
#     """
#     def __init__(self, func, doc=None):
#         assert callable(func)
#         self.func = func
#         self.__doc__ = doc or func.__doc__
#         self.__name__ = func.__name__
#
#     def __get__(self, obj, _):
#         if obj is None:
#             return self
#         obj.__dict__[self.__name__] = result = self.func(obj)
#         return result
#
#     def _reset(self, obj):
#         LazyProperty.reset(obj, self.__name__)
#
#     @classmethod
#     def reset(cls, obj, name):
#         obj.__dict__.pop(name, None)
#
# lazy_property = LazyProperty
