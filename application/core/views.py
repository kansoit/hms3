import json
import logging
from datetime import date

from django.conf import settings
from django.db import connection
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .country import PROFILE
from .i18n import get_country_text
from .models import Especialidad, Medico, Paciente
from .synthetic_identifiers import generate_unique_patient_identifiers

logger = logging.getLogger(__name__)


# --- Consultas base (una sola rama para los tres países, ver core/country.py) ---

def _pacientes_qs(q=''):
    doctor = PROFILE['patient_doctor']
    qs = Paciente.objects.select_related(doctor, f"{doctor}__{PROFILE['doctor_specialty']}")
    if q:
        cond = Q()
        for campo in PROFILE['patient_search']:
            cond |= Q(**{f'{campo}__icontains': q})
        qs = qs.filter(cond)
    return qs.order_by(*PROFILE['patient_order'])


def _medicos_qs(q=''):
    especialidad = PROFILE['doctor_specialty']
    qs = Medico.objects.select_related(especialidad)
    if q:
        cond = Q(**{f"{especialidad}__{PROFILE['specialty_name']}__icontains": q})
        for campo in PROFILE['doctor_search']:
            cond |= Q(**{f'{campo}__icontains': q})
        qs = qs.filter(cond)
    return qs.order_by(*PROFILE['doctor_order'])


def referencias_rotas():
    """
    Cuenta relaciones que apuntan a filas inexistentes. Las tablas no tienen
    FOREIGN KEY (para permitir el TRUNCATE del masking on-the-fly), así que la
    base no lo impide: puede pasar si un job de masking deja fuera una tabla o
    modifica una columna de relación.
    """
    doctor = PROFILE['patient_doctor']
    especialidad = PROFILE['doctor_specialty']
    medicos = Medico.objects.exclude(
        **{f'{especialidad}_id__in': Especialidad.objects.values('pk')}
    ).count()
    pacientes = Paciente.objects.filter(
        **{f'{doctor}_id__isnull': False}
    ).exclude(
        **{f'{doctor}_id__in': Medico.objects.values('pk')}
    ).count()
    return {'doctors_without_specialty': medicos, 'patients_with_missing_doctor': pacientes}


def _parse_id(valor):
    """Devuelve el entero de un ID recibido como texto, o None si no es válido."""
    valor = str(valor or '').strip()
    return int(valor) if valor.isdigit() else None


def dashboard(request):
    """
    Vista principal única para demostración de Delphix Continuous Compliance.
    Muestra Pacientes y Médicos con soporte de filtrado y sin almacenamiento en caché.
    """
    query_paciente = request.GET.get('q_paciente', '').strip()
    query_medico = request.GET.get('q_medico', '').strip()

    tab = request.GET.get('tab', '').strip().lower()
    if not tab:
        tab = 'medicos' if query_medico else 'pacientes'

    context = {
        'txt': get_country_text(),
        'hms_env': settings.HMS_ENV,
        'db_name': settings.DB_NAME,
        'pacientes': _pacientes_qs(query_paciente),
        'medicos': _medicos_qs(query_medico),
        'todos_medicos': _medicos_qs(),
        'total_pacientes': Paciente.objects.count(),
        'total_medicos': Medico.objects.count(),
        'total_especialidades': Especialidad.objects.count(),
        'obras_sociales_count': Paciente.objects.values(PROFILE['patient_insurance']).distinct().count(),
        'q_paciente': query_paciente,
        'q_medico': query_medico,
        'active_tab': tab,
    }
    return render(request, 'dashboard.html', context)


def api_health(request):
    """
    Health check real: consulta la base de datos. Responde 200 con status UP si
    la base contesta y tiene las tablas, o 503 con status DOWN si no.
    Informa además las referencias rotas entre tablas (integrity OK / BROKEN).
    Lo usa hms-ctl.py para confirmar que el entorno quedó operativo.
    """
    data = {
        'status': 'UP',
        'environment': settings.HMS_ENV,
        'country': settings.HMS_COUNTRY,
        'database': settings.DB_NAME,
        'masked': settings.HMS_ENV == 'test',
        'build': settings.HMS_BUILD,
    }
    try:
        data['patients'] = Paciente.objects.count()
        data['doctors'] = Medico.objects.count()
        data['specialties'] = Especialidad.objects.count()
        rotas = referencias_rotas()
        data['integrity'] = 'BROKEN' if any(rotas.values()) else 'OK'
        data.update(rotas)
    except Exception as exc:
        logger.error("Health check: base de datos no disponible: %s", exc)
        connection.close()
        data['status'] = 'DOWN'
        data['error'] = 'Database not available or not seeded.'
        return JsonResponse(data, status=503)
    return JsonResponse(data)


