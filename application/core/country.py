"""
Nombres reales de campos por país para las consultas del ORM.

Los modelos de BR y US exponen alias en español (p.dni, p.apellido, etc.) que
sirven para leer y escribir atributos, pero filter(), order_by() y
select_related() necesitan el nombre real del campo. Este mapa concentra esas
diferencias para que las vistas tengan una sola rama de código.
"""
from django.conf import settings

_PROFILES = {
    'AR': {
        'patient_doctor': 'medico_asignado',
        'doctor_specialty': 'especialidad',
        'specialty_name': 'especialidad',
        'patient_search': ('dni', 'cuil', 'apellido', 'nombre', 'obra_social', 'diagnostico_clinico'),
        'patient_order': ('apellido', 'nombre'),
        'patient_insurance': 'obra_social',
        'doctor_search': ('matricula_nacional', 'apellido', 'nombre', 'dni'),
        'doctor_order': ('apellido', 'nombre'),
        'doctor_license': 'matricula_nacional',
        # Clave y campo del documento que se publica en /api/doctors/
        'doctor_doc': ('dni', 'dni'),
    },
    'BR': {
        'patient_doctor': 'medico_responsavel',
        'doctor_specialty': 'especialidade',
        'specialty_name': 'especialidade',
        'patient_search': ('cpf', 'rg', 'sobrenome', 'nome', 'convenio', 'diagnostico'),
        'patient_order': ('sobrenome', 'nome'),
        'patient_insurance': 'convenio',
        'doctor_search': ('crm', 'sobrenome', 'nome', 'cpf'),
        'doctor_order': ('sobrenome', 'nome'),
        'doctor_license': 'crm',
        'doctor_doc': ('cpf', 'cpf'),
    },
    'US': {
        'patient_doctor': 'assigned_doctor',
        'doctor_specialty': 'specialty',
        'specialty_name': 'specialty',
        'patient_search': ('ssn', 'state_id', 'last_name', 'first_name', 'insurance_provider', 'diagnosis'),
        'patient_order': ('last_name', 'first_name'),
        'patient_insurance': 'insurance_provider',
        'doctor_search': ('npi', 'last_name', 'first_name', 'ssn'),
        'doctor_order': ('last_name', 'first_name'),
        'doctor_license': 'npi',
        'doctor_doc': ('ssn', 'ssn'),
    },
}

PROFILE = _PROFILES[settings.HMS_COUNTRY]
