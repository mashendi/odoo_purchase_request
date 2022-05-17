from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    request_id = fields.Many2one('purchase.request', string='Purchase Request', store=True)

    def action_view_purchase_request(self):
        return {
            'name': "Purchase Request",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'purchase.request',
            'target': 'current',
            'domain': [('id', '=', self.request_id.id)]
        }