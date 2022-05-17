from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class EstateProperty(models.Model):
    _name = "estate.property"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Estate property descriptions"
    _order = "id desc"

    name = fields.Char("Title", required=True, translate=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )

    description = fields.Text("Description")
    estate_image = fields.Binary(string="Product Image")
    property_description = fields.Html()
    postcode = fields.Char("Postcode")
    date_availability = fields.Date(
        "Avaialiable From",
        copy=False,
        default=lambda self: fields.Date.today() + timedelta(days=90),
    )
    type_id = fields.Many2one("estate.property.type", string="Property Type")
    partner_id = fields.Many2one("res.partner", string="Buyer")
    user_id = fields.Many2one(
        "res.users",
        string="Salesman",
        tracking=True,
        default=lambda self: self.env.user,
    )
    tag_ids = fields.Many2many("estate.property.tag", string="Property Tags")
    offer_ids = fields.One2many(
        "estate.property.offer", "property_id", string="Property Offer"
    )
    expected_price = fields.Float("Expected Price", required=True)
    selling_price = fields.Float("Selling Price", readonly=True, copy=False)
    best_price = fields.Float(compute="_compute_offer")
    bedrooms = fields.Integer("Bedrooms", default=2)
    living_area = fields.Integer("Living Area")
    facades = fields.Integer("Facades")
    garage = fields.Boolean("Garage")
    garden = fields.Boolean("Garden")
    garden_area = fields.Integer("Gareden area")
    total_area = fields.Integer(compute="_compute_total")
    amount = fields.Float()
    address_id = fields.Many2one(
        "res.partner",
        "Address",
        help="Enter here the private of a property",
        groups="estate.estate_group_user",
        tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
        help="To select the Garden Orientation",
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        copy=False,
        default="new",
        required=True,
        string="States",
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
    )
    city = fields.Char("City")
    postal = fields.Integer("Zip")
    street = fields.Char("Street")

    _sql_constraints = [
        (
            "expected_pricecheck",
            "CHECK(expected_price > 0)",
            "A property expected price must be strictly positive",
        ),
        (
            "selling_pricecheck",
            "CHECK(selling_price >= 0)",
            "A property selling price must be positive",
        ),
    ]

    def unlink(self):
        for record in self:
            if record.state not in ["new", "cancelled"]:
                raise UserError("Only new and cancelled items can be deleted.")
        return super().unlink()

    @api.constrains("expected_price", "selling_price")
    def _check_acceptprice(self):
        for record in self:
            calculated_price = record.expected_price * 0.9
            for offers in record.offer_ids:
                if offers.status == "accepted":
                    if float_compare(record.selling_price, calculated_price, 2) < 0:
                        raise ValidationError(
                            "The selling price cannot be lower"
                            + "than 90% of the expected price."
                        )

    @api.depends("garden_area", "living_area")
    def _compute_total(self):
        for record in self:
            record.total_area = record.garden_area * record.living_area

    @api.depends("offer_ids.price")
    def _compute_offer(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_set_sold(self):
        self.ensure_one()
        if self.state == "cancelled":
            raise UserError("Cancelled properties cannot be sold.")
        elif self.state != "offer_accepted":
            raise UserError("Please accept offer before selling.")
        self.state = "sold"

    def action_set_cancel(self):
        self.ensure_one()
        if self.state == "sold":
            raise UserError("Sold properties cannot be cancelled.")
        self.state = "cancelled"

    # this function will get required fields and concatinate them in address field
    @api.depends("store_id")
    def _compute_address(self):
        for rec in self:
            res = [
                rec.store_id.street,
                rec.store_id.street2,
                rec.store_id.city,
                rec.store_id.zip,
            ]
            self.address = ", ".join(filter(bool, res))

    def action_offer_accepted_send(self):

        self.ensure_one()
        template_id = self.env["ir.model.data"].xmlid_to_res_id(
            "estate.email_template_offer_accepted", raise_if_not_found=False
        )
        ctx = {
            "default_model": "estate.property",
            "default_res_id": self.ids[0],
            "default_use_template": bool(template_id),
            "default_template_id": template_id,
            "default_composition_mode": "comment",
            "force_email": True,
            "model_description": "Estate Property",
        }
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "view_id": False,
            "target": "new",
            "context": ctx,
        }

    def action_offer_refused_send(self):

        self.ensure_one()
        # template_id = self._find_mail_template()
        template_id = self.env["ir.model.data"].xmlid_to_res_id(
            "estate.email_template_offer_refused", raise_if_not_found=False
        )
        values = {
            "model": "estate.property",
            "res_id": self.ids[0],
            "template_id": template_id,
            "composition_mode": "comment",
        }
        mail = (
            self.env["mail.compose.message"]
            .with_context(force_email=True, model_description="Estate Property")
            .create(values)
        )
        # If you call create method then please look for
        # onchange decorator and call that function manually
        mail.onchange_template_id_wrapper()
        mail.send_mail()


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate property type descriptions"
    _order = "name"

    name = fields.Char("Title", required=True, translate=True)
    _sql_constraints = [
        ("property_name_uniq", "UNIQUE (name)", "A property type name must be unique")
    ]

    sequence = fields.Integer(
        "Sequence", default=1, help="Used to order stages. Lower is better."
    )
    property_ids = fields.One2many("estate.property", "type_id", string="Properties")
    offer_ids = fields.One2many(
        "estate.property.offer", "property_type_id", string="Offers"
    )
    offer_count = fields.Integer("Offer Counts", compute="_compute_offers")

    @api.depends("offer_ids")
    def _compute_offers(self):
        for record in self:
            record.offer_count = len(record.offer_ids)


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate property tag"
    _order = "name"

    name = fields.Char("Title", required=True, translate=True)
    _sql_constraints = [
        ("tag_name_uniq", "UNIQUE (name)", "A property tag name must be unique")
    ]
    color = fields.Integer("Color")


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate property offer"
    _order = "price desc"

    price = fields.Float("Price", required=True)
    validity_days = fields.Integer("Validity", default=7)
    date_deadline = fields.Date("Deadline", compute="_compute_deadline")
    status = fields.Selection(
        selection=[("accepted", "Accepted"), ("refused", "Refused")], copy=False
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    property_type_id = fields.Many2one(
        "estate.property.type", related="property_id.type_id", store=True
    )

    _sql_constraints = [
        (
            "price_pricecheck",
            "CHECK(price > 0 )",
            "Offer price must be strictly positive",
        ),
    ]

    @api.model
    def create(self, vals):
        property_id = self.env["estate.property"].browse(vals["property_id"])
        if property_id.state == "sold":
            raise UserError("Offer cannot be created for sold property.")
        property_id.state = "offer_received"
        if vals.get("price", 0) < property_id.best_price:
            raise UserError("Offer cannot be created")
        return super().create(vals)

    def action_accepted(self):
        self.ensure_one()
        # Set status of already accepted offer to refused
        if self.property_id.state == "offer_accepted":
            raise UserError(
                "Only one offer can be accepted please refuse the previous offer"
            )

        self.write({"status": "accepted"})
        self.property_id.write(
            {
                "selling_price": self.price,
                "partner_id": self.partner_id.id,
                "state": "offer_accepted",
            }
        )
        return self.property_id.action_offer_accepted_send()

    def action_refused(self):
        self.ensure_one()
        self.write({"status": "refused"})
        self.property_id.write({"state": "offer_received"})
        return self.property_id.action_offer_refused_send()

    @api.depends("create_date", "validity_days")
    def _compute_deadline(self):
        for record in self:
            create_date = fields.Date.today()
            if record.create_date:
                create_date = record.create_date
            record.date_deadline = (
                timedelta(days=int(record.validity_days)) + create_date
            )
