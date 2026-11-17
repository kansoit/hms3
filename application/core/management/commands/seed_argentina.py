import random
from datetime import date, timedelta

from core.management.seed_base import BaseSeedCommand, email_slug
from core.synthetic_identifiers import generate_ar_cuil as calcular_cuil

NOMBRES_MASCULINOS = [
    "Mateo", "Bautista", "Juan", "Felipe", "Bruno", "Santiago", "Joaquín", "Lucas", 
    "Benjamín", "Tomás", "Nicolás", "Martín", "Ignacio", "Agustín", "Francisco", 
    "Lautaro", "Facundo", "Julián", "Emiliano", "Manuel", "Federico", "Gonzalo", 
    "Ramiro", "Maximiliano", "Esteban", "Mariano", "Diego", "Hernán", "Sebastián", 
    "Gabriel", "Alejandro", "Fernando", "Matías", "Ezequiel", "Rodrigo", "Leandro", 
    "Marcos", "Pablo", "Luciano", "Guillermo", "Damián", "Patricio", "Federico", 
    "Gastón", "Cristian", "Leonardo", "Javier", "Germán", "Gustavo", "Andrés"
]

NOMBRES_FEMENINOS = [
    "Sofía", "Emma", "Valentina", "Isabella", "Martina", "Lucía", "Camila", "María", 
    "Catalina", "Julieta", "Delfina", "Mía", "Paula", "Victoria", "Florencia", 
    "Carolina", "Agustina", "Luciana", "Milagros", "Micaela", "Rocío", "Sol", 
    "Candela", "Belén", "Mariana", "Daniela", "Valeria", "Cecilia", "Natalia", 
    "Romina", "Carla", "Constanza", "Pilar", "Guadalupe", "Macarena", "Malena", 
    "Sabrina", "Clara", "Morena", "Josefina", "Abril", "Brenda", "Flavia", 
    "Mariela", "Gisela", "Melisa", "Patricia", "Andrea", "Lorena", "Soledad"
]

APELLIDOS = [
    "González", "Rodríguez", "Gómez", "Fernández", "López", "Díaz", "Martínez", 
    "Pérez", "García", "Sánchez", "Romero", "Sosa", "Álvarez", "Torres", "Ruiz", 
    "Ramírez", "Flores", "Benítez", "Acosta", "Medina", "Herrera", "Aguirre", 
    "Giménez", "Gutiérrez", "Pereyra", "Castro", "Molina", "Ortiz", "Silva", 
    "Núñez", "Luna", "Juárez", "Cabrera", "Ríos", "Morales", "Godoy", "Moreno", 
    "Ferreyra", "Domínguez", "Carrizo", "Vega", "Castillo", "Ojeda", "Rojas", 
    "Méndez", "Peralta", "Quiroga", "Vázquez", "Rossi", "Ferrari", "Bianchi"
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


class Command(BaseSeedCommand):
    help = 'Genera pacientes, médicos y catálogo dinámico de especialidades argentinas para Delphix Continuous Compliance.'
    country = 'AR'

    # Sin FOREIGN KEY a propósito: permite el TRUNCATE del masking on-the-fly.
    ddl = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ESPECIALIDADES')
        CREATE TABLE ESPECIALIDADES (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            ESPECIALIDAD NVARCHAR(60) NOT NULL UNIQUE,
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
            ESPECIALIDAD_ID INT NOT NULL,
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
            DIAGNOSTICO_CLINICO NVARCHAR(150) NOT NULL,
            HISTORIA_CLINICA NVARCHAR(MAX) NOT NULL,
            MEDICO_ID INT NULL,
            FECHA_INGRESO DATE NOT NULL DEFAULT GETDATE()
        );
    """

    def get_models(self):
        from core.models_ar import Especialidad, Medico, Paciente
        return (Especialidad, Medico, Paciente)

    def populate(self, cant_medicos, cant_pacientes):
        Especialidad, Medico, Paciente = self.get_models()

        # 1. Crear catálogo dinámico de especialidades
        self.stdout.write("-> Creando catálogo de especialidades médicas...")
        especialidades_objs = [
            Especialidad.objects.create(especialidad=esp_nombre, descripcion=esp_desc)
            for esp_nombre, esp_desc in ESPECIALIDADES_ARGENTINA
        ]

        self.stdout.write(f"-> Generando {cant_medicos} médicos argentinos...")
        medicos_creados = []
        dni_base_medicos = random.randint(22000000, 32000000)
        used_names = set()
        used_matriculas = set()

        for i in range(cant_medicos):
            genero, nombre, apellido = self.pick_person(NOMBRES_MASCULINOS, NOMBRES_FEMENINOS, APELLIDOS, used_names)

            dni = str(dni_base_medicos + i * 137)
            cuil = calcular_cuil(dni, genero)
            mn = self.unique(lambda: str(random.randint(90000, 160000)), used_matriculas)
            mp = str(random.randint(40000, 80000))
            esp_seleccionada = especialidades_objs[i % len(especialidades_objs)]
            telefono = f"+54 9 11 {random.randint(4000, 6999)}-{random.randint(1000, 9999)}"
            email = f"{email_slug(nombre)}.{email_slug(apellido)}@sanatoriometropolitano.com.ar"

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
            genero, nombre, apellido = self.pick_person(NOMBRES_MASCULINOS, NOMBRES_FEMENINOS, APELLIDOS, used_names)

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

            if genero == 'M':
                candidatos = [m for m in medicos_creados if m.especialidad.especialidad != 'Ginecología y Obstetricia']
            else:
                candidatos = medicos_creados
            medico_asignado = random.choice(candidatos if candidatos else medicos_creados)

            posibles_diag = DIAGNOSTICOS_POR_ESPECIALIDAD.get(
                medico_asignado.especialidad.especialidad,
                [("Control clínico general", "Evaluación preventiva integral de rutina.")]
            )
            if medico_asignado.especialidad.especialidad == 'Urología' and genero == 'F':
                posibles_diag = [d for d in posibles_diag if "prostática" not in d[0].lower()]
            diag_titulo, diag_historia = random.choice(posibles_diag)

            telefono = f"+54 9 11 {random.randint(2000, 3999)}-{random.randint(1000, 9999)}"
            email = f"{email_slug(nombre)}.{email_slug(apellido)}{random.randint(10, 99)}@gmail.com"

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

        return (
            f"¡Éxito! Se crearon {len(especialidades_objs)} especialidades en catálogo, {cant_medicos} médicos "
            f"y {cant_pacientes} pacientes con DNIs y CUILs sintéticos (Módulo 11)."
        )
