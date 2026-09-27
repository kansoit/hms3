import random
from datetime import date, timedelta
import pyodbc
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from core.models import Especialidad, Medico, Paciente

NOMBRES_MASCULINOS = [
    "Juan Carlos", "Santiago", "Mateo", "Lucas", "Joaquin", "Agustin", "Facundo", 
    "Nicolas", "Martin", "Tomas", "Gonzalo", "Ignacio", "Matias", "Diego", "Esteban"
]

NOMBRES_FEMENINOS = [
    "Maria Elena", "Lucia", "Valentina", "Martina", "Sofia", "Camila", "Julieta", 
    "Florencia", "Mariana", "Victoria", "Paula", "Carla", "Daniela", "Milagros", "Carolina"
]

APELLIDOS = [
    "Gonzalez", "Rodriguez", "Gomez", "Fernandez", "Lopez", "Diaz", "Martinez", 
    "Perez", "Garcia", "Sanchez", "Romero", "Sosa", "Alvarez", "Torres", "Ruiz", 
    "Ramirez", "Flores", "Benitez", "Acosta", "Medina", "Herrera", "Aguirre", "Gimenez"
]

ESPECIALIDADES_ARGENTINA = [
    ("Cardiología", "Prevención, diagnóstico y tratamiento de enfermedades cardiovasculares"),
    ("Clínica Médica", "Atención médica integral del adulto en internación y ambulatorio"),
    ("Traumatología y Ortopedia", "Afecciones del sistema musculoesquelético y lesiones articulares"),
    ("Pediatría", "Atención integral de la salud en la infancia y adolescencia"),
    ("Dermatología", "Patologías de la piel, mucosas y anexos cutáneos"),
    ("Neurología", "Trastornos del sistema nervioso central y periférico"),
    ("Gastroenterología", "Enfermedades del tracto digestivo, hígado y páncreas"),
    ("Oftalmología", "Salud ocular, agudeza visual y cirugía refractiva"),
    ("Neumonología", "Enfermedades respiratorias y de la caja torácica"),
    ("Ginecología y Obstetricia", "Salud reproductiva femenina, embarazo y parto"),
    ("Urología", "Afecciones del sistema urinario y aparato reproductor masculino"),
    ("Diagnóstico por Imágenes", "Tomografía computada, ecografía y resonancia magnética")
]

OBRAS_SOCIALES = [
    "OSDE 310", "OSDE 210", "Swiss Medical", "Galeno Oro", "Medifé", 
    "PAMI", "IOMA", "OMINT", "Sancor Salud", "Hospital Italiano"
]

