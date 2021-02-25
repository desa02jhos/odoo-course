# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare
from werkzeug.urls import url_encode


# Se crea el modulo cursos
class Cotizacion(models.Model):
    _name = 'cotizacion.prueba'
    # _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    # _description = "Quotion"
    # _order = 'date_order desc, id desc'
    # _check_company_auto = True

    _inherit=['mail.thread']
    _description = "Registro de Cotizacion de Envios de Remesa"



    # name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    # date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    # commitment_date = fields.Datetime('Delivery Date',
    #                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
    #                                   copy=False, readonly=True,
    #                                   help="This is the delivery date promised to the customer. "
    #                                        "If set, the delivery order will be scheduled based on "
    #                                        "this date rather than product lead times.")
    # expected_date = fields.Datetime("Expected Date", compute='_compute_expected_date', store=False,  # Note: can not be stored since depends on today()
    #     help="Delivery date you can promise to the customer, computed from the minimum lead time of the order lines.")
    # partner_id = fields.Many2one(
    #     'res.partner', string='Customer', readonly=True,
    #     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
    #     required=True, change_default=True, index=True, tracking=1,
    #     domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)




   

   
    
   
    
    

    # def action_unlock(self):
    #     self.write({'state': 'sale'})

   



   

    # def _create_analytic_account(self, prefix=None):
    #     for order in self:
    #         analytic = self.env['account.analytic.account'].create(order._prepare_analytic_account_data(prefix))
    #         order.analytic_account_id = analytic

   

    # def action_done(self):
    #     for order in self:
    #         tx = order.sudo().transaction_ids.get_last_transaction()
    #         if tx and tx.state == 'pending' and tx.acquirer_id.provider == 'transfer':
    #             tx._set_transaction_done()
    #             tx.write({'is_processed': True})
    #     return self.write({'state': 'done'})

    # def has_to_be_signed(self, include_draft=False):
    #     return (self.state == 'sent' or (self.state == 'draft' and include_draft)) and not self.is_expired and self.require_signature and not self.signature

    # def has_to_be_paid(self, include_draft=False):
    #     transaction = self.get_portal_last_transaction()
    #     return (self.state == 'sent' or (self.state == 'draft' and include_draft))

    
    customer_id = fields.Many2one(comodel_name='cliente.prueba', string='Cliente')
    customer_beneficiary = fields.Many2one(comodel_name='cliente.prueba',string='Cliente Beneficiario')
    # bpstagestate_id = fields.Many2one(comodel_name='cfs.bp.stage.state', string='Estado de etapa',track_visibility="onchange")
    
    
    
    
    #Estado General
    state = fields.Selection([
         ('draft', 'Cotizar'),
        ('sent', 'Presupueto Enviado'),
         ('valid', 'Validar Documentos'),
         ('sale', 'Sales Order'),
         ('done', 'Locked'),
         ('cancel', 'Cancelled'),
         ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    @api.depends('state')
    def _compute_type_name(self):
        for record in self:
            record.type_name = _('Cotizar') if record.state in ('draft', 'sent', 'valid', 'cancel') else _('Sales Order')


    #Cancela la Cotizacion
    def action_cancel(self):
        return self.write({'state': 'cancel'})




    #Enviar Email

    type_name = fields.Char('Type Name', compute='_compute_type_name')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True)

    #Genera Email
    def _find_mail_template(self, force_confirmation_template=False):
        template_id = False

        if force_confirmation_template or (self.state == 'sale' and not self.env.context.get('proforma', False)):
            template_id = int(self.env['ir.config_parameter'].sudo().get_param('sale.default_confirmation_template'))
            template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
            if not template_id:
                template_id = self.env['ir.model.data'].xmlid_to_res_id('sale.mail_template_sale_confirmation', raise_if_not_found=False)
        if not template_id:
            template_id = self.env['ir.model.data'].xmlid_to_res_id('sale.email_template_edi_sale', raise_if_not_found=False)

        return template_id
    #Envia emal
    def action_quotation_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self._find_mail_template()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_template(template.lang, 'cotizacion.prueba', self.ids[0])
        ctx = {
            'default_model': 'cotizacion.prueba',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
    
    def _send_order_confirmation_mail(self):
        if self.env.su:
            # sending mail in sudo was meant for it being sent from superuser
            self = self.with_user(SUPERUSER_ID)
        template_id = self._find_mail_template(force_confirmation_template=True)
        if template_id:
            for order in self:
                order.with_context(force_send=True).message_post_with_template(template_id, composition_mode='comment', email_layout_xmlid="mail.mail_notification_paynow")
    
    # URL - Confirmar envio
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    def preview_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    def _get_share_url(self, redirect=False, signup_partner=False, pid=None):
        self.ensure_one()
        if self.state not in ['sale', 'done']:
            auth_param = url_encode(self.partner_id.signup_get_auth_param()[self.partner_id.id])
            return self.get_portal_url(query_string='&%s' % auth_param)
        return super(Cotizacion, self)._get_share_url(redirect, signup_partner, pid)

    def _compute_access_url(self):
        super(Cotizacion, self)._compute_access_url()
        for order in self:
            order.access_url = '/my/orders/%s' % (order.id)

    #Confirmar
    def _action_confirm(self):
        for order in self:
            if any([expense_policy not in [False, 'no'] for expense_policy in order.order_line.mapped('product_id.expense_policy')]):
                if not order.analytic_account_id:
                    order._create_analytic_account()
        return True

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_('It is not allowed to confirm an order in the following states: %s') % (', '.join(self._get_forbidden_state_confirm())))
    
    def _get_forbidden_state_confirm(self):
        return {'done', 'cancel'}

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })






    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel', 'sent'])
        return orders.write({
            'state': 'draft',
            'signature': False,
            'signed_by': False,
            'signed_on': False,
        })
    
    # def checkPLAFTControlThreshold(self,finalamount):
    #     single = self.checkPLAFTSingleOperation(finalamount)
    #     acumulated = self.checkPLAFTMultipleOperation(self.customer_id,self.customer_payer,self.customer_beneficiary,finalamount)
    #     if(acumulated is not None):
    #         if single != False and acumulated <= 0:
    #             objRo = self.env['cfs.plaft.ro.declaration'].createRoDeclaration(self.customer_id,self.customer_payer,self.customer_beneficiary,self,acumulated,1)
    #         elif acumulated > 0 and single != True:
    #             objRo = self.env['cfs.plaft.ro.declaration'].createRoDeclaration(self.customer_id,self.customer_payer,self.customer_beneficiary,self,acumulated,2)
    #         elif single != False and acumulated > 0:
    #             objRo = self.env['cfs.plaft.ro.declaration'].createRoDeclaration(self.customer_id,self.customer_payer,self.customer_beneficiary,self,acumulated,3)
    #         else: 
    #             objRo = False
    #     else:
    #         objRo = False
    #     if(objRo != False):
    #         self.ro_declaration_id = objRo

    # def checkPLAFTSingleOperation(self,finalamount):
    #     objThreshold = self.env['cfs.plaft.controlthreshold'].search(['&',('businessline_id','=',1),'&',('s_control_type','=','U'),'&',('amount_min','<=',finalamount),('amount_max','>=',finalamount)])
    #     objCustomerDocs = self.env['cfs.moex.quote.customer.doc']
    #     if(objThreshold != False):
    #         self.CreateRO('S')
    #         requirements = objThreshold.threshold_req_ids  #categorias 
    #         for record in requirements:
    #                 objCustomerDocs.sudo().create({
    #                 'documentcategory_id' : record.id,
    #                 'quote_id' : self.id})        
    #         return True
            
    # def checkPLAFTMultipleOperation(self,obj_customer,obj_payer,obj_beneficiary,finalamount):
    #     objThreshold = self.env['cfs.plaft.controlthreshold'].search(['&',('businessline_id','=',1),('s_control_type','=','M')])
    #     if(objThreshold != False):
    #         for record in objThreshold:
    #             timeframe = record.s_time_frame_type #Tipo de periodo de tiempo
    #             itimeframe = record.i_time_frame #Periodo en dias
    #             if(timeframe == 'cal'):
    #                 date = datetime.now()
    #                 start_date = datetime(date.year,date.month,1)
    #                 end_date = datetime(date.year, date.month, calendar.mdays[date.month])
                   
    #             elif(timeframe == 'cro'):
    #                 date = datetime.now()
    #                 start_date = datetime(date.year,date.month,date.day)
    #                 end_date = start_date - timedelta(days= itimeframe)
                    
    #             objPayOrder = self.env['treasury.payment.paymentorder.moex'].search(['&','|',('reference_performer_id','=',obj_customer.id),
    #             '|',('reference_performer_id','=',obj_payer.id),('reference_beneficiary_id','=',obj_beneficiary.id),'&',
    #             ('date_paymentorder','>=',start_date.strftime('%Y-%m-%d')),('date_paymentorder','<=',end_date.strftime('%Y-%m-%d'))])

    #             totalamountpayorder = sum(item.reference_amount_received_equivalent for item in objPayOrder)
    #             acumulatedpayorder = totalamountpayorder + finalamount
    #             if(acumulatedpayorder >= record.amount_min and acumulatedpayorder <= record.amount_max):
                    
    #                 self.CreateRO('M')  
    #                 objThreshold = self.env['cfs.plaft.controlthreshold'].search(['&',('s_control_type','=','M'),'&',('businessline_id','=',1),'&',('amount_min','<=',acumulatedpayorder),('amount_max','>=',acumulatedpayorder)])
    #                 objCustomerDocs = self.env['cfs.moex.quote.customer.doc']
    #                 if(objThreshold != False):
    #                     requirements = objThreshold.threshold_req_ids  #categorias 
    #                     for record in requirements:
    #                         objCustomerDocs.sudo().create({
    #                         'documentcategory_id' : record.id,
    #                         'quote_id' : self.id})             
    #                     return acumulatedpayorder
    #             else:
    #                 return False

    # def checkComercialThreshold(self,finalamount):
    #     commercialthreshold = self.env['cfs.commercial.threshold'].search(['&',('active','=',True),'&',('amount_minimum','<=',finalamount),'&',('amount_maximum','>=',finalamount),('b_authorization','=',True)])
    #     if(commercialthreshold.id != False): 
    #         return True
    #     else:
    #         return False


    # @api.multi
    # def getCustomerDocs(self,finalamount):
    #     objThreshold = self.env['plaft.control.threshold'].search(['&',('businessline_id','=',1),'&',('amount_min','<=',finalamount),('amount_max','>=',finalamount)])
    #     arrayThreshold = []
    #     if(len(objThreshold) != 0):
    #         for threshold in objThreshold:
    #             arrayThreshold.append(threshold)
    #         requirements = arrayThreshold
    #         return requirements
    #     else:
    #         requirements = []
    #         return requirements

    # def action_enroll_documents(self):
    #     documents = self.customerdocument_ids
    #     if (len(documents)>0):       
    #         for document in documents:
    #             if(document.documentcatalog_id.id != False and len(self.paymentinstruction_ids) != 0):
    #                 self.write({
    #                     'bpstagestate_id' : 9
    #                 })
    #             else:
    #                 raise ValidationError('Ingrese documentos o instrucciones de pago del cliente')
    #     else:
    #         if(len(self.paymentinstruction_ids) != 0):
    #            self.action_schedule_payment()
    #         else:
               
    #             raise ValidationError('Ingrese instrucciones de pago del cliente')
