from . import report
from . import wizards
from . import models

from odoo import api, SUPERUSER_ID, _, tools
import psycopg2


def _set_account_group(cr, registry):
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        try:
            with cr.savepoint():
                cr.execute("""
                update account_account as aa
                    set group_id = (select id from account_group as ag where  aa.code ilike  ag.code_prefix || '%' and ag.level = 3 );
                update account_account as aa
                    set group_id = (select id from account_group as ag where  aa.code ilike  ag.code_prefix || '%' and ag.level = 4 );
                update account_account as aa
                    set group_id = (select id from account_group as ag where  aa.code ilike  ag.code_prefix || '%' and ag.level = 5 );
                """)
        except psycopg2.Error:
            pass
        account_group = env['account.group'].search([], order = 'path desc')
        all_accounts = env['account.account'].search([])

        #for group in account_group:

        #     if grp.parent_id:
        #         path = grp.parent_id.path + " / " + grp.code_prefix or '0'
        #     else:
        #         path = grp.code_prefix or '0'
        #         if grp.code_prefix:
        #              account_ids = all_accounts.filtered(lambda a: a.code.startswith(grp.code_prefix))
        #              account_ids.write({'group_id': grp.id})
        #     if path != grp.path:
        #         grp.write({'path': path})
