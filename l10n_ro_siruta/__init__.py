# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Fekete Mihai <mihai.fekete@forbiom.eu>
#    Copyright (C) 2014 FOREST AND BIOMASS SERVICES ROMANIA SA
#    (http://www.forbiom.eu).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from . import models

from . import models
from odoo import tools
import os


def post_init_hook(cr, registry):

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

    files = ['res.country.zone.csv','res.country.state.csv','res.country.commune.csv']
    for file in files:
        with tools.file_open(path + "/" + file, mode="rb") as fp:
            tools.convert_csv_import(
                cr, "base", file, fp.read(), {}, mode="init", noupdate=True,
            )

    cr.execute("""
    UPDATE res_city  
                SET commune_id = commune.id
            FROM
                res_country_commune as commune
            WHERE res_city.municipality = commune.name  
    """)

