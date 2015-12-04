#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelView
from trytond.pool import Pool, PoolMeta

__all__ = ['Move']
__metaclass__ = PoolMeta


class Move:
    __name__ = 'account.move'

    @classmethod
    @ModelView.button
    def post(cls, moves):
        pool = Pool()
        AnalyticLine = pool.get('analytic_account.line')
        to_create = []
        for move in moves:
            journal = move.journal or None
            if not journal or not journal.analytics:
                continue
            to_create += journal.set_analytic_lines(move)
        AnalyticLine.create([c._save_values for c in to_create])
        super(Move, cls).post(moves)


    @classmethod
    @ModelView.button
    def draft(cls, moves):
        super(Move, cls).draft(moves)
        for move in moves:
            journal = move.journal or None
            if not journal or not journal.analytics:
                continue
            journal.delete_analytic_lines(move)
