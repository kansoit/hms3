import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.conf import settings
from .models import Paciente, Medico, Especialidad
from .i18n import get_country_text

def dashboard(request):
    """
    Vista principal única para demostración de Delphix Continuous Compliance.
    Muestra Pacientes y Médicos con soporte de filtrado y sin almacenamiento en caché.
    """
    txt = get_country_text()
    hms_env = os.getenv('HMS_ENV', 'prod').lower()
    db_name = settings.DATABASES['default'].get('NAME', 'hms3')
    query_paciente = request.GET.get('q_paciente', '').strip()
    query_medico = request.GET.get('q_medico', '').strip()

    country = os.getenv('HMS_COUNTRY', 'AR').upper()
    if country == 'BR':
        pacientes_qs = Paciente.objects.select_related('medico_responsavel', 'medico_responsavel__especialidade').all()
        if query_paciente:
            pacientes_qs = pacientes_qs.filter(
                Q(cpf__icontains=query_paciente) |
                Q(rg__icontains=query_paciente) |
                Q(sobrenome__icontains=query_paciente) |
                Q(nome__icontains=query_paciente) |
                Q(convenio__icontains=query_paciente) |
                Q(diagnostico__icontains=query_paciente)
            )

        medicos_qs = Medico.objects.select_related('especialidade').all()
        if query_medico:
            medicos_qs = medicos_qs.filter(
                Q(crm__icontains=query_medico) |
                Q(sobrenome__icontains=query_medico) |
                Q(nome__icontains=query_medico) |
                Q(especialidade__nome__icontains=query_medico) |
                Q(cpf__icontains=query_medico)
            )
        obras_sociales_count = Paciente.objects.values('convenio').distinct().count()
        todos_medicos = Medico.objects.select_related('especialidade').all().order_by('sobrenome', 'nome')

    elif country == 'US':
        pacientes_qs = Paciente.objects.select_related('assigned_doctor', 'assigned_doctor__specialty').all()
        if query_paciente:
            pacientes_qs = pacientes_qs.filter(
                Q(ssn__icontains=query_paciente) |
                Q(state_id__icontains=query_paciente) |
                Q(last_name__icontains=query_paciente) |
                Q(first_name__icontains=query_paciente) |
                Q(insurance_provider__icontains=query_paciente) |
                Q(diagnosis__icontains=query_paciente)
            )

        medicos_qs = Medico.objects.select_related('specialty').all()
        if query_medico:
            medicos_qs = medicos_qs.filter(
                Q(npi__icontains=query_medico) |
                Q(last_name__icontains=query_medico) |
                Q(first_name__icontains=query_medico) |
                Q(specialty__name__icontains=query_medico) |
                Q(ssn__icontains=query_medico)
            )
        obras_sociales_count = Paciente.objects.values('insurance_provider').distinct().count()
        todos_medicos = Medico.objects.select_related('specialty').all().order_by('last_name', 'first_name')

    else:
        pacientes_qs = Paciente.objects.select_related('medico_asignado', 'medico_asignado__especialidad').all()
        if query_paciente:
            pacientes_qs = pacientes_qs.filter(
                Q(dni__icontains=query_paciente) |
                Q(cuil__icontains=query_paciente) |
                Q(apellido__icontains=query_paciente) |
                Q(nombre__icontains=query_paciente) |
                Q(obra_social__icontains=query_paciente) |
                Q(diagnostico_clinico__icontains=query_paciente)
            )

        medicos_qs = Medico.objects.select_related('especialidad').all()
        if query_medico:
            medicos_qs = medicos_qs.filter(
                Q(matricula_nacional__icontains=query_medico) |
                Q(apellido__icontains=query_medico) |
                Q(nombre__icontains=query_medico) |
                Q(especialidad__nombre__icontains=query_medico) |
                Q(dni__icontains=query_medico)
            )
        obras_sociales_count = Paciente.objects.values('obra_social').distinct().count()
        todos_medicos = Medico.objects.select_related('especialidad').all().order_by('apellido', 'nombre')

    total_pacientes = Paciente.objects.count()
    total_medicos = Medico.objects.count()
    total_especialidades = Especialidad.objects.count()
    tab = request.GET.get('tab', '').strip().lower()
    if not tab:
        tab = 'medicos' if query_medico else 'pacientes'

    context = {
        'txt': txt,
        'hms_env': hms_env,
        'db_name': db_name,
        'pacientes': pacientes_qs,
        'medicos': medicos_qs,
        'todos_medicos': todos_medicos,
        'total_pacientes': total_pacientes,
        'total_medicos': total_medicos,
        'total_especialidades': total_especialidades,
        'obras_sociales_count': obras_sociales_count,
        'q_paciente': query_paciente,
        'q_medico': query_medico,
        'active_tab': tab,
    }
    return render(request, 'dashboard.html', context)


