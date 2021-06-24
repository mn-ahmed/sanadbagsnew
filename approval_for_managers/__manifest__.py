

{
  "name"                 :  "Approval For Managers",
  "summary"              :  "This Module add the approval of sale purchase and inventory",
  "category"             :  "sale, purchase, mrp",
  "version"              :  "13.0.0.0",
  "sequence"             :  1,
  "author"               :  "Viltco",
  "license"              :  "AGPL-3",
  "website"              :  "http://www.viltco.com",
  "description"          :  """

""",
  "live_test_url"        :  "",
  "depends"              :  [
                             'sale','purchase','mrp'
                            ],
    "data":  [
        # 'security/ir.model.access.csv',
        # 'views/approval_for_manager_groups.xml',
        'views/approval_for_manager_views.xml',
        ],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
}
