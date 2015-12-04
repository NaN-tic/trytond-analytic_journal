# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .journal import *
from .move import *
from .analytic import *

def register():
    Pool.register(
        Account,
        AnalyticLine,
        Journal,
        Move,
        module='analytic_journal', type_='model')
