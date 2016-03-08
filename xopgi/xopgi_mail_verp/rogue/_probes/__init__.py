# flake8:  noqa
'''Probes.

Probes must have a single ``__call__(self, message)``.  See the
'interfaces.py' file for document.

'''

# The router use the probes in the order given by __all__, so you may prefer a
# probe other another.
__all__ = [
    'NautaProbe',

    # Keep this at the bottom
    'FLUFLProbe',
]

from .nauta import NautaProbe
from .heuristics import FLUFLProbe
