# -*- coding: utf-8 -*-

from odoo import models, fields, api


# Se crea el modulo cursos
class Cliente(models.Model):
    _name = 'cliente.prueba'

    _inherit=['mail.thread']
    # Nos permite llamar los datos del res parnert y a la vez hace que el valor que se obtendra se guarde en el partner id, esto hace que se guarde el valor en el res.partner
    _inherits = { 'res.partner' : 'partner_id'}

    # customerdocument_ids = fields.One2many(string=u'Documentos de Identidad',comodel_name='cfs.customer.document',inverse_name='customer_id',track_visibility='onchange',)

    # Crear Cliente
    namecomplete = fields.Char(string='Nombre',store=False,compute="_get_complete_name",readonly=True,track_visibility='onchange',)
    c_lastname = fields.Char(string=u'Apellido Paterno',store=True,track_visibility='onchange',)
    c_motherlastname = fields.Char(string=u'Apellido Materno',store=True,track_visibility='onchange',)
    c_firstname = fields.Char(string=u'Nombres',store=True,track_visibility='onchange',)
    # Se obtiene los valores del res.partner (alverga los datos en el name)
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade', auto_join=True,track_visibility='onchange',)
    #Metodos Cliente
    #Union de datos del nombre
    @api.depends('c_firstname','c_lastname','c_motherlastname')
    def _get_complete_name(self):
        completename = ''
        if self.c_lastname:
            completename += str(self.c_lastname) + ' '
        if self.c_motherlastname:
                completename += str(self.c_motherlastname) + ' '
        if self.c_firstname:
            completename += str(self.c_firstname)
            
        self.namecomplete = str.strip(completename)
    
    # El valor se alverga en la variable name que es del res.partner esto que guarden en las dos tablas
    @api.onchange('namecomplete')   
    def _onchange_namecomplete(self):
        print(self.namecomplete)
        if str.strip(self.namecomplete) != None or '' or ' ':
            self.name = self.namecomplete
    
    #Menu de crear y guardar
    @api.model
    def create(self,vals):
        if vals.get('c_lastname',False) or vals.get('c_motherlastname',False) or vals.get('c_firstname', False):
            c_lastname = vals.get('c_lastname',False)
            c_motherlastname = vals.get('c_motherlastname',False)
            c_firstname = vals.get('c_firstname',False)

            vals.update({'c_lastname' : c_lastname.upper() if c_lastname != False else '',
                         'c_motherlastname' : c_motherlastname.upper()  if c_motherlastname != False else '',
                         'c_firstname' : c_firstname.upper() if c_firstname != False else '', 
                         })

        return super(Cliente,self).create(vals)

    #Aparece iconos en parte superior de la interfaz no son utilizables
     
    # subscribe = fields.Boolean(string='Esta Suscrito',default=False)
    # def action_subscribe(self):
    #     if(self.subscribe == False):
    #         self.subscribe = True
    #     else:
    #         self.subscribe = False


    #Tipo de Persona
    c_customer_type = fields.Selection(string='Tipo de cliente', selection=[('0', 'Pers. Natural'), ('1', 'Pers. Juridica'),],store=True,default='0',track_visibility='onchange',)

    @api.constrains('c_firstname','c_lastname')
    def _check_first_name(self):
        if self.c_customer_type == '0':
            fields = ['c_firstname','c_lastname']
            self._check_names(fields)



