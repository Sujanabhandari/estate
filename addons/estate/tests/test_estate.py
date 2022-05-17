from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import SavepointCase


# The CI will run these tests after all the modules are installed,
# not right after installing the one defining it.
@tagged("post_install", "-at_install")
class EstateTestCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        # add env on cls and many other things
        super().setUpClass()

        # create the data for each tests. By doing it in the setUpClass instead
        # of in a setUp or in each test case, we reduce the testing time and
        # the duplication of code.
        cls.partner_1 = cls.env["res.partner"].create({"name": "Sujana Bhandari"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "Bishal Pun"})
        cls.partner_3 = cls.env["res.partner"].create({"name": "Olivia Harlod"})
        cls.partner_4 = cls.env["res.partner"].create({"name": "Kaucha"})
        cls.property1 = cls.env["estate.property"].create(
            {
                "name": "Property test1",
                "state": "new",
                "description": "A nice and big property",
                "postcode": "8955",
                "date_availability": "2022-02-02",
                "expected_price": 21000,
                "bedrooms": 7,
                "type_id": cls.env.ref("estate.estate_property_type_1").id,
                "living_area": 78,
                "facades": 4,
                "garage": True,
                "garden": True,
                "garden_area": 785,
                "garden_orientation": "south",
                "offer_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.partner_1.id,
                            "price": 20000,
                            "validity_days": 14,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.partner_2.id,
                            "price": 289900,
                            "validity_days": 14,
                        },
                    ),
                ],
            }
        )

    # def test_creation_area(self):
    #     """Test that the total_area is computed like it should."""
    #     self.properties.living_area = 20
    #     self.assertRecordValues(self.properties, [
    #        {'name': ..., 'total_area': ...},
    #        {'name': ..., 'total_area': ...},
    #     ])

    def test_action_sell(self):
        """Test that everything behaves like it should when selling a property."""
        offer1 = self.property1.offer_ids[0]
        offer1.action_accepted()
        self.assertEqual(offer1.price, self.property1.selling_price)
        self.assertEqual(offer1.status, "accepted")
        self.assertEqual(offer1.partner_id, self.partner_1)
        self.assertEqual(self.property1.state, "offer_accepted")
        self.assertEqual(self.property1.state, "offer_accepted")
        self.property1.action_set_sold()
        self.assertEqual(self.property1.state, "sold")
        # self.assertRecordValues(self.properties, [
        #    {'name': ..., 'state': ...},
        #    {'name': ..., 'state': ...},
        # ])

        with self.assertRaises(UserError):
            self.env["estate.property.offer"].create(
                {
                    "property_id": self.property1.id,
                    "partner_id": self.partner_3.id,
                    "price": 89555555,
                }
            )
