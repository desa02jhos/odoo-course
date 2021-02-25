# -*- coding: utf-8 -*-

from odoo import models, fields, api


# Se crea el modulo cursos
class Partner(models.Model):
# Hereda automaticamente todos los datos o valores de los otros modelos como cursos y sesiones
    _inherit ='res.partner'

    instructor = fields.Boolean(default=False)
    session_ids = fields.Many2many('prueba.session', string="Attended Sessions", readonly=True)
    # Esto hace que las casillas se marquen
    other_field = fields.Boolean(default=True)
    other_field2 = fields.Boolean(default=True)