DIAGNOSTICOS_POR_ESPECIALIDAD = {
    "Cardiología": [
        ("Hipertensión arterial estadio 2", "Paciente con registros superiores a 150/95 mmHg. Se indica ajuste de medicación con enalapril 10mg y dieta hiposódica."),
        ("Arritmia cardíaca - Fibrilación Auricular", "Episodio paroxístico. Monitoreo Holter 24hs solicitado. Tratamiento anticoagulante iniciado."),
        ("Insuficiencia coronaria crónica", "Angina de esfuerzo clase funcional II. Ecocardiograma muestra fracción de eyección conservada. Optimización de betabloqueantes.")
    ],
    "Clínica Médica": [
        ("Diabetes mellitus tipo 2", "Control metabólico trimestral. HbA1c en 7.8%. Se ajusta dosis de metformina y se solicita interconsulta con nutrición."),
        ("Insuficiencia venosa periférica", "Edemas vespertinos en miembros inferiores. Se sugieren medias de compresión elástica y caminatas regulares."),
        ("Síndrome metabólico y dislipidemia", "Perfil lipídico alterado con hipertrigliceridemia y LDL elevado. Plan de actividad física y estatinas.")
    ],
    "Traumatología y Ortopedia": [
        ("Lumbalgia mecánica aguda", "Dolor lumbar invalidante tras esfuerzo físico. Radiografía descarta fractura. Reposo 72hs y AINEs."),
        ("Traumatismo de rodilla derecha", "Esguince de ligamento colateral medial grado I. Inmovilización con férula y kinesioterapia."),
        ("Tendinopatía de hombro (Manguito rotador)", "Dolor nocturno y limitación a la abducción en hombro derecho. Se indica fisioterapia y antiinflamatorios.")
    ],
    "Pediatría": [
        ("Control pediátrico de rutina y percentiles", "Crecimiento pondoestatural adecuado en percentil 50. Vacunación de calendario al día. Pautas de puericultura."),
        ("Bronquiolitis aguda leve", "Lactante con sibilancias espiratorias leves y buena mecánica ventilatoria. Tratamiento sintomático ambulatorio."),
        ("Gastroenteritis aguda infantil", "Cuadro diarreico viral de 24hs sin signos de deshidratación. Sales de rehidratación oral y dieta astringente.")
    ],
    "Dermatología": [
        ("Dermatitis atópica severa", "Lesiones eccematosas pruriginosas generalizadas en pliegues. Tratamiento con emolientes y corticoterapia tópica."),
        ("Psoriasis en placas moderada", "Placas eritematosas con escamas plateadas en codos y rodillas. Se indica terapia tópica combinada."),
        ("Control dermatoscópico de nevos", "Revisión de lesiones pigmentadas corporales sin signos de atipia ni asimetría. Se recomienda fotoprotección FPS 50+.")
    ],
    "Neurología": [
        ("Cefalea tensional recurrente", "Episodios bi-semanales relacionados con estrés laboral. RMN de encéfalo normal. Terapia profiláctica pautada."),
        ("Migraña con aura visual", "Cefalea pulsátil hemicraneana precedida de escotomas centellantes y fotofobia. Se indican triptanes al rescate."),
        ("Neuropatía periférica leve", "Parestesias en ambos pies con hipoestesia distal. Electromiograma solicitado para evaluar velocidad de conducción.")
    ],
    "Gastroenterología": [
        ("Gastroenteritis aguda", "Cuadro de 48 horas de evolución con vómitos y deposiciones líquidas. Hidratación oral tolerada."),
        ("Enfermedad por reflujo gastroesofágico (ERGE)", "Pirosis retroesternal nocturna y regurgitación. Se prescribe inhibidor de bomba de protones (pantoprazol 40mg)."),
        ("Síndrome de intestino irritable", "Dolor cólico recurrente que alivia con la defecación y distensión abdominal. Plan alimentario bajo en FODMAPs.")
    ],
    "Oftalmología": [
        ("Astigmatismo miópico bilateral", "Disminución progresiva de la agudeza visual de lejos. Fondo de ojo normal. Se prescribe receta de cristales correctores."),
        ("Conjuntivitis bacteriana aguda", "Hiperemia conjuntival con secreción mucopurulenta bilateral. Colirio antibiótico tópico con tobramicina cada 6hs."),
        ("Control de presión ocular / Sospecha Glaucoma", "PIO en límite superior (21 mmHg). Gonioscopía y campo visual computarizado programados.")
    ],
    "Neumonología": [
        ("Asma bronquial en crisis moderada", "Espirometría con patrón obstructivo reversible. Se indican broncodilatadores y corticoides inhalados."),
        ("EPOC reagudizada leve", "Paciente tabaquista con aumento de tos y disnea habitual. Se intensifica tratamiento con broncodilatadores duales (LABA/LAMA)."),
        ("Neumonía aguda de la comunidad", "Infiltrado en lóbulo inferior derecho en radiografía con tos y fiebre. Se inicia antibioticoterapia ambulatoria.")
    ],
    "Ginecología y Obstetricia": [
        ("Control ginecológico preventivo anual", "Examen mamario y pélvico sin alteraciones. Papanicolaou y colposcopía realizados satisfactoriamente."),
        ("Embarazo de primer trimestre - Control", "Gestación única de 10 semanas con vitalidad embrionaria positiva por ecografía. Se indica ácido fólico y hierro."),
        ("Síndrome de ovario poliquístico", "Trastornos del ciclo menstrual con ciclos anovulatorios y leve acné. Se pauta anticoncepción hormonal oral.")
    ],
    "Urología": [
        ("Hiperplasia prostática benigna (HPB)", "Sintomatología obstructiva urinaria baja con chorro débil y nicturia. Se prescribe tamsulosina 0.4mg diaria."),
        ("Litiasis renal cólica", "Dolor lumbar agudo unilateral irradiado a fosa ilíaca. Ecografía confirma lito de 3.5mm en uréter distal."),
        ("Infección urinaria no complicada", "Disuria y polaquiuria de 48hs de evolución. Urocultivo en curso y tratamiento antibiótico empírico iniciado.")
    ],
    "Diagnóstico por Imágenes": [
        ("Evaluación ecográfica de nódulo tiroideo", "Ecografía cervical evidencia nódulo sólido isoecoico TIRADS 3. Se sugiere control evolutivo en 6 meses."),
        ("Lumbociatalgia - Hernia discal L5-S1", "Resonancia magnética de columna lumbosacra constata hernia discal posterolateral con contacto radicular."),
        ("Ecografía hepatobiliopancreática", "Esteatosis hepática difusa leve a moderada grado I sin dilatación de vía biliar ni litiasis vesicular.")
    ]
}

