import json

from odoo import http
from odoo.http import request
from datetime import datetime


class MedicalAppointment(http.Controller):

    @http.route(['/api/patient'], type="http", auth="none", website=True, method=['GET'],
                csrf=False)
    def get_infos(self, id):
        values = {}

        data = request.env['medical.patient'].sudo().search([("user_id", "=", int(id))])

        if data:
            values['status'] = 200
            details = []
            for rec in data:
                patient_details = {
                    "patient_id": rec.patient_id.id, "user_id": rec.user_id.id,
                    "name": rec.patient_id.name, "date_of_birth": str(rec.date_of_birth), "sex": rec.sex,
                    "critical_info": rec.critical_info, "receivable": rec.receivable, "insurance":
                        {
                            "current_insurance": rec.current_insurance_id.number,
                            "type": rec.current_insurance_id.type,
                            "member_since": str(rec.current_insurance_id.member_since),
                            "category": rec.current_insurance_id.category,
                            "company": rec.current_insurance_id.insurance_compnay_id.name,
                            "expiration": str(rec.current_insurance_id.member_exp),
                        }, "general_info": {
                        "blood_type": rec.blood_type,
                        "rh": rec.rh,
                        "medical_ethnicity": rec.medical_ethnicity_id.name,
                        "rh": rec.rh,
                        "marital_status": rec.marital_status,
                        "family_code": rec.family_code_id.name,
                        "deceased": rec.deceased
                    }
                }
                details.append(patient_details)

            values['details'] = patient_details
        else:
            values['success'] = False
            values['error_code'] = 1
            values['error_data'] = 'No data found!'

        return json.dumps(values)

    @http.route(['/api/patient/appointments'], type="http", auth="none", website=True, method=['GET'],
                csrf=False)
    def get_appointments(self, id):
        values = {}
        data = request.env['medical.appointment'].sudo().search([("patient_id", "=", int(id))])
        requests = request.env['medical.appointment.request'].sudo(). \
            search([("partner_id", "=", request.env['medical.patient'].sudo().
                     browse(int(id)).patient_id.id)])

        details = []
        appointments = {}
        if requests:
            values['status'] = 200
            for req in requests:
                appointment_requests = {
                    "name": req.name,
                    "request_date": str(req.request_date),
                    "desired_date": str(req.appointment_date),
                    "speciality": req.speciality_id.name,
                    "consultation_service": req.consultations_id.name,
                    "state": req.state,
                    "appointment_id": req.appointment_id.id,
                }
                details.append(appointment_requests)
            appointments["requests"] = details

        details = []
        if data:
            values['status'] = 200
            for rec in data:
                appointments_scheduled = {
                    "id": rec.id,
                    "name": rec.name,
                    "doctor": rec.doctor_id.partner_id.name,
                    "speciality": rec.speciality_id.name,
                    "appointment_date": str(rec.appointment_date),
                    "appointment_end": str(rec.appointment_end),
                    "invoice_exempt": rec.no_invoice,
                    "validity_status": rec.validity_status,
                    "validity_date": str(rec.appointment_validity_date),
                    "urgency_level": rec.urgency_level,
                    "consultation_service": rec.consultations_id.name,
                    "event_id": rec.event_id.id,
                    "request_id": rec.request_id.id,
                    "comments": rec.comments,
                    "conference_link": rec.event_id.attendee_link
                }
                details.append(appointments_scheduled)

            appointments["scheduled"] = details
            values['appointments'] = appointments
        if not requests and not data:
            values['status'] = 404
            values['error_code'] = 1
            values['error_data'] = 'No data found!'
        return json.dumps(values)

    @http.route(['/api/patient/appointment/request'], type="http", auth="none", website=True, method=['POST'],
                csrf=False)
    def post_appointment_request(self, **kwargs):
        values = {}
        if kwargs:
            if kwargs["partner_id"]:
                if kwargs["appointment_date"]:
                    if kwargs["speciality_id"]:
                        if kwargs["consultations_id"]:
                            if kwargs["comments"]:
                                values["partner_id"] = int(kwargs["partner_id"])
                                values["request_date"] = datetime.now()
                                values["appointment_date"] = datetime(kwargs["appointment_date"])
                                values["speciality_id"] = int(kwargs["speciality_id"])
                                values["consultations_id"] = int(kwargs["consultations_id"])
                                values["comments"] = int(kwargs["comments"])

        if values:
            result = request.env['medical.appointment.request'].sudo().create(values)
            return json.dumps({
                "status": 200,
                "message": "Appointment request submitted. Name: {}".format(result.name),
            })
        else:
            return json.dumps({
                "status": 400,
                "message": "Error while creating appointment request"
            })

        # @http.route(['/api/patient/info/update'], type="http", auth="none", website=True, method=['POST'],
        #             csrf=False)
        # def put_patient_infos(self, **kwargs):
        #     values = {}
        #     if kwargs:
