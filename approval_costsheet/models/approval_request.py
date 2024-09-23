from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging, json

from odoo.addons.test_convert.tests.test_env import record

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class approval_request(models.Model):
    _inherit = "approval.request"
    # _inherit = ['approval.request', 'analytic.mixin']

    mrp_production_id = fields.Many2one('mrp.production')
    suborder_production_id = fields.Many2one('mrp.production')
    agreement_production_id = fields.Many2one('purchase.requisition')
    from_mrp = fields.Boolean()

    has_analytic_distribution = fields.Selection(related="category_id.has_analytic_distribution")
    has_picking_type_id = fields.Selection(related="category_id.has_picking_type_id")
    has_location_src_id = fields.Selection(related="category_id.has_location_src_id")
    has_location_dest_id = fields.Selection(related="category_id.has_location_dest_id")
    has_vendor_id = fields.Selection(related="category_id.has_vendor_id")
    has_product_id = fields.Selection(related="category_id.has_product_id")
    has_product_qty = fields.Selection(related="category_id.has_product_qty")

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type')
    location_src_id = fields.Many2one('stock.location', 'Components Location')
    location_dest_id = fields.Many2one('stock.location', 'Finished Products Location')
    vendor_id = fields.Many2one('res.partner', 'Vendor')
    product_id = fields.Many2one('product.product', 'Product')
    product_qty = fields.Float('product_qty')

    analytic_distribution_text = fields.Text(company_dependent=True)
    analytic_distribution = fields.Json(inverse="_inverse_analytic_distribution", store=True)
    analytic_account_ids = fields.Many2many('account.analytic.account', compute="_compute_analytic_account_ids",
                                            copy=True)
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
    )


    @api.depends_context('company')
    @api.depends('analytic_distribution_text')
    def _compute_analytic_distribution(self):
        for record in self:
            record.analytic_distribution = json.loads(record.analytic_distribution_text or '{}')


    def _inverse_analytic_distribution(self):
        for record in self:
            record.analytic_distribution_text = json.dumps(record.analytic_distribution)


    @api.depends('analytic_distribution')
    def _compute_analytic_account_ids(self):
        for record in self:
            record.analytic_account_ids = bool(record.analytic_distribution) and self.env[
                'account.analytic.account'].browse(
                list({int(account_id) for ids in record.analytic_distribution for account_id in ids.split(",")})
            ).exists()

    def action_create_costsheet_suborder(self):
        manufacutre_lines = []
        for product_line_obj in self.product_line_ids:
            if product_line_obj.quantity > 0.0:
                manufacutre_lines.append((0, 0, {
                    'product_id': product_line_obj.product_id.id,
                    'product_uom_qty': product_line_obj.quantity
                }))
        if manufacutre_lines:
            if self.mrp_production_id:
                next_seq = self.env['mrp.production'].sudo().search_count(
                    [('mrp_production_id', '=', self.mrp_production_id.id)])
                name = self.mrp_production_id._get_name_backorder(self.mrp_production_id.name, next_seq + 1)
                origin = self.mrp_production_id.name +"/"+ str(self.name)
                mrp_production_id = self.mrp_production_id.id or ''
                product_id = self.mrp_production_id.product_id.id
                product_qty = self.mrp_production_id.product_uom_qty
            else:
                name = self.picking_type_id.sequence_id.next_by_id()
                origin = str(self.name)
                mrp_production_id = ''
                product_id = self.product_id.id
                product_qty = self.product_qty
            manufacutre_vals = {
                'name': name,
                'origin': origin,
                'mrp_production_id': mrp_production_id,
                'product_id': product_id,
                'product_qty': product_qty,
                'analytic_distribution': self.analytic_distribution,
                'picking_type_id': self.picking_type_id.id,
                'location_src_id': self.location_src_id.id,
                'location_dest_id': self.location_dest_id.id,
                'move_raw_ids': manufacutre_lines
            }
            mrp_production_obj = self.env['mrp.production'].sudo().create(manufacutre_vals)
            self.suborder_production_id = mrp_production_obj.id
            mrp_production_obj.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': mrp_production_obj, 'origin': self, 'edit': True},
                subtype_xmlid='mail.mt_note',
            )

    def action_create_costsheet_agreement(self):
        purchase_requisition = []
        for product_line_obj in self.product_line_ids:
            if product_line_obj.quantity > 0.0:
                purchase_requisition.append((0, 0, {
                    'product_id': product_line_obj.product_id.id,
                    'product_uom_qty': product_line_obj.quantity,
                    'analytic_distribution': self.analytic_distribution,
                }))
        if purchase_requisition:
            purchase_requisition_vals = {
                'vendor_id': self.partner_id.id,
                'origin': self.mrp_production_id.name,
                'mrp_production_id': self.mrp_production_id.id,
                'line_ids': purchase_requisition
            }
            if self.env['stock.picking.type'].sudo().search(
                    [('code', '=', 'incoming'),
                     ('warehouse_id', '=', self.mrp_production_id.sale_costsheet_id.warehouse_id.id)],
                    limit=1):
                purchase_requisition_vals.update({
                    'picking_type_id': self.env['stock.picking.type'].sudo().search(
                        [('code', '=', 'incoming'),
                         ('warehouse_id', '=', self.mrp_production_id.sale_costsheet_id.warehouse_id.id)],
                        limit=1).id
                })
            purchase_requisition_obj = self.env['purchase.requisition'].sudo().create(purchase_requisition_vals)
            self.agreement_production_id = purchase_requisition_obj.id
            purchase_requisition_obj.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': purchase_requisition_obj, 'origin': self.mrp_production_id, 'edit': True},
                subtype_xmlid='mail.mt_note',
            )
        return True


class approval_product_line(models.Model):
    _inherit = "approval.product.line"

    mrp_manufacture_line_id = fields.Many2one('stock.move', 'Components')
