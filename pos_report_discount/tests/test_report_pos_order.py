from odoo import fields
from odoo.tests.common import TransactionCase


class TestPosReportDiscount(TransactionCase):
    def setUp(self):
        super().setUp()
        self.PosOrder = self.env["pos.order"]
        self.pos_product = self.env.ref("point_of_sale.whiteboard_pen")
        self.pricelist = self.env.ref("product.list0")

        # Create a new pos config and open it
        self.pos_config = self.env.ref("point_of_sale.pos_config_main").copy()
        self.pos_config.open_session_cb()

    def test_discount(self):
        """Check in report discount value"""
        order = self._create_order()
        report = (
            self.env["report.pos.order"]
            .sudo()
            .search([("order_id", "=", order.id)], order="discount", limit=1)
        )
        self.assertEqual(report.discount, 10.0, "Must be equal 10.0")

    def _create_order(self):
        # Create order
        account_id = self.env.user.partner_id.property_account_receivable_id.id
        order_data = {
            "id": "0006-001-0010",
            "to_invoice": False,
            "data": {
                "pricelist_id": self.pricelist.id,
                "user_id": 1,
                "name": "Order 0006-001-0010",
                "partner_id": False,
                "amount_paid": 0.9,
                "pos_session_id": self.pos_config.current_session_id.id,
                "lines": [
                    [
                        0,
                        0,
                        {
                            "product_id": self.pos_product.id,
                            "price_unit": self.pos_product.list_price,
                            "qty": 10,
                            "price_subtotal": 18.0,
                            "discount": 10,
                            "price_subtotal_incl": 18.0,
                        },
                    ]
                ],
                "statement_ids": [
                    [
                        0,
                        0,
                        {
                            "payment_method_id": self.pos_config.payment_method_ids[
                                0
                            ].id,
                            "amount": 18.0,
                            "name": fields.Datetime.now(),
                            "account_id": account_id,
                            "session_id": self.pos_config.current_session_id.id,
                        },
                    ]
                ],
                "creation_date": "2023-06-15 00:51:03",
                "amount_tax": 0,
                "fiscal_position_id": False,
                "uid": "00001-001-0001",
                "amount_return": 0,
                "sequence_number": 1,
                "amount_total": 18.0,
            },
        }
        result = self.PosOrder.create_from_ui([order_data])
        order = self.PosOrder.browse(result[0].get("id"))
        return order