def patient_list(request):
    """
    REST API endpoint returning JSON list of all patients.
    Supports query parameter '?q=' for filtering.
    """
    items = []
    for p in _pacientes_qs(request.GET.get('q', '').strip()):
        items.append({
            'id': p.id,
            'patient_id': p.id,
            'doc_primary': p.dni,
            'doc_secondary': p.cuil,
            'first_name': p.nombre,
            'last_name': p.apellido,
            'phone': p.telefono_celular,
            'email': p.email,
            'address': p.direccion,
            'city': p.localidad,
            'state': p.provincia,
            'postal_code': p.codigo_postal,
            'insurance': p.obra_social,
            'diagnosis': p.diagnostico_clinico,
            'doctor': str(p.medico_asignado) if p.medico_asignado else None,
        })
    return JsonResponse({'status': 'ok', 'count': len(items), 'patients': items})


def doctor_list(request):
    """
    REST API endpoint returning JSON list of all doctors.
    """
    doc_key, doc_field = PROFILE['doctor_doc']
    items = []
    for m in _medicos_qs():
        items.append({
            'id': m.id,
            'first_name': m.nombre,
            'last_name': m.apellido,
            'license': getattr(m, PROFILE['doctor_license']),
            doc_key: getattr(m, doc_field),
            'specialty': getattr(m.especialidad, PROFILE['specialty_name']) if m.especialidad else None,
            'phone': m.telefono_celular,
            'email': m.email,
        })
    return JsonResponse({'status': 'ok', 'count': len(items), 'doctors': items})


def patient_detail(request, pk):
    """
    Returns sensitive PHI and clinical records for a specific patient.
    """
    paciente = get_object_or_404(_pacientes_qs(), pk=pk)

    doctor_obj = paciente.medico_asignado
    doctor_str = str(doctor_obj) if doctor_obj else get_country_text()['no_doctor']

    dob = paciente.fecha_nacimiento
    if dob and hasattr(dob, 'strftime'):
        dob_str = dob.strftime('%d/%m/%Y')
        dob_iso = dob.strftime('%Y-%m-%d')
    else:
        dob_str = dob_iso = str(dob or '')

    last_name = paciente.apellido or ''
    first_name = paciente.nombre or ''
    full_name = f"{last_name}, {first_name}" if last_name and first_name else (last_name or first_name)

    return JsonResponse({
        'id': paciente.id,
        'patient_id': paciente.id,
        'first_name': first_name,
        'last_name': last_name,
        'full_name': full_name,
        'doc_primary': paciente.dni or '',
        'doc_secondary': paciente.cuil or '',
        'date_of_birth': dob_str,
        'date_of_birth_iso': dob_iso,
        'phone': paciente.telefono_celular or '',
        'email': paciente.email or '',
        'address': paciente.direccion or '',
        'city': paciente.localidad or '',
        'state': paciente.provincia or '',
        'postal_code': paciente.codigo_postal or '',
        'insurance_provider': paciente.obra_social or '',
        'insurance_number': paciente.numero_afiliado or '',
        'diagnosis': paciente.diagnostico_clinico or '',
        'clinical_notes': paciente.historia_clinica or '',
        'doctor_id': paciente.medico_asignado_id if doctor_obj else None,
        'doctor_name': doctor_str,
        'doctor': doctor_str,
    })


def _error(message, status=400):
    return JsonResponse({'status': 'error', 'message': message}, status=status)


