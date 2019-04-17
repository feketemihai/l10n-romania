# -*- coding: utf-8 -*-
# ©  2018 Terrabit
# See README.rst file on addons root folder for license details


from odoo import api, fields, models
from odoo.tools import safe_eval


class Declaration(models.Model):
    _inherit = "l10n_ro.declaration"

    code = fields.Selection(selection_add=[('D100', 'D100'), ('D300', 'D300'), ('D394', 'D394')])



