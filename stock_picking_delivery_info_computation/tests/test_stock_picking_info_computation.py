# -*- coding: utf-8 -*-
# Copyright 2019 Tecnativa - Victor M.M. Torres
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.sale.tests.test_sale_common import TestSale


class TestStockPickingInfoComputation(TestSale):
    def setUp(self):
        super(TestStockPickingInfoComputation, self).setUp()
        self.product_uom_unit = self.env.ref('product.product_uom_unit')
        self.product_category_5 = self.env.ref('product.product_category_5')
        self.product_pricelist_0 = self.env.ref('product.list0')
        self.product_a = self.env['product.product'].create({
            'name': 'Test product A',
            'type': 'consu',
            'weight': 0.3,
            'volume': 0.02,
        })
        self.product_b = self.env['product.product'].create({
            'name': 'Test product B',
            'type': 'consu',
            'weight': 0.25,
            'volume': 0.03,
        })

        self.sale_test = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'pricelist_id': self.product_pricelist_0.id,
            'order_line': [
                (0, 0, {
                    'name': 'Bose Mini Bluetooth Speaker',
                    'product_id': self.product_a.id,
                    'product_uom_qty': 2,
                    'product_uom': self.product_uom_unit.id,
                    'price_unit': 300.00,
                }),
                (0, 0, {
                    'name': 'iPad Mini',
                    'product_id': self.product_b.id,
                    'product_uom_qty': 5,
                    'product_uom': self.product_uom_unit.id,
                    'price_unit': 390.00,
                })
            ],
            'picking_policy': 'direct',
        })

    def test_weight_volume_initial(self):
        # Test weight and volume function
        # over an stock.picking with initial demand
        self.sale_test.action_confirm()
        self.sale_test.picking_ids.ensure_one()
        self.sale_test.picking_ids.do_unreserve()
        self.assertFalse(self.sale_test.picking_ids.pack_operation_product_ids)
        for picking in self.sale_test.picking_ids:
            self.assertEqual(picking.volume, 0.0)
            self.assertEqual(picking.weight, 1.85)
            picking.action_calculate_volume()
            self.assertEqual(picking.volume, 0.19)

    def test_weight_volume_todo(self):
        # Test weight and volume funtcion
        # over an stock.picking with pack operation to do
        # self.sale_test.action_confirm()
        self.sale_test.action_confirm()
        self.sale_test.picking_ids.ensure_one()
        for picking in self.sale_test.picking_ids:
            self.assertEqual(picking.volume, 0.0)
            self.assertEqual(picking.weight, 1.85)
            picking.action_calculate_volume()
            self.assertEqual(picking.volume, 0.19)

    def test_weight_volume_with_reserved_qty(self):
        # Test weight and volume funtcion over an stock.picking
        # with just one pack operation done qty
        self.sale_test.action_confirm()
        self.sale_test.picking_ids.ensure_one()
        for picking in self.sale_test.picking_ids:
            self.assertEqual(picking.volume, 0.0)
            self.assertEqual(picking.weight, 1.85)
            picking.action_calculate_volume()
            self.assertEqual(picking.volume, 0.19)
        operations = self.sale_test.picking_ids.pack_operation_product_ids
        operations[0].write({'qty_done': 1})
        self.sale_test.picking_ids.write({
            'pack_operation_product_ids': [(6, 0, operations.ids)]
        })
        for picking in self.sale_test.picking_ids:
            self.assertEqual(picking.weight, 0.3)
            picking.action_calculate_volume()
            self.assertEqual(picking.volume, 0.02)
