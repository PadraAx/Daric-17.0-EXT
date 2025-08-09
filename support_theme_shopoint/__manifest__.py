# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Support Theme Shopoint",
  "category"             :  "Theme",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "description"          :  """Support Shopoint theme""",
  "depends"              :  [
                             'website_sale',
                             'website_sale_wishlist',
                             'website_sale_comparison_wishlist',
                            ],
  "data"                 :  [
                             'views/product_attributes.xml',
                            ],
  "demo"                 :  [],
  "assets"               :  {
                              "website.assets_frontend": [
                                "support_theme_shopoint/static/src/scss/website_sale_recommended_prodcuts.scss",
                              ],
                            },
  "images"               :  [
                             'static/description/Banner.png',
                             'static/description/main_screenshot.png',
                            ],
  "application"          :  False,
  "installable"          :  True,
  "price"                :  0,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