@csrf_exempt
@require_POST
def patient_save(request):
    """
    Creates or updates a patient record via JSON or form payload.
    """
    txt = get_country_text()

    payload = {}
    if request.content_type == 'application/json':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            payload = {}
        if not isinstance(payload, dict):
            payload = {}

    def get_val(*keys, default=''):
        for k in keys:
            if payload.get(k) is not None:
                return str(payload[k]).strip()
            val = request.POST.get(k)
            if val is not None:
                return str(val).strip()
        return default

    patient_id_raw = get_val('patient_id', 'id')
    doc_primary = get_val('doc_primary', 'ssn', 'state_id')
    doc_secondary = get_val('doc_secondary')
    last_name = get_val('last_name')
    first_name = get_val('first_name')
    dob_raw = get_val('dob', 'date_of_birth')
    doctor_id_raw = get_val('doctor_id')

    if not last_name or not first_name:
        return _error(txt['error_name_required'])

    # ID de paciente: vacío = alta; si viene, tiene que ser numérico.
    patient_id = None
    if patient_id_raw:
        patient_id = _parse_id(patient_id_raw)
        if patient_id is None:
            return _error('Invalid patient id.')

    # Fecha de nacimiento: se valida acá para no depender del error de la base.
    dob = None
    if dob_raw:
        try:
            dob = date.fromisoformat(dob_raw)
        except ValueError:
            return _error('Invalid date of birth (expected YYYY-MM-DD).')

    # Médico: las tablas no tienen FOREIGN KEY (para permitir el TRUNCATE del
    # masking on-the-fly), así que la existencia se valida en la aplicación.
    doctor_id = None
    if doctor_id_raw:
        doctor_id = _parse_id(doctor_id_raw)
        if doctor_id is None or not Medico.objects.filter(pk=doctor_id).exists():
            return _error(txt['error_doctor_not_found'])

    if patient_id is not None:
        paciente = get_object_or_404(Paciente, pk=patient_id)
        if doc_primary:
            paciente.dni = doc_primary
        if doc_secondary:
            paciente.cuil = doc_secondary
        if dob:
            paciente.fecha_nacimiento = dob
        if doctor_id is not None:
            paciente.medico_asignado_id = doctor_id
    else:
        try:
            doc_primary, doc_secondary = generate_unique_patient_identifiers(
                country=settings.HMS_COUNTRY,
                paciente_model=Paciente,
                doc_primary=doc_primary or None,
                doc_secondary=doc_secondary or None,
                exclude_id=None
            )
        except Exception:
            logger.exception("Error generating synthetic identifiers for patient")
            return _error('Database error while generating synthetic identifiers.')

        paciente = Paciente()
        paciente.dni = doc_primary
        paciente.cuil = doc_secondary
        paciente.fecha_nacimiento = dob or date(1990, 1, 1)
        paciente.medico_asignado_id = doctor_id

    paciente.apellido = last_name
    paciente.nombre = first_name
    paciente.telefono_celular = get_val('phone', 'phone_number')
    paciente.email = get_val('email')
    paciente.direccion = get_val('address')
    paciente.localidad = get_val('city')
    paciente.provincia = get_val('state')
    paciente.codigo_postal = get_val('postal_code', 'zip_code')
    paciente.obra_social = get_val('insurance', 'insurance_provider')
    paciente.numero_afiliado = get_val('insurance_number', 'policy_number')
    paciente.diagnostico_clinico = get_val('diagnosis')
    paciente.historia_clinica = get_val('notes', 'clinical_notes')

    try:
        paciente.save()
    except Exception:
        logger.exception("Error saving patient")
        return _error('Database error while saving patient.')

    action = "updated" if patient_id is not None else "created"
    return JsonResponse({
        'status': 'ok',
        'id': paciente.id,
        'patient_id': paciente.id,
        'message': f'Patient {paciente.apellido}, {paciente.nombre} {action} successfully.'
    })


@csrf_exempt
@require_POST
def patient_delete(request, pk):
    """
    Deletes a patient record (simulating data loss/corruption for Delphix rewind demo).
    """
    paciente = get_object_or_404(Paciente, pk=pk)
    full_name = f"{paciente.apellido}, {paciente.nombre}"
    try:
        paciente.delete()
    except Exception:
        logger.exception("Error deleting patient")
        return _error('Database error while deleting patient.')
    return JsonResponse({
        'status': 'ok',
        'id': pk,
        'patient_id': pk,
        'message': f'Patient {full_name} deleted successfully.'
    })
