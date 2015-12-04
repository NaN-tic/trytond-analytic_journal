#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['AnalyticLine']
__metaclass__ = PoolMeta


class AnalyticLine:
    __name__ = 'analytic_account.line'

    ## Allow to easily filter analytic lines by account.account
    account_account = fields.Function(fields.Many2One('account.account',
            'Move Line Account'), 'get_account_account',
        searcher='search_account_account')
    from_journal = fields.Boolean('Line created from Journal')

    @staticmethod
    def default_from_journal():
        return False

    def get_account_account(self, name):
        return (self.move_line and self.move_line.account and
            self.move_line.account.id or False)

    @classmethod
    def search_account_account(cls, name, clause):
        if clause[2]:
            lines = cls.search([
                    ('move_line.account', clause[1], clause[2]),
                    ])
            return [('id', 'in', [l.id for l in lines])]
        return
