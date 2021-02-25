# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Producto(models.Model):
 #Heredando variables a producto 
    _inherit ='product.template'
    # _name = 'prueba.producto' 
    product_info= fields.Char(string="Marca del Producto")
    description = fields.Text()


class Ventas(models.Model):

    _inherit = 'stock.picking'
    venta_info= fields.Char(string="Venta")
    resena= fields.Text()
    

    
