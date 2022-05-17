from odoo import http


class Estate(http.Controller):
    @http.route("/estates", auth="public", website=True)
    def index(self, **kw):
        # Propertys is a variable for class for storing class.
        # env is a global variable ,which stores necessary global data for a database.
        Propertys = http.request.env["estate.property"]
        return http.request.render(
            "estate_website.index", {"propertys": Propertys.sudo().search([])}
        )

    @http.route(
        '/estate/<model("estate.property"):property>', auth="public", website=True
    )
    def estate(self, property):
        return http.request.render(
            "estate_website.description", {"propertyinfo": property.sudo()}
        )

    @http.route("/offer", auth="public", website=True)
    def offer_request(self, **kw):
        # kw is key-value variable where form data will be there.
        # Get offer class
        # prepare dict values for creation of offers.
        # Call create method
        # Return thankyou o
        Offer = http.request.env["estate.property.offer"]
        Partner = http.request.env["res.partner"]
        partner_id = Partner.sudo().create(
            {
                "company_type": "person",
                # the get() checks the key in dict and returns either empty or value
                # on the otherhand [] will give error if the key doesnt exist.
                "name": kw.get("fname") + kw.get("lname"),
                "phone": kw.get("phone"),
                "email": kw.get("email"),
            }
        )
        offer = Offer.sudo().create(
            {
                "partner_id": partner_id.id,
                "property_id": int(kw.get("property_id")),
                "price": float(kw.get("offer_price")),
            }
        )

        return http.request.render("estate_website.offer_thankyou", {"offer": offer})