import json
from django.views.decorators.csrf import csrf_exempt


def api_health(request):
    """
    Health check API endpoint returning operational status, environment and database.
    """
    hms_env = os.getenv('HMS_ENV', 'prod').lower()
    country = os.getenv('HMS_COUNTRY', 'AR').upper()
    db_name = settings.DATABASES['default'].get('NAME', 'hms3')
    is_masked = (hms_env == 'test')
    return JsonResponse({
        'status': 'UP',
        'environment': hms_env,
        'country': country,
        'database': db_name,
        'masked': is_masked,
    })


def patient_list(request):
    """
    REST API endpoint returning JSON list of all patients.
    Supports query parameter '?q=' for filtering.
    """
    q = request.GET.get('q', '').strip()
    country = os.getenv('HMS_COUNTRY', 'AR').upper()
    if country == 'BR':
        qs = Paciente.objects.select_related('medico_responsavel', 'medico_responsavel__especialidade').all()
        if q:
            qs = qs.filter(
                Q(cpf__icontains=q) | Q(rg__icontains=q) |
                Q(sobrenome__icontains=q) | Q(nome__icontains=q) |
                Q(convenio__icontains=q) | Q(diagnostico__icontains=q)
            )
    elif country == 'US':
        qs = Paciente.objects.select_related('assigned_doctor', 'assigned_doctor__specialty').all()
        if q:
            qs = qs.filter(
                Q(ssn__icontains=q) | Q(state_id__icontains=q) |
                Q(last_name__icontains=q) | Q(first_name__icontains=q) |
                Q(insurance_provider__icontains=q) | Q(diagnosis__icontains=q)
            )
    else:
        qs = Paciente.objects.select_related('medico_asignado', 'medico_asignado__especialidad').all()
        if q:
            qs = qs.filter(
                Q(dni__icontains=q) | Q(cuil__icontains=q) |
                Q(apellido__icontains=q) | Q(nombre__icontains=q) |
                Q(obra_social__icontains=q) | Q(diagnostico_clinico__icontains=q)
            )

    items = []
    for p in qs:
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
            'insurance': p.obra_social,
            'diagnosis': p.diagnostico_clinico,
            'doctor': str(p.medico_asignado) if p.medico_asignado else None,
        })
    return JsonResponse({'status': 'ok', 'count': len(items), 'patients': items})


def doctor_list(request):
    """
    REST API endpoint returning JSON list of all doctors.
    """
    country = os.getenv('HMS_COUNTRY', 'AR').upper()
    if country == 'BR':
        qs = Medico.objects.select_related('especialidade').all()
        items = [{
            'id': m.id,
            'first_name': m.nome,
            'last_name': m.sobrenome,
            'license': m.crm,
            'cpf': m.cpf,
            'specialty': m.especialidade.nome if m.especialidade else None,
            'phone': m.telefone_celular,
            'email': m.email
        } for m in qs]
    elif country == 'US':
        qs = Medico.objects.select_related('specialty').all()
        items = [{
            'id': m.id,
            'first_name': m.first_name,
            'last_name': m.last_name,
            'license': m.npi,
            'ssn': m.ssn,
            'specialty': m.specialty.name if m.specialty else None,
            'phone': m.phone_number,
            'email': m.email
        } for m in qs]
    else:
        qs = Medico.objects.select_related('especialidad').all()
        items = [{
            'id': m.id,
            'first_name': m.nombre,
            'last_name': m.apellido,
            'license': m.matricula_nacional,
            'dni': m.dni,
            'specialty': m.especialidad.nombre if m.especialidad else None,
            'phone': m.telefono_celular,
            'email': m.email
        } for m in qs]
    return JsonResponse({'status': 'ok', 'count': len(items), 'doctors': items})


