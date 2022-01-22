# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
# <!--Marzouk IDRISSOU (educmarz@gmail.com)-->

from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError
import logging

logger = logging.getLogger(__name__)


class medical_appointment_request(models.Model):
    _name = "medical.appointment.request"
    _inherit = 'mail.thread'

    name = fields.Char(string="Appointment Request ID", readonly=True, copy=True)
    partner_id = fields.Many2one('res.partner', 'Applicant', required=True)
    request_date = fields.Datetime('Request Date', required=True, default=fields.Datetime.now(), readonly=True)
    appointment_date = fields.Datetime('Desired Appointment Date', required=True)
    speciality_id = fields.Many2one('medical.speciality', 'Speciality', required=True)
    consultations_id = fields.Many2one('product.product', 'Consultation Service', required=True)
    comments = fields.Text(string="Info")
    state = fields.Selection([('draft', 'Brouillon'), ('submit', 'Soumis'), ('cancel', 'Rejeté'), ('scheduled', 'Planifié')],
                             string="State", default='draft')
    appointment_id = fields.Many2one('medical.appointment', 'Consultation planifiée', readonly=True)

    @api.model
    def create(self, vals):
        vals['name'] = 'Demande N°{}|{}'.format(self.env['medical.appointment.request'].search([])[-1].id+1,
                                                  self.env["res.partner"].browse(vals['partner_id']).name)
        msg_body = 'Appointment Request created'
        self.message_post(body=msg_body)
        vals['state'] = 'submit'
        result = super(medical_appointment_request, self).create(vals)
        return result

    @api.multi
    def schedule(self, appointment_id):
        self.write({'state': 'scheduled'})
        self.write({'appointment_id': appointment_id})

    @api.multi
    def cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def create_appointment(self):
        # apt_req_obj = self.env['medical.appointment.request']
        # appointment_obj = self.env['medical.appointment']

        if self.state == 'scheduled':
            raise UserError(_(' Appointment already scheduled'))
        elif self.state == 'submit':
            patient_id = self.env['medical.patient'].search([("patient_id", "=", self.partner_id.id)])
            logger.info("\n---------------PATIENT_ID-------------------\n{}\n".format(patient_id.id))
            if len(patient_id) > 0:
                context = {
                    "default_model": 'medical.appointment.request',
                    "default_res_id": self.id,
                    "default_inpatient_registration_id": '',
                    "default_patient_id": patient_id[0].id,
                    "default_doctor_id": self.env['medical.physician'].search([("speciality_id",
                                                                              "=", self.speciality_id.id)])[0].id,
                    "default_speciality_id": self.speciality_id.id,
                    "default_appointment_date": self.appointment_date,
                    "default_consultations_id": self.consultations_id.id,
                    "default_request_id": self.id,
                }
                imd = self.env['ir.model.data']
                form_view_id = imd.xmlid_to_res_id('hospital_management.medical_appointment_form_view')
                result = {
                    'name': "Planification de la demande de consultation",
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'views': [(form_view_id, 'form')],
                    'target': 'new',
                    'context': context,
                    'res_model': 'medical.appointment',
                }

                return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
