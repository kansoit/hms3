"""
Smoke tests de HMS 3.0: recorren lo que se muestra en una demo.

Corren contra SQLite (sin SQL Server). Como el país se elige al arrancar, se
ejecutan una vez por país con ./run_smoke_tests.sh (AR, BR y US).
"""
from unittest import mock

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import OperationalError, connection
from django.test import TestCase

from core.models import Especialidad, Medico, Paciente

SEEDERS = {'AR': 'seed_argentina', 'BR': 'seed_brazil', 'US': 'seed_usa'}
SEEDER = SEEDERS[settings.HMS_COUNTRY]
OTHER_SEEDER = next(cmd for country, cmd in SEEDERS.items() if country != settings.HMS_COUNTRY)


def seed(*args):
    call_command(SEEDER, *args, verbosity=0, stdout=mock.MagicMock())


class SmokeTests(TestCase):
    @classmethod
    def setUpClass(cls):
        # Los modelos son managed = False: en SQL Server las tablas las crean los
        # seeders. Para el test se crean acá, antes de abrir la transacción.
        with connection.schema_editor() as editor:
            for model in (Especialidad, Medico, Paciente):
                editor.create_model(model)
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        seed('--seed', '7')

    # ------------------------------------------------------------- seeders
    def test_seed_crea_los_datos(self):
        self.assertEqual(Paciente.objects.count(), 40)
        self.assertEqual(Medico.objects.count(), 10)
        self.assertGreater(Especialidad.objects.count(), 0)

    def test_seed_sin_clean_no_borra(self):
        antes = list(Paciente.objects.values_list('pk', flat=True))
        with self.assertRaises(CommandError):
            seed()
        self.assertEqual(list(Paciente.objects.values_list('pk', flat=True)), antes)

    def test_seeder_de_otro_pais_no_corre(self):
        with self.assertRaises(CommandError):
            call_command(OTHER_SEEDER, '--clean', verbosity=0, stdout=mock.MagicMock())
        self.assertEqual(Paciente.objects.count(), 40)

    def test_seed_reproducible(self):
        def nombres():
            return sorted((p.apellido, p.nombre, p.dni) for p in Paciente.objects.all())
        seed('--clean', '--seed', '123')
        primera = nombres()
        seed('--clean', '--seed', '123')
        self.assertEqual(nombres(), primera)

    def test_emails_sin_acentos(self):
        for email in list(Paciente.objects.values_list('email', flat=True)) + \
                list(Medico.objects.values_list('email', flat=True)):
            self.assertTrue(email.isascii(), email)

    # -------------------------------------------------------------- vistas
    def test_dashboard(self):
        paciente = Paciente.objects.first()
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, paciente.dni)
        html = res.content.decode()
        self.assertNotIn('cdn.jsdelivr.net', html)
        self.assertNotIn('cdnjs.cloudflare.com', html)
        self.assertEqual(len(res.context['medicos']), 10)

    def test_dashboard_busquedas(self):
        paciente = Paciente.objects.first()
        res = self.client.get('/', {'q_paciente': paciente.dni})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['pacientes']), 1)
        medico = Medico.objects.first()
        res = self.client.get('/', {'q_medico': medico.apellido, 'tab': 'medicos'})
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.context['medicos']), 1)

    def test_assets_locales(self):
        for path in ('vendor/bootstrap/bootstrap.min.css',
                     'vendor/bootstrap/bootstrap.bundle.min.js',
                     'vendor/fontawesome/css/all.min.css',
                     'vendor/fontawesome/webfonts/fa-solid-900.woff2'):
            self.assertIsNotNone(finders.find(path), path)

    def test_health(self):
        res = self.client.get('/api/health/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'UP')
        self.assertEqual(data['patients'], 40)
        self.assertEqual(data['country'], settings.HMS_COUNTRY)

    def test_referencias_rotas(self):
        data = self.client.get('/api/health/').json()
        self.assertEqual(data['integrity'], 'OK')
        self.assertEqual(data['doctors_without_specialty'], 0)
        self.assertEqual(data['patients_with_missing_doctor'], 0)

        # Simula un job de masking que dejó ESPECIALIDADES vacía y un paciente
        # apuntando a un médico que no existe.
        # (borrado directo en la tabla, como lo haría un proceso externo: el ORM lo impediría)
        Especialidad.objects.all()._raw_delete(Especialidad.objects.db)
        paciente = Paciente.objects.first()
        paciente.medico_asignado_id = 999999
        paciente.save()

        data = self.client.get('/api/health/').json()
        self.assertEqual(data['status'], 'UP')
        self.assertEqual(data['integrity'], 'BROKEN')
        self.assertEqual(data['doctors_without_specialty'], 10)
        self.assertEqual(data['patients_with_missing_doctor'], 1)

        # Los médicos siguen apareciendo, marcados sin especialidad.
        res = self.client.get('/', {'tab': 'medicos'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['medicos']), 10)
        self.assertContains(res, res.context['txt']['no_specialty'])
        self.assertEqual(self.client.get('/api/doctors/').json()['count'], 10)
        self.assertEqual(self.client.get('/api/patients/').json()['count'], 40)
        self.assertEqual(self.client.get(f'/api/patient/{paciente.pk}/').status_code, 200)

    def test_api_listados(self):
        data = self.client.get('/api/patients/').json()
        self.assertEqual(data['count'], 40)
        data = self.client.get('/api/doctors/').json()
        self.assertEqual(data['count'], 10)
        self.assertTrue(data['doctors'][0]['license'])
        self.assertTrue(data['doctors'][0]['specialty'])

    def test_detalle_paciente(self):
        paciente = Paciente.objects.first()
        data = self.client.get(f'/api/patient/{paciente.pk}/').json()
        self.assertEqual(data['doc_primary'], paciente.dni)
        self.assertTrue(data['date_of_birth_iso'])
        self.assertTrue(data['doctor_id'])
        self.assertEqual(self.client.get('/api/patient/999999/').status_code, 404)

    def test_alta_edicion_y_baja(self):
        medico = Medico.objects.first()
        res = self.client.post('/api/patient/save/', {'first_name': 'Demo', 'last_name': 'Paciente'})
        self.assertEqual(res.status_code, 200, res.content)
        pk = res.json()['id']
        nuevo = Paciente.objects.get(pk=pk)
        self.assertTrue(nuevo.dni and nuevo.cuil)

        res = self.client.post('/api/patient/save/', {
            'patient_id': pk, 'first_name': 'Demo', 'last_name': 'Editado',
            'dob': '1985-03-02', 'doctor_id': medico.pk, 'postal_code': '1234',
            'diagnosis': 'Control', 'notes': 'Nota',
        })
        self.assertEqual(res.status_code, 200, res.content)
        data = self.client.get(f'/api/patient/{pk}/').json()
        self.assertEqual(data['last_name'], 'Editado')
        self.assertEqual(data['date_of_birth_iso'], '1985-03-02')
        self.assertEqual(data['doctor_id'], medico.pk)
        self.assertEqual(data['postal_code'], '1234')

        res = self.client.post(f'/api/patient/{pk}/delete/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.client.get(f'/api/patient/{pk}/').status_code, 404)

    def test_alta_por_json(self):
        res = self.client.post('/api/patient/save/', data='{"first_name": "Json", "last_name": "Demo"}',
                               content_type='application/json')
        self.assertEqual(res.status_code, 200, res.content)

    def test_validaciones_de_guardado(self):
        casos = [
            {'first_name': 'SoloNombre'},
            {'first_name': 'A', 'last_name': 'B', 'doctor_id': '999999'},
            {'first_name': 'A', 'last_name': 'B', 'doctor_id': 'abc'},
            {'first_name': 'A', 'last_name': 'B', 'patient_id': 'abc'},
            {'first_name': 'A', 'last_name': 'B', 'dob': '31/12/1990'},
        ]
        total = Paciente.objects.count()
        for payload in casos:
            res = self.client.post('/api/patient/save/', payload)
            self.assertEqual(res.status_code, 400, payload)
            self.assertEqual(res.json()['status'], 'error')
        self.assertEqual(Paciente.objects.count(), total)

    # ------------------------------------------------ base de datos caída
    def test_base_caida_muestra_pagina_amable(self):
        with mock.patch('core.views._pacientes_qs', side_effect=OperationalError('db down')):
            res = self.client.get('/')
            self.assertEqual(res.status_code, 503)
            self.assertTemplateUsed(res, 'db_unavailable.html')
            res = self.client.get('/api/patients/')
            self.assertEqual(res.status_code, 503)
            self.assertEqual(res.json()['status'], 'error')

    def test_health_informa_base_caida(self):
        with mock.patch.object(Paciente.objects, 'count', side_effect=OperationalError('db down')):
            res = self.client.get('/api/health/')
        self.assertEqual(res.status_code, 503)
        self.assertEqual(res.json()['status'], 'DOWN')