def patient_detail(request, pk):
    """
    Returns sensitive PHI and clinical records for a specific patient.
    """
    country = os.getenv('HMS_COUNTRY', 'AR').upper()
    if country == 'BR':
        paciente = get_object_or_404(
            Paciente.objects.select_related('medico_responsavel', 'medico_responsavel__especialidade'), 
            pk=pk
        )
    elif country == 'US':
        paciente = get_object_or_404(
            Paciente.objects.select_related('assigned_doctor', 'assigned_doctor__specialty'), 
            pk=pk
        )
    else:
        paciente = get_object_or_404(
            Paciente.objects.select_related('medico_asignado', 'medico_asignado__especialidad'), 
            pk=pk
        )

    doctor_obj = paciente.medico_asignado
    doctor_str = str(doctor_obj) if doctor_obj else ("No physician assigned" if country == 'US' else ("Sem médico atribuído" if country == 'BR' else "Sin asignar"))

    data = {
        'id': paciente.id,
        'patient_id': paciente.id,
        'first_name': paciente.nombre,
        'last_name': paciente.apellido,
        'full_name': f"{paciente.apellido}, {paciente.nombre}",
        'doc_primary': paciente.dni,
        'doc_secondary': paciente.cuil,
        'date_of_birth': paciente.fecha_nacimiento.strftime('%d/%m/%Y') if paciente.fecha_nacimiento else '',
        'date_of_birth_iso': paciente.fecha_nacimiento.strftime('%Y-%m-%d') if paciente.fecha_nacimiento else '',
        'phone': paciente.telefono_celular,
        'email': paciente.email,
        'address': paciente.direccion,
        'city': paciente.localidad,
        'state': paciente.provincia,
        'postal_code': getattr(paciente, 'codigo_postal', getattr(paciente, 'zip_code', getattr(paciente, 'cep', ''))),
        'insurance_provider': paciente.obra_social,
        'insurance_number': paciente.numero_afiliado,
        'diagnosis': paciente.diagnostico_clinico,
        'clinical_notes': paciente.historia_clinica,
        'doctor_id': paciente.medico_asignado_id if doctor_obj else None,
        'doctor_name': doctor_str,
        'doctor': doctor_str,
    }
    return JsonResponse(data)


