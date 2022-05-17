{
    "name": "Estate",
    "version": "1.0",
    "category": "Real Estate/Brokerage",
    "sequence": 5,
    "depends": [
        "base",
        "project",
        "mail",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/estate_property_views.xml",
        "data/master_data.xml",
        "data/mail_data.xml",
        "views/res_users_inherit.xml",
        "report/estate_report_templates.xml",
        "report/estate_report_views.xml",
        "report/estate_users_templates.xml",
        "views/estate_menus.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "application": True,
}
