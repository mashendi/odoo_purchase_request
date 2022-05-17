from odoo import models, fields, api


class PurchaseRequestLine(models.Model):
    _name = "purchase.request.line"
    _description = "Purchase request line"

    name = fields.Char(string="Description")
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="UoM",
        domain="[('category_id', '=', product_uom_category_id)]"
    )
    product_uom_category_id = fields.Many2one(
        related='product_id.uom_id.category_id')
    product_qty = fields.Float(
        string="Quantity", tracking=True, digits="Product Unit of Measure"
    )
    request_id = fields.Many2one(
        comodel_name="purchase.request",
        string="Purchase Request",
        ondelete="cascade",
        readonly=True,
        index=True,
        auto_join=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="request_id.company_id",
        string="Company",
        store=True,
    )
    vendor_id = fields.Many2one(
        comodel_name="res.partner",
        string="vendor",
        store=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain=[("purchase_ok", "=", True)],
        tracking=True,
    )
