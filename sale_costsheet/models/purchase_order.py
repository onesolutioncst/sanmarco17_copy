from odoo import api, fields, models, _, SUPERUSER_ID, tools
import logging

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
DATES_FORMAT = "%Y-%m-%d"


class purchase_order(models.Model):
    _inherit = "purchase.order"

    def check_see_rfq(self, requisition_id):
        for record in requisition_id:
            for line_obj in record.line_ids:
                purchase_order_line_objs = self.env['purchase.order.line'].sudo().search([('purchase_requisition_line_id', '=', line_obj.id)])
                remaining_milestone_qty = sum(purchase_order_line_obj.product_qty for purchase_order_line_obj in purchase_order_line_objs)
                if line_obj.milestone_qty > remaining_milestone_qty:
                    return True
        return False


    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        if not self.requisition_id:
            return

        self = self.with_company(self.company_id)
        if not self.check_see_rfq(self.requisition_id):
            raise ValidationError(_("Sorry No Quantity to Invoice"))

        requisition = self.requisition_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.vendor_id
        payment_term = partner.property_supplier_payment_term_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.with_company(self.company_id)._get_fiscal_position(partner)

        self.partner_id = partner.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id
        self.company_id = requisition.company_id.id
        self.currency_id = requisition.currency_id.id
        if not self.origin or requisition.name not in self.origin.split(', '):
            if self.origin:
                if requisition.name:
                    self.origin = self.origin + ', ' + requisition.name
            else:
                self.origin = requisition.name
        self.notes = requisition.description
        self.date_order = fields.Datetime.now()

        if requisition.type_id.line_copy != 'copy':
            return

        # Create PO lines if necessary
        order_lines = []
        for line in requisition.line_ids:
            # Compute name
            product_lang = line.product_id.with_context(
                lang=partner.lang or self.env.user.lang,
                partner_id=partner.id
            )
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += '\n' + product_lang.description_purchase

            # Compute taxes
            taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id)).ids

            # Compute quantity and price_unit


            if line.product_uom_id != line.product_id.uom_po_id:
                product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.price_unit

            if requisition.type_id.quantity_copy != 'copy':
                product_qty = 0
            milestone_qty = line.milestone_qty
            purchase_order_line_objs = self.env['purchase.order.line'].sudo().search(
                [('purchase_requisition_line_id', '=', line.id)])
            done_milestone_qty = sum(
                purchase_order_line_obj.product_qty for purchase_order_line_obj in purchase_order_line_objs)
            product_qty = milestone_qty - done_milestone_qty
            # Create PO line
            if product_qty != 0:
                order_line_values = line._prepare_purchase_order_line(
                    name=name, product_qty=product_qty, price_unit=price_unit,
                    taxes_ids=taxes_ids)
                order_lines.append((0, 0, order_line_values))
        self.order_line = order_lines


class purchase_order_line(models.Model):
    _inherit = "purchase.order.line"

    purchase_requisition_line_id = fields.Many2one('purchase.requisition.line')