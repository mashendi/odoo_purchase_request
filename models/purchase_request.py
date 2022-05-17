from odoo import models, fields, api
from odoo.odoo.exceptions import UserError

_STATES = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed')
]

_READONLY_STATES = {'confirmed': [('readonly', True)]}


class PurchaseRequest(models.Model):
    _name = "purchase.request"
    _description = "Purchase Request"
    _order = "id desc"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("purchase.request")

    name = fields.Char(
        string="Reference",
        required=True,
        default="New",
        tracking=True,
        states=_READONLY_STATES
    )
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="draft",
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        tracking=True,
        states=_READONLY_STATES
    )
    creation_date = fields.Date(
        string="Created On",
        help="Date when the user initiated the request.",
        default=fields.Date.context_today,
        tracking=True,
        readonly=True
    )
    created_by = fields.Many2one(
        comodel_name="res.users",
        required=True,
        copy=False,
        default=_get_default_requested_by,
        readonly=True
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        required=True,
        copy=False,
        tracking=True,
        default=_get_default_requested_by,
        index=True,
        states=_READONLY_STATES
    )
    requested_on = fields.Date(
        string="Requested On",
        default=fields.Date.context_today,
        tracking=True,
        states=_READONLY_STATES
    )
    description = fields.Text()
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=False,
        default=_company_get,
        tracking=True,
        states=_READONLY_STATES
    )
    line_ids = fields.One2many(
        comodel_name="purchase.request.line",
        inverse_name="request_id",
        string="Products to Purchase",
        states=_READONLY_STATES,
        copy=True,
        tracking=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="line_ids.product_id",
        string="Product",
        readonly=True,
    )
    purchase_count = fields.Integer(
        string="Purchases count", compute="_compute_purchase_count", readonly=True
    )

    order_id = fields.One2many('purchase.order', 'request_id', string='Purchase Order')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request') or 'New'
        result = super(PurchaseRequest, self).create(vals)
        return result

    def write(self, vals):
        if any(state == 'confirmed' for state in set(self.mapped('state'))):
            raise UserError(_("No edit in confirmed state"))
        else:
            return super().write(vals)

    def _compute_purchase_count(self):
        for rec in self:
            rec.purchase_count = len(self.env['purchase.order'].search([('request_id', '=', rec.id)]))

    def action_view_purchase_order(self):
        return {
            'name': "Purchase Orders",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'target': 'current',
            'domain': [('request_id', '=', self.id)]
        }

    def _create_rfq(self):
        po_obj = self.env['purchase.order']
        vendors = self.mapped('line_ids.vendor_id')
        for vendor in vendors:
            po_order = po_obj.create({
                'partner_id': vendor.id,
                'date_order': self.requested_on,
                'company_id': self.env.user.company_id.id,
            })

            lines = self.env['purchase.request.line'].search(
                [('vendor_id', '=', vendor.id), ('request_id', '=', self.id)])
            line_ids = []
            for line in lines:
                price = line.product_id.standard_price
                line_ids.append((0, 0, {
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'price_unit': price,
                    'product_uom': line.product_uom_id.id,
                }))
            po_order.update({'order_line': line_ids, 'request_id': self.id})

    def button_confirmed(self):
        self._create_rfq()
        self.state = 'confirmed'