CALLES = [
    "Av. Corrientes", "Av. Santa Fe", "Av. Rivadavia", "Av. Cabildo", "Av. Belgrano",
    "Callao", "Pueyrredón", "San Martín", "Mitre", "Sarmiento", "Alberdi", "Las Heras"
]

LOCALIDADES = [
    ("CABA", "CABA", "C1002"),
    ("Vicente López", "Buenos Aires", "B1638"),
    ("San Isidro", "Buenos Aires", "B1642"),
    ("Quilmes", "Buenos Aires", "B1878"),
    ("Ramos Mejía", "Buenos Aires", "B1704"),
    ("Morón", "Buenos Aires", "B1708"),
    ("La Plata", "Buenos Aires", "B1900"),
    ("Córdoba Capital", "Córdoba", "X5000"),
    ("Rosario", "Santa Fe", "S2000")
]


def calcular_cuil(dni_str: str, genero: str) -> str:
    """
    Calcula el CUIL matemáticamente válido (Módulo 11) compatible con Delphix ar-mask.
    """
    prefix = 27 if genero == 'F' else 20
    dni_int = int(dni_str)
    weights = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

    def _eval(p, d):
        digits = [int(x) for x in f"{p:02d}{d:08d}"]
        s = sum(w * d for w, d in zip(weights, digits))
        return s % 11

    residue = _eval(prefix, dni_int)
    if residue == 0:
        dv = 0
    elif residue == 1:
        # Fallback a prefijo 23
        prefix = 23
        residue2 = _eval(prefix, dni_int)
        dv = 0 if residue2 == 0 else (11 - residue2)
    else:
        dv = 11 - residue

    return f"{prefix}-{dni_str}-{dv}"


