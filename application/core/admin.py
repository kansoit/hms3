import os
from django.contrib import admin
from .models import Especialidad, Medico, Paciente

country = os.getenv('HMS_COUNTRY', 'AR').upper()

if country == 'BR':
    @admin.register(Especialidad)
    class EspecialidadeAdmin(admin.ModelAdmin):
        list_display = ('id', 'nome', 'descricao')
        search_fields = ('nome',)

    @admin.register(Medico)
    class MedicoBRAdmin(admin.ModelAdmin):
        list_display = ('id', 'crm', 'estado_crm', 'sobrenome', 'nome', 'especialidade', 'cpf', 'rg', 'telefone_celular')
        search_fields = ('sobrenome', 'nome', 'cpf', 'rg', 'crm')
        list_filter = ('especialidade', 'estado_crm')

    @admin.register(Paciente)
    class PacienteBRAdmin(admin.ModelAdmin):
        list_display = ('id', 'cpf', 'rg', 'sobrenome', 'nome', 'convenio', 'numero_carteirinha', 'telefone_celular')
        search_fields = ('sobrenome', 'nome', 'cpf', 'rg', 'convenio')
        list_filter = ('convenio', 'estado')

elif country == 'US':
    @admin.register(Especialidad)
    class SpecialtyAdmin(admin.ModelAdmin):
        list_display = ('id', 'name', 'description')
        search_fields = ('name',)

    @admin.register(Medico)
    class DoctorAdmin(admin.ModelAdmin):
        list_display = ('id', 'npi', 'state_license', 'last_name', 'first_name', 'specialty', 'ssn', 'state_id', 'phone_number')
        search_fields = ('last_name', 'first_name', 'ssn', 'npi')
        list_filter = ('specialty',)

    @admin.register(Paciente)
    class PatientAdmin(admin.ModelAdmin):
        list_display = ('id', 'ssn', 'state_id', 'last_name', 'first_name', 'insurance_provider', 'policy_number', 'phone_number')
        search_fields = ('last_name', 'first_name', 'ssn', 'insurance_provider')
        list_filter = ('insurance_provider', 'state')

else:
    @admin.register(Especialidad)
    class EspecialidadAdmin(admin.ModelAdmin):
        list_display = ('id', 'nombre', 'descripcion')
        search_fields = ('nombre',)

    @admin.register(Medico)
    class MedicoAdmin(admin.ModelAdmin):
        list_display = ('id', 'matricula_nacional', 'apellido', 'nombre', 'especialidad', 'dni', 'cuil', 'telefono_celular')
        search_fields = ('apellido', 'nombre', 'dni', 'cuil', 'matricula_nacional', 'especialidad__nombre')
        list_filter = ('especialidad',)

    @admin.register(Paciente)
    class PacienteAdmin(admin.ModelAdmin):
        list_display = ('id', 'dni', 'cuil', 'apellido', 'nombre', 'obra_social', 'numero_afiliado', 'telefono_celular', 'medico_asignado')
        search_fields = ('apellido', 'nombre', 'dni', 'cuil', 'obra_social', 'numero_afiliado')
        list_filter = ('obra_social', 'provincia')
