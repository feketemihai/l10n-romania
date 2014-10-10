# -*- encoding: utf-8 -*-
##############################################################################
#
#   Master Data Management - made by atta
#
##############################################################################
{
    "name" : "Master Data Management",
    "version" : "*0.1 for v7",
    "author" : "Tatár Attila",
    "website": "",
    "category" : "Tools",
    #"sequence": 1,
    "depends" : [                                                       
                'base',
                ],
    "description": """
To Keep Master Data for other databases:
========================================
    - geographical data - zip codes Romania
    - legal - financial data - RO companies VAT information from official sites (mfinante.ro, static.anaf.ro)

    """,    
    "data" : [
              'vatonp_cronjob.xml',           
              ],
    "test" : [],
    "demo" : [],
    "auto_install": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

