# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import time
# Cursos crear - Responsable
#Se tiene que ingresar mediante la consola
# def get_uid(self, *a):
#     import pdb; pdb.set_trace()
#     return self.env.uid
#Ingreso directo
def get_uid(self, *a):
    return self.env.uid

# Se crea el modulo cursos
class Course(models.Model):
 _name = 'prueba.course'
 name = fields.Char(string="Title", required=True)
 description = fields.Text()
#  Se encarga de unir los datos junto con la otra table de modo que si se elimima el curso tambien se elimina la sesion
#  responsible_id= fields.Many2one('res.users', string ="Responsible", index=True, ondelete='set null', default=lambda self, *a: self.env.uid)
 responsible_id= fields.Many2one('res.users', string ="Responsible", index=True, ondelete='set null', default=get_uid)
 session_ids = fields.One2many('prueba.session', 'course_id')

 

# Se crear el modulo session
class Session(models.Model):
 _name = 'prueba.session'
 name = fields.Char(required=True)
 #  Automaticamente genera el codigo de la fecha
 start_date = fields.Date(default=fields.Date.today)
 datetime_test = fields.Datetime(default= fields.Datetime.now)
#  datetime_test = fields.Datetime(default= time.strftime('%Y-%m-%d %H:%M:%S'))
 duration = fields.Float(digits=(6, 2), help="Dias de Duracion")
 seats = fields.Integer(string="Numero de asientos")
#  Generacion de las tablas como no se puede de muchos a muchos se crea una tabla intermedia
 instructor_id= fields.Many2one('res.partner', string='Instructor', domain= ['|',('instructor', '=', True), ('category_id.name', 'ilike', 'Teacher')])
 course_id= fields.Many2one('prueba.course', ondelete='cascade', string="Course", required=True)
 attendee_ids = fields.Many2many('res.partner', string='Attendees')
 #Se encarga de que aparezca el cargando
 taken_seats = fields.Float(compute='_taken_seats')
 #Check Activar
 active = fields.Boolean(default=True)
 
 @api.depends('seats', 'attendee_ids')
 def _taken_seats(self):
    # for record in self.filtered(lambda r: r.seats):   
    #     record.taken_seats =100.0 * len(record.attendee_ids) / record.seats
    #   La pantalla se pone cargando y depende la cantidad de datos
    #  import pdb; pdb.set_trace()
     for record in self:
         if not record.seats:
             record.taken_seats = 0
         else:
             record.taken_seats =100.0 * len(record.attendee_ids) / record.seats

 #Establecer alertas en asientos como restricciones
 @api.onchange('seats', 'attendee_ids')
 def _verify_valid_seats(self):
     if self.filtered(lambda r: r.seats <0):
         self.active = False
         return {
                'warning' : {
                            'title' : "Incorrecto 'seats' value", 'message' : "El numero ingresado no es permitido",
                            }
                }
     if self.seats < len(self.attendee_ids):
         self.active = False
         return {
                'warning' : {
                            'title' : "Too many Attendees", 'message' : "Increase seats or remove excess attendees",
                            }
                }
         self.active = True
#  Alerta de poner a instructor como asistente
 @api.constrains('instructor_id', 'attendee_ids')
 def _check_instructor_not_in_attendees(self):
     for record in self.filtered('instructor_id'):
         if record.instructor_id in record.attendee_ids:
             raise exceptions.ValidationError("A session's instructor cant't be an attendee")
     


