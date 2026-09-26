import os

HMS_COUNTRY = os.getenv('HMS_COUNTRY', 'AR').upper()

if HMS_COUNTRY == 'US':
    from .models_us import Specialty as Especialidad, Doctor as Medico, Patient as Paciente
elif HMS_COUNTRY == 'BR':
    from .models_br import Especialidade as Especialidad, Medico, Paciente
else:
    from .models_ar import Especialidad, Medico, Paciente

__all__ = ['Especialidad', 'Medico', 'Paciente', 'HMS_COUNTRY']