@csrf_exempt
@require_POST
def patient_save(request):
    """
    Creates or updates a patient record via JSON or form payload.
    """
    payload = {}
    if request.content_type == 'application/json':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            payload = {}

    def get_val(*keys, default=''):
        for k in keys:
            if k in payload and payload[k] is not None:
                return str(payload[k]).strip()
            val = request.POST.get(k)
            if val is not None:
                return str(val).strip()
        return default

    patient_id = get_val('patient_id', 'id')
    doc_primary = get_val('doc_primary', 'ssn', 'state_id')
    doc_secondary = get_val('doc_secondary')
    last_name = get_val('last_name')
    first_name = get_val('first_name')
    dob = get_val('dob', 'date_of_birth')
    phone = get_val('phone', 'phone_number')
    email = get_val('email')
    address = get_val('address')
    city = get_val('city')
    state = get_val('state')
    postal_code = get_val('postal_code', 'zip_code')
    insurance = get_val('insurance', 'insurance_provider')
    insurance_number = get_val('insurance_number', 'policy_number')
    diagnosis = get_val('diagnosis')
    notes = get_val('notes', 'clinical_notes')
    doctor_id = get_val('doctor_id')

    if not doc_primary or not last_name or not first_name:
        return JsonResponse({
            'status': 'error',
            'message': 'Primary ID, Last Name, and First Name are required fields.'
        }, status=400)

    country = os.getenv('HMS_COUNTRY', 'AR').upper()
    default_city = 'New York' if country == 'US' else ('São Paulo' if country == 'BR' else 'CABA')
    default_state = 'NY' if country == 'US' else ('SP' if country == 'BR' else 'Buenos Aires')
    default_ins = 'Blue Cross' if country == 'US' else ('Unimed' if country == 'BR' else 'OSDE')
    default_phone = '+1 (212) 555-0199' if country == 'US' else ('+55 11 98888-0000' if country == 'BR' else '+54 9 11 4000-0000')
    default_domain = 'hospital.org' if country == 'US' else ('hospital.com.br' if country == 'BR' else 'hospital.com.ar')

    if patient_id:
        paciente = get_object_or_404(Paciente, pk=patient_id)
        paciente.dni = doc_primary
        if doc_secondary:
            paciente.cuil = doc_secondary
        paciente.apellido = last_name
        paciente.nombre = first_name
        if dob:
            paciente.fecha_nacimiento = dob
        if phone:
            paciente.telefono_celular = phone
        if email:
            paciente.email = email
        if address:
            paciente.direccion = address
        if city:
            paciente.localidad = city
        if state:
            paciente.provincia = state
        if postal_code and hasattr(paciente, 'codigo_postal'):
            paciente.codigo_postal = postal_code
        if insurance:
            paciente.obra_social = insurance
        if insurance_number:
            paciente.numero_afiliado = insurance_number
        if diagnosis:
            paciente.diagnostico_clinico = diagnosis
        if notes:
            paciente.historia_clinica = notes
        if doctor_id and doctor_id.isdigit():
            paciente.medico_asignado_id = int(doctor_id)
    else:
        paciente = Paciente()
        paciente.dni = doc_primary
        paciente.cuil = doc_secondary or (f"999-{doc_primary[-4:]}" if country == 'US' else (f"999.{doc_primary[-3:]}-00" if country == 'BR' else f"20-{doc_primary}-9"))
        paciente.apellido = last_name
        paciente.nombre = first_name
        if dob:
            paciente.fecha_nacimiento = dob
        else:
            from datetime import date
            paciente.fecha_nacimiento = date(1985, 1, 1)

        paciente.telefono_celular = phone or default_phone
        paciente.email = email or f"{first_name.lower().replace(' ', '')}.{last_name.lower().replace(' ', '')}@{default_domain}"
        paciente.direccion = address or ("100 Main St" if country == 'US' else ("Av. Paulista 1000" if country == 'BR' else "Av. Corrientes 1234"))
        paciente.localidad = city or default_city
        paciente.provincia = state or default_state
        if postal_code and hasattr(paciente, 'codigo_postal'):
            paciente.codigo_postal = postal_code
        paciente.obra_social = insurance or default_ins
        paciente.numero_afiliado = insurance_number or "10002345"
        paciente.diagnostico_clinico = diagnosis or ("Clinical Checkup" if country == 'US' else ("Consulta de rotina" if country == 'BR' else "Consulta médica general"))
        paciente.historia_clinica = notes or ("Routine evaluation without acute complaints." if country == 'US' else ("Avaliação de rotina sem queixas agudas." if country == 'BR' else "Sin antecedentes relevantes reportados."))
        paciente.medico_asignado_id = int(doctor_id) if doctor_id and doctor_id.isdigit() else None

    try:
        paciente.save()
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Database error while saving patient: {str(e)}'
        }, status=400)

    action = "updated" if patient_id else "created"
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
    paciente.delete()
    return JsonResponse({
        'status': 'ok',
        'id': pk,
        'patient_id': pk,
        'message': f'Patient {full_name} deleted successfully.'
    })