class Command(BaseCommand):
    help = 'Genera pacientes, médicos y catálogo dinámico de especialidades argentinas para Delphix Continuous Compliance.'

    def add_arguments(self, parser):
        parser.add_argument('--pacientes', type=int, default=40, help='Cantidad de pacientes a generar')
        parser.add_argument('--medicos', type=int, default=10, help='Cantidad de médicos a generar')
        parser.add_argument('--clean', action='store_true', help='Elimina los registros existentes antes de poblar')

    def asegurar_base_datos(self):
        """Crea la base de datos en SQL Server si aún no existe (Día 0)."""
        db_conf = settings.DATABASES.get('default', {})
        engine = db_conf.get('ENGINE', '')
        if 'mssql' not in engine:
            return

        target_db = db_conf.get('NAME')
        if not target_db:
            return

        host = db_conf.get('HOST')
        port = db_conf.get('PORT', '1433')
        user = db_conf.get('USER', 'sa')
        password = db_conf.get('PASSWORD', '')
        driver = db_conf.get('OPTIONS', {}).get('driver', 'ODBC Driver 18 for SQL Server')
        extra = db_conf.get('OPTIONS', {}).get('extra_params', 'TrustServerCertificate=yes;')

        conn_str = f"DRIVER={{{driver}}};SERVER={host},{port};DATABASE=master;UID={user};PWD={password};{extra}"
        try:
            conn = pyodbc.connect(conn_str, autocommit=True, timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT database_id FROM sys.databases WHERE name = ?", (target_db,))
            row = cursor.fetchone()
            if not row:
                self.stdout.write(self.style.WARNING(f"-> Base de datos '{target_db}' no existe. Creándola en SQL Server..."))
                safe_db_name = target_db.replace("]", "]]")
                cursor.execute(f"CREATE DATABASE [{safe_db_name}];")
                self.stdout.write(self.style.SUCCESS(f"-> ¡Base de datos '{target_db}' creada exitosamente!"))
            else:
                self.stdout.write(f"-> Base de datos '{target_db}' verificada en SQL Server.")
            conn.close()
            connection.close()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al verificar/crear la base de datos '{target_db}': {e}"))
            raise

    def asegurar_tablas(self):
        """Crea las tablas argentinas en SQL Server si aún no existen."""
        with connection.cursor() as cursor:
            cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ESPECIALIDADES')
            CREATE TABLE ESPECIALIDADES (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                NOMBRE NVARCHAR(60) NOT NULL UNIQUE,
                DESCRIPCION NVARCHAR(255) NULL
            );
            
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'MEDICOS')
            CREATE TABLE MEDICOS (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                MATRICULA_NACIONAL NVARCHAR(20) NOT NULL UNIQUE,
                MATRICULA_PROVINCIAL NVARCHAR(20) NULL,
                DNI NVARCHAR(12) NOT NULL UNIQUE,
                CUIL NVARCHAR(15) NOT NULL UNIQUE,
                APELLIDO NVARCHAR(60) NOT NULL,
                NOMBRE NVARCHAR(60) NOT NULL,
                ESPECIALIDAD_ID INT NOT NULL FOREIGN KEY REFERENCES ESPECIALIDADES(ID),
                TELEFONO_CELULAR NVARCHAR(25) NOT NULL,
                EMAIL NVARCHAR(100) NOT NULL
            );

            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PACIENTES')
            CREATE TABLE PACIENTES (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                DNI NVARCHAR(12) NOT NULL UNIQUE,
                CUIL NVARCHAR(15) NOT NULL UNIQUE,
                APELLIDO NVARCHAR(60) NOT NULL,
                NOMBRE NVARCHAR(60) NOT NULL,
                FECHA_NACIMIENTO DATE NOT NULL,
                TELEFONO_CELULAR NVARCHAR(25) NOT NULL,
                EMAIL NVARCHAR(100) NOT NULL,
                DIRECCION NVARCHAR(120) NOT NULL,
                LOCALIDAD NVARCHAR(60) NOT NULL,
                PROVINCIA NVARCHAR(60) NOT NULL,
                CODIGO_POSTAL NVARCHAR(10) NOT NULL,
                OBRA_SOCIAL NVARCHAR(60) NOT NULL,
                NUMERO_AFILIADO NVARCHAR(30) NOT NULL,
                DIAGNOSTICO_CLINICO NVARCHAR(255) NOT NULL,
                HISTORIA_CLINICA NVARCHAR(MAX) NOT NULL,
                MEDICO_ID INT NULL FOREIGN KEY REFERENCES MEDICOS(ID),
                FECHA_INGRESO DATE NOT NULL DEFAULT GETDATE()
            );

            IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('PACIENTES') AND name = 'CODIGO_POSTAL')
            BEGIN
                ALTER TABLE PACIENTES ADD CODIGO_POSTAL NVARCHAR(10) NULL;
                EXEC('UPDATE PACIENTES SET CODIGO_POSTAL = CASE LOCALIDAD
                    WHEN ''CABA'' THEN ''C1002''
                    WHEN ''Vicente López'' THEN ''B1638''
                    WHEN ''San Isidro'' THEN ''B1642''
                    WHEN ''Quilmes'' THEN ''B1878''
                    WHEN ''Ramos Mejía'' THEN ''B1704''
                    WHEN ''Morón'' THEN ''B1708''
                    WHEN ''La Plata'' THEN ''B1900''
                    WHEN ''Córdoba Capital'' THEN ''X5000''
                    WHEN ''Rosario'' THEN ''S2000''
                    ELSE ''C1000''
                END WHERE CODIGO_POSTAL IS NULL;');
                ALTER TABLE PACIENTES ALTER COLUMN CODIGO_POSTAL NVARCHAR(10) NOT NULL;
            END;
            """)
            if not connection.get_autocommit():
                connection.commit()

    def handle(self, *args, **options):
        self.asegurar_base_datos()
        self.asegurar_tablas()

        with transaction.atomic():
            if options['clean']:
                self.stdout.write(self.style.WARNING("Eliminando registros previos y reseteando IDs a 0..."))
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM PACIENTES;")
                    cursor.execute("DELETE FROM MEDICOS;")
                    cursor.execute("DELETE FROM ESPECIALIDADES;")
                    cursor.execute("DBCC CHECKIDENT ('PACIENTES', RESEED, 0);")
                    cursor.execute("DBCC CHECKIDENT ('MEDICOS', RESEED, 0);")
                    cursor.execute("DBCC CHECKIDENT ('ESPECIALIDADES', RESEED, 0);")

            from core.models_ar import Especialidad, Medico, Paciente

            # 1. Crear catálogo dinámico de especialidades
            self.stdout.write("-> Creando catálogo de especialidades médicas...")
            especialidades_objs = []
            for esp_nombre, esp_desc in ESPECIALIDADES_ARGENTINA:
                obj, _ = Especialidad.objects.get_or_create(
                    nombre=esp_nombre,
                    defaults={'descripcion': esp_desc}
                )
                especialidades_objs.append(obj)

            cant_medicos = options['medicos']
            cant_pacientes = options['pacientes']

            self.stdout.write(f"-> Generando {cant_medicos} médicos argentinos...")
            medicos_creados = []
            dni_base_medicos = random.randint(22000000, 32000000)

            for i in range(cant_medicos):
                genero = 'M' if random.random() > 0.5 else 'F'
                nombre = random.choice(NOMBRES_MASCULINOS if genero == 'M' else NOMBRES_FEMENINOS)
                apellido = random.choice(APELLIDOS)
                dni = str(dni_base_medicos + i * 137)
                cuil = calcular_cuil(dni, genero)
                mn = str(random.randint(90000, 160000))
                mp = str(random.randint(40000, 80000))
                esp_seleccionada = especialidades_objs[i % len(especialidades_objs)]
                telefono = f"+54 9 11 {random.randint(4000, 6999)}-{random.randint(1000, 9999)}"
                email = f"{nombre.lower().replace(' ', '')}.{apellido.lower()}@sanatoriometropolitano.com.ar"

                medico = Medico.objects.create(
                    matricula_nacional=mn,
                    matricula_provincial=mp,
                    dni=dni,
                    cuil=cuil,
                    apellido=apellido,
                    nombre=nombre,
                    especialidad=esp_seleccionada,
                    telefono_celular=telefono,
                    email=email
                )
                medicos_creados.append(medico)

            self.stdout.write(f"-> Generando {cant_pacientes} pacientes argentinos...")
            dni_base_pacientes = random.randint(33000000, 44000000)
            hoy = date.today()

            for j in range(cant_pacientes):
                genero = 'M' if random.random() > 0.5 else 'F'
                nombre = random.choice(NOMBRES_MASCULINOS if genero == 'M' else NOMBRES_FEMENINOS)
                apellido = random.choice(APELLIDOS)
                dni = str(dni_base_pacientes + j * 97)
                cuil = calcular_cuil(dni, genero)

                edad_dias = random.randint(18 * 365, 80 * 365)
                fecha_nac = hoy - timedelta(days=edad_dias)

                calle = random.choice(CALLES)
                altura = random.randint(100, 7500)
                piso = f", {random.randint(1, 14)}° {random.choice(['A', 'B', 'C', 'D'])}" if random.random() > 0.4 else ""
                direccion = f"{calle} {altura}{piso}"
                localidad, provincia, cp = random.choice(LOCALIDADES)

                obra = random.choice(OBRAS_SOCIALES)
                afiliado = f"{random.randint(10000000, 99999999)}/{random.randint(1, 4)}"
                
                medico_asignado = None
                if medicos_creados:
                    if genero == 'M':
                        candidatos = [m for m in medicos_creados if m.especialidad.nombre != 'Ginecología y Obstetricia']
                    else:
                        candidatos = medicos_creados
                    medico_asignado = random.choice(candidatos if candidatos else medicos_creados)

                if medico_asignado and medico_asignado.especialidad:
                    posibles_diag = DIAGNOSTICOS_POR_ESPECIALIDAD.get(
                        medico_asignado.especialidad.nombre,
                        [("Control clínico general", "Evaluación preventiva integral de rutina.")]
                    )
                    if medico_asignado.especialidad.nombre == 'Urología' and genero == 'F':
                        posibles_diag = [d for d in posibles_diag if "prostática" not in d[0].lower()]
                    diag_titulo, diag_historia = random.choice(posibles_diag)
                else:
                    diag_titulo, diag_historia = ("Control clínico general", "Evaluación preventiva integral de rutina.")

                telefono = f"+54 9 11 {random.randint(2000, 3999)}-{random.randint(1000, 9999)}"
                email = f"{nombre.lower().replace(' ', '')}.{apellido.lower()}{random.randint(10, 99)}@gmail.com"

                Paciente.objects.create(
                    dni=dni,
                    cuil=cuil,
                    apellido=apellido,
                    nombre=nombre,
                    fecha_nacimiento=fecha_nac,
                    telefono_celular=telefono,
                    email=email,
                    direccion=direccion,
                    localidad=localidad,
                    provincia=provincia,
                    codigo_postal=cp,
                    obra_social=obra,
                    numero_afiliado=afiliado,
                    diagnostico_clinico=diag_titulo,
                    historia_clinica=diag_historia,
                    medico_asignado=medico_asignado
                )

            self.stdout.write(self.style.SUCCESS(
                f"¡Éxito! Se crearon {len(especialidades_objs)} especialidades en catálogo, {cant_medicos} médicos y {cant_pacientes} pacientes con DNIs y CUILs válidos."
            ))
