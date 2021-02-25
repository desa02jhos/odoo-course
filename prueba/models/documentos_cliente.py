# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CustomerDocument(models.Model):

    _name = 'cfs.customer.document'
    _description = 'Documentos de identidad asociados al cliente'
    _rec_name="c_idnumber"

    #Nombre completo del Cliente:
    # Es campo calculado =>
    # apellido paterno + apellido materno + nombre + descripción del tipo de doc. De identidad + número de documento de identidad.
    #name = fields.Char(string='Nombre Completo')
    
    #Ids de los documentos de idendidad del cliente
    #documentcatalog_ids = fields.Many2many(string='Tipo de Documento', comodel_name='plaft.documentcatalog', required=True)
    
    #Cliente
    customer_id = fields.Many2one(string=u'Cliente',comodel_name='cfs.customer',ondelete='cascade',)

    #Ids de los documentos de Identidad del cliente
    documentcatalog_ids = fields.Many2one(
        string=u'Tipo de Documento',
        comodel_name='cfs.plaft.documentcatalog',
        ondelete='set null', 
        domain=[('documentcategory_ids.c_acronym','=','DI')]
        )
    
    #Número de identidad del cliente
    c_idnumber = fields.Char(string='Número de Documento',required=True)

    #Fecha de Caducidad    
    date_expiration = fields.Date(string='Fecha de Caducidad')

    #Imagen del Documento
    bi_imagendocument = fields.Binary(string='Imagen de documento')
    

    #Observaciones
    t_remark = fields.Text(string='Observaciones')

    #Indica si el registro esta activo o no
    active = fields.Boolean(string='Activo?', default='True')

    # def typePerson(self):
    #     import pdb; pdb.set_trace()
    #     objCfsCustomer = self.env['cfs.customer'].search(['&',('c_customer_type','=','0'),('c_customer_type','=','1')])