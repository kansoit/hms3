"""
Modelos activos según el país configurado (settings.HMS_COUNTRY, ya validado).
El resto de la app importa siempre Especialidad, Medico y Paciente desde acá.
"""
from django.conf import settings

HMS_COUNTRY = settings.HMS_COUNTRY

if HMS_COUNTRY == 'US':
    from .models_us import Specialty as Especialidad, Doctor as Medico, Patient as Paciente
elif HMS_COUNTRY == 'BR':
    from .models_br import Especialidade as Especialidad, Medico, Paciente
else:
    from .models_ar import Especialidad, Medico, Paciente

__all__ = ['Especialidad', 'Medico', 'Paciente', 'HMS_COUNTRY']
