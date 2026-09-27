import random
from datetime import date, timedelta
import pyodbc
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, transaction

NOMBRES_MASCULINOS = [
    "Arthur", "Bernardo", "Davi", "Gabriel", "Heitor", "Lucas", "Matheus", "Pedro", 
    "Lorenzo", "Enzo", "Cauã", "Thales", "Felipe", "Rodrigo", "Gustavo", "Leonardo", 
    "Bruno", "Thiago", "Rafael", "Henrique", "Marcelo", "Vinicius", "Eduardo", "Caio", 
    "Alexandre", "Murilo", "Otávio", "Diego", "Samuel", "Danilo", "Guilherme", "Renato", 
    "Igor", "Leandro", "Fernando", "André", "Fábio", "Ricardo", "Vitor", "Breno", 
    "Yuri", "Luiz", "César", "Erick", "Wagner", "Renan", "Daniel", "Marcos", 
    "Paulo", "Cristiano", "Everton", "Fabrício", "Tiago", "Maurício"
]

NOMBRES_FEMENINOS = [
    "Alice", "Helena", "Laura", "Manuela", "Sophia", "Isabella", "Heloísa", "Luiza", 
    "Júlia", "Lorena", "Lívia", "Giovanna", "Beatriz", "Mariana", "Camila", "Larissa", 
    "Fernanda", "Gabriela", "Letícia", "Amanda", "Bruna", "Carolina", "Natália", "Jéssica", 
    "Aline", "Cecília", "Maitê", "Yasmin", "Bianca", "Rafaela", "Vanessa", "Tatiane", 
    "Priscila", "Renata", "Clarice", "Taís", "Débora", "Flávia", "Patrícia", "Sabrina", 
    "Clara", "Elisa", "Rebeca", "Daniela", "Milena", "Carla", "Luciana", "Monique", 
    "Adriana", "Jaqueline", "Viviane", "Alessandra", "Juliana", "Talita"
]

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Pereira", "Lima", "Carvalho", 
    "Ferreira", "Ribeiro", "Rodrigues", "Almeida", "Nascimento", "Alves", "Araújo", "Ramos",
    "Gomes", "Martins", "Rocha", "Barbosa", "Cardoso", "Melo", "Teixeira", "Monteiro",
    "da Silva", "dos Santos", "de Oliveira", "de Souza", "Ferreira Lima", "Barbosa da Costa",
    "Cardoso de Oliveira", "Alves de Souza", "Vieira", "Machado", "Moraes", "Cavalcanti",
    "Batista", "Pinto", "Correia", "Castro", "Freitas", "Dias", "Moreira", "Nunes", 
    "Marques", "Fernandes", "Barros", "Costa e Silva", "Tavares", "Mendes", 
    "Guimarães", "Borges", "Farias", "Dantas", "Assis", "Peixoto", "Siqueira"
]

ESPECIALIDADES_BRASIL = [
    ("Cardiologia", "Prevenção, diagnóstico e tratamento de doenças cardiovasculares"),
    ("Clínica Médica", "Acompanhamento médico integral do adulto em regime ambulatorial e hospitalar"),
    ("Ortopedia e Traumatologia", "Afecções do sistema locomotor, lesões articulares e traumas ósseos"),
    ("Pediatria", "Atenção integral à saúde na infância e adolescência"),
    ("Dermatologia", "Patologias da pele, mucosas, cabelos e unhas"),
    ("Neurologia", "Distúrbios do sistema nervoso central e periférico"),
    ("Gastroenterologia", "Doenças do aparelho digestivo, fígado e pâncreas"),
    ("Oftalmologia", "Saúde ocular, acuidade visual e microcirurgia refrativa"),
    ("Pneumologia", "Doenças respiratórias crônicas e da caixa torácica"),
    ("Ginecologia e Obstetrícia", "Saúde reprodutiva feminina, pré-natal e parto"),
    ("Urologia", "Afecções do trato urinário e sistema reprodutor masculino"),
    ("Diagnóstico por Imagem", "Tomografia computadorizada, ultrassonografia e ressonância magnética")
]

CONVENIOS_BRASIL = [
    "Unimed Nacional", "Bradesco Saúde Top", "Amil 400", "SulAmérica Especial", 
    "NotreDame Intermédica", "Porto Seguro Saúde", "SUS (Sistema Único de Saúde)", "Golden Cross"
]

DIAGNOSTICOS_POR_ESPECIALIDADE = {
    "Cardiologia": [
        ("Hipertensão arterial estágio 2", "Paciente com registros tensionais superiores a 150/95 mmHg. Indicado ajuste de enalapril 10mg e dieta hipossódica."),
        ("Fibrilação Atrial Paroxística", "Episódio agudo revertido. Solicitado monitoramento Holter 24h e iniciado tratamento anticoagulante oral."),
        ("Insuficiência coronariana crônica", "Angina aos esforços classe funcional II. Ecocardiograma com fração de ejeção preservada. Ajuste de betabloqueador.")
    ],
    "Clínica Médica": [
        ("Diabetes mellitus tipo 2 descompensado", "Controle glicêmico trimestral. HbA1c em 7.9%. Ajustada dose de metformina e encaminhado ao nutricionista."),
        ("Insuficiência venosa periférica crônica", "Edema vespertino em membros inferiores bilateral. Recomendadas meias de compressão elástica e caminhadas."),
        ("Síndrome metabólica e dislipidemia", "Hipertrigliceridemia acentuada e LDL elevado. Orientadas mudanças de estilo de vida e prescrita estatina.")
    ],
    "Ortopedia e Traumatologia": [
        ("Lombalgia mecânica aguda", "Dor lombar incapacitante após esforço físico. Radiografia sem evidência de fratura. Repouso de 72h e AINEs."),
        ("Entorse de joelho direito grau I", "Lesão do ligamento colateral medial sem instabilidade cirúrgica. Imobilização com órtese e fisioterapia."),
        ("Tendinopatia do manguito rotador", "Dor noturna e limitação à abdução do ombro direito. Ultrassonografia confirma espessamento. Prescrita reabilitação motora.")
    ],
    "Pediatria": [
        ("Puericultura e controle de crescimento", "Desenvolvimento neuropsicomotor adequado no percentil 50. Calendário vacinal completo. Orientações de aleitamento."),
        ("Bronquiolite viral aguda leve", "Lactente com sibilos expiratórios leves sem esforço respiratório acentuado. Conduta expectante com hidratação oral."),
        ("Gastroenterite aguda infantil", "Episódio diarreico de 24h autolimitado sem desidratação. Prescrita solução de reidratação oral e dieta constipante.")
    ],
    "Dermatologia": [
        ("Dermatite atópica moderada", "Eczema pruriginoso em dobras cubitais e poplíteas. Prescrita corticoterapia tópica e hidratantes com ceramidas."),
        ("Psoríase em placas crônica", "Placas eritemato-descamativas em cotovelos e joelhos. Iniciado tratamento tópico combinado com calcipotriol."),
        ("Mapeamento dermatoscópico de nevos", "Avaliação de lesões pigmentadas sem critérios de atipia ou assimetria (ABCD). Orientado fotoprotetor FPS 50+.")
    ],
    "Neurologia": [
        ("Cefaleia tensional episódica", "Crises cefalálgicas semanais associadas a sobrecarga laboral. RMN de crânio dentro da normalidade. Iniciada profilaxia."),
        ("Enxaqueca com aura visual típica", "Cefaleia pulsátil hemicraniana precedida de escotomas cintilantes. Prescrito triptano em SOS ao início da dor."),
        ("Polineuropatia periférica distal", "Parestesias em extremidades de membros inferiores. Solicitada eletroneuromiografia para confirmação diagnóstica.")
    ],
    "Gastroenterologia": [
        ("Gastroenterocolite aguda viral", "Quadro de 48h com náuseas, vômitos e evacuações líquidas. Hidratação oral bem tolerada."),
        ("Doença do refluxo gastroesofágico (DRGE)", "Pirose retroesternal e regurgitação ácida noturna. Iniciado teste terapêutico com pantoprazol 40mg."),
        ("Síndrome do intestino irritável", "Dor abdominal espasmódica com alívio pós-evacuação e distensão. Orientada reeducação alimentar low-FODMAP.")
    ],
    "Oftalmologia": [
        ("Astigmatismo miópico composto", "Queda progressiva da acuidade visual para longe. Fundoscopia normal. Prescrita receita de lentes corretivas."),
        ("Conjuntivite bacteriana aguda", "Hiperemia conjuntival e secreção mucopurulenta bilateral. Colírio de tobramicina a cada 6 horas por 7 dias."),
        ("Glaucoma de ângulo aberto em investigação", "Pressão intraocular limítrofe (22 mmHg). Indicada paquimetria ultrassônica e campimetria computadorizada.")
    ],
    "Pneumologia": [
        ("Asma brônquica em crise leve", "Espirometria com distúrbio obstrutivo ventilatório reversível. Indicado corticoide inalatório associado a broncodilatador."),
        ("DPOC reagudizada moderada", "Tabagista crônico com aumento de tosse produtiva e dispneia mMRC 2. Otimizada terapia inalatória dupla (LABA/LAMA)."),
        ("Pneumonia adquirida na comunidade", "Infiltrado broncoalveolar em base pulmonar direita com febre e tosse. Iniciada antibioticoterapia com amoxicilina/clavulanato.")
    ],
    "Ginecologia e Obstetrícia": [
        ("Exame ginecológico de rotina (Papanicolau)", "Exame especular e colposcopia sem alterações citológicas. Exame clínico das mamas preservado."),
        ("Pré-natal de primeiro trimestre (10 semanas)", "Gravidez confirmada por ultrassom com embrião viável e batimentos cardíacos presentes. Prescrito ácido fólico e sulfato ferroso."),
        ("Síndrome dos ovários policísticos (SOP)", "Oligomenorreia associada a manifestações clínicas de hiperandrogenismo. Indicada terapia com anticoncepcional oral.")
    ],
    "Urologia": [
        ("Hiperplasia prostática benigna (HPB)", "Jato urinário fraco, nictúria e sensação de esvaziamento incompleto. PSA em 1.8 ng/mL. Prescrita tansulosina 0.4mg."),
        ("Cólica nefrética por litíase ureteral", "Dor lombar súbita com irradiação anterior. Ultrassom confirma cálculo de 4mm em terço distal ureteral."),
        ("Infecção do trato urinário (ITU baixa)", "Disúria, polaciúria e urgência miccional de 48 horas. Urocultura coletada e iniciado ciprofloxacino empírico.")
    ],
    "Diagnóstico por Imagem": [
        ("Nódulo tireoidiano sólido (TIRADS 3)", "Ultrassonografia cervical revela nódulo isoecoico bem delimitado de 1.1cm. Recomendado seguimento em 6 meses."),
        ("Lombociatalgia - Hérnia discal L5-S1", "RMN lombar demonstra protrusão discal focal póstero-lateral com compressão da raiz emergente S1."),
        ("Esteatose hepática difusa grau II", "Ultrassonografia de abdome superior constata hiperecogenicidade do parênquima hepático sem lesões focais.")
    ]
}

LOGRADOUROS_BRASIL = [
    ("Av. Paulista", "Bela Vista", "São Paulo", "SP", "01311-200"),
    ("Av. Brigadeiro Faria Lima", "Pinheiros", "São Paulo", "SP", "01452-000"),
    ("Rua Oscar Freire", "Jardins", "São Paulo", "SP", "01426-001"),
    ("Av. Ibirapuera", "Moema", "São Paulo", "SP", "04028-000"),
    ("Rua Vergueiro", "Vila Mariana", "São Paulo", "SP", "04101-000"),
    ("Av. Morumbi", "Morumbi", "São Paulo", "SP", "05650-000"),
    ("Av. Atlântica", "Copacabana", "Rio de Janeiro", "RJ", "22070-000"),
    ("Av. Vieira Souto", "Ipanema", "Rio de Janeiro", "RJ", "22420-000"),
    ("Av. Afonso Pena", "Funcionários", "Belo Horizonte", "MG", "30130-002"),
    ("Rua das Flores", "Centro", "Curitiba", "PR", "80020-000")
]


def calcular_cpf_valido() -> str:
    """
    Gera um CPF 100% válido com os dois dígitos verificadores calculados (Módulo 11)
    conforme padrão oficial da Receita Federal do Brasil para LGPD.
    """
    nove_digitos = [random.randint(0, 9) for _ in range(9)]
    
    # 1º Dígito verificador
    soma1 = sum(d * (10 - i) for i, d in enumerate(nove_digitos))
    resto1 = soma1 % 11
    d1 = 0 if resto1 < 2 else (11 - resto1)
    
    # 2º Dígito verificador
    dez_digitos = nove_digitos + [d1]
    soma2 = sum(d * (11 - i) for i, d in enumerate(dez_digitos))
    resto2 = soma2 % 11
    d2 = 0 if resto2 < 2 else (11 - resto2)
    
    digs = "".join(str(d) for d in nove_digitos)
    return f"{digs[:3]}.{digs[3:6]}.{digs[6:9]}-{d1}{d2}"


def gerar_rg_brasileiro(estado: str) -> str:
    """Gera formato realista de RG (Registro Geral) brasileiro."""
    p1 = random.randint(10, 60)
    p2 = random.randint(100, 999)
    p3 = random.randint(100, 999)
    dv = random.choice([str(random.randint(0, 9)), "X"])
    return f"{estado}-{p1}.{p2}.{p3}-{dv}"


class Command(BaseCommand):
    help = 'Povoa a base de dados brasileira com CPFs válidos (Módulo 11), RGs, CRMs e Prontuários para LGPD.'

    def add_arguments(self, parser):
        parser.add_argument('--pacientes', type=int, default=40, help='Quantidade de pacientes')
        parser.add_argument('--medicos', type=int, default=10, help='Quantidade de médicos')
        parser.add_argument('--clean', action='store_true', help='Limpa tabelas e reseta IDs em 0')

    def asegurar_base_dados(self):
        """Cria a base de dados no SQL Server se não existir (Dia 0)."""
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
                self.stdout.write(self.style.WARNING(f"-> Base de dados '{target_db}' não encontrada. Criando no SQL Server..."))
                safe_db_name = target_db.replace("]", "]]")
                cursor.execute(f"CREATE DATABASE [{safe_db_name}];")
                self.stdout.write(self.style.SUCCESS(f"-> Base de dados '{target_db}' criada com sucesso!"))
            else:
                self.stdout.write(f"-> Base de dados '{target_db}' verificada no SQL Server.")
            conn.close()
            connection.close()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao verificar/criar a base de dados '{target_db}': {e}"))
            raise

    def asegurar_tabelas(self, drop_first=False):
        """Cria as tabelas em SQL Server se ainda não existirem, ou as recria se drop_first=True."""
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT COUNT(*) FROM sys.tables WHERE name = 'PACIENTES';
            """)
            has_pacientes = cursor.fetchone()[0] > 0
            if has_pacientes and not drop_first:
                cursor.execute("""
                SELECT COUNT(*) FROM sys.columns WHERE object_id = OBJECT_ID('PACIENTES') AND name = 'CPF';
                """)
                if cursor.fetchone()[0] == 0:
                    self.stdout.write(self.style.WARNING("-> Detectado schema anterior incompatível em PACIENTES. Recriando tabelas..."))
                    drop_first = True

            if drop_first:
                self.stdout.write(self.style.WARNING("-> Excluindo tabelas anteriores para recriação limpa..."))
                cursor.execute("""
                IF OBJECT_ID('dbo.PACIENTES', 'U') IS NOT NULL DROP TABLE dbo.PACIENTES;
                IF OBJECT_ID('dbo.MEDICOS', 'U') IS NOT NULL DROP TABLE dbo.MEDICOS;
                IF OBJECT_ID('dbo.ESPECIALIDADES', 'U') IS NOT NULL DROP TABLE dbo.ESPECIALIDADES;
                IF OBJECT_ID('dbo.PATIENTS', 'U') IS NOT NULL DROP TABLE dbo.PATIENTS;
                IF OBJECT_ID('dbo.DOCTORS', 'U') IS NOT NULL DROP TABLE dbo.DOCTORS;
                IF OBJECT_ID('dbo.SPECIALTIES', 'U') IS NOT NULL DROP TABLE dbo.SPECIALTIES;
                """)

            cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ESPECIALIDADES')
            CREATE TABLE ESPECIALIDADES (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                NOME NVARCHAR(60) NOT NULL UNIQUE,
                DESCRICAO NVARCHAR(255) NULL
            );
            
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'MEDICOS')
            CREATE TABLE MEDICOS (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                CRM NVARCHAR(20) NOT NULL UNIQUE,
                ESTADO_CRM NVARCHAR(10) NOT NULL DEFAULT 'SP',
                CPF NVARCHAR(15) NOT NULL UNIQUE,
                RG NVARCHAR(15) NOT NULL UNIQUE,
                SOBRENOME NVARCHAR(60) NOT NULL,
                NOME NVARCHAR(60) NOT NULL,
                ESPECIALIDADE_ID INT NOT NULL FOREIGN KEY REFERENCES ESPECIALIDADES(ID),
                TELEFONE_CELULAR NVARCHAR(25) NOT NULL,
                EMAIL NVARCHAR(100) NOT NULL
            );

            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PACIENTES')
            CREATE TABLE PACIENTES (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                CPF NVARCHAR(15) NOT NULL UNIQUE,
                RG NVARCHAR(15) NOT NULL UNIQUE,
                SOBRENOME NVARCHAR(60) NOT NULL,
                NOME NVARCHAR(60) NOT NULL,
                DATA_NASCIMENTO DATE NOT NULL,
                TELEFONE_CELULAR NVARCHAR(25) NOT NULL,
                EMAIL NVARCHAR(100) NOT NULL,
                ENDERECO NVARCHAR(120) NOT NULL,
                BAIRRO NVARCHAR(60) NOT NULL,
                CIDADE NVARCHAR(60) NOT NULL,
                ESTADO NVARCHAR(10) NOT NULL,
                CEP NVARCHAR(10) NOT NULL,
                CONVENIO NVARCHAR(60) NOT NULL,
                NUMERO_CARTEIRINHA NVARCHAR(30) NOT NULL,
                DIAGNOSTICO NVARCHAR(150) NOT NULL,
                PRONTUARIO NVARCHAR(MAX) NOT NULL,
                MEDICO_ID INT NULL FOREIGN KEY REFERENCES MEDICOS(ID),
                DATA_INTERNACAO DATE NOT NULL DEFAULT GETDATE()
            );

            IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('PACIENTES') AND name = 'CEP')
            BEGIN
                ALTER TABLE PACIENTES ADD CEP NVARCHAR(10) NULL;
                EXEC('UPDATE PACIENTES SET CEP = CASE ESTADO
                    WHEN ''SP'' THEN ''01310-100''
                    WHEN ''RJ'' THEN ''20040-002''
                    WHEN ''MG'' THEN ''30130-100''
                    WHEN ''PR'' THEN ''80020-010''
                    ELSE ''01000-000''
                END WHERE CEP IS NULL;');
                ALTER TABLE PACIENTES ALTER COLUMN CEP NVARCHAR(10) NOT NULL;
            END;
            """)
            if not connection.get_autocommit():
                connection.commit()

    def handle(self, *args, **options):
        self.asegurar_base_dados()

        if options['clean']:
            self.stdout.write(self.style.WARNING("Limpando e recriando tabelas brasileiras do zero (Reset IDs em 1)..."))
            self.asegurar_tabelas(drop_first=True)
        else:
            self.asegurar_tabelas(drop_first=False)

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("""
                IF (SELECT COUNT(*) FROM PACIENTES) > 0 DELETE FROM PACIENTES;
                IF (SELECT COUNT(*) FROM MEDICOS) > 0 DELETE FROM MEDICOS;
                IF (SELECT COUNT(*) FROM ESPECIALIDADES) > 0 DELETE FROM ESPECIALIDADES;

                IF (SELECT last_value FROM sys.identity_columns WHERE object_id = OBJECT_ID('PACIENTES')) IS NULL
                    DBCC CHECKIDENT ('PACIENTES', RESEED, 1);
                ELSE
                    DBCC CHECKIDENT ('PACIENTES', RESEED, 0);

                IF (SELECT last_value FROM sys.identity_columns WHERE object_id = OBJECT_ID('MEDICOS')) IS NULL
                    DBCC CHECKIDENT ('MEDICOS', RESEED, 1);
                ELSE
                    DBCC CHECKIDENT ('MEDICOS', RESEED, 0);

                IF (SELECT last_value FROM sys.identity_columns WHERE object_id = OBJECT_ID('ESPECIALIDADES')) IS NULL
                    DBCC CHECKIDENT ('ESPECIALIDADES', RESEED, 1);
                ELSE
                    DBCC CHECKIDENT ('ESPECIALIDADES', RESEED, 0);
                """)

            from core.models_br import Especialidade, Medico, Paciente

            # 1. Especialidades
            self.stdout.write("-> Criando catálogo de especialidades médicas (Brasil)...")
            especialidades_objs = []
            for esp_nome, esp_desc in ESPECIALIDADES_BRASIL:
                obj, _ = Especialidade.objects.get_or_create(
                    nome=esp_nome,
                    defaults={'descricao': esp_desc}
                )
                especialidades_objs.append(obj)

            cant_medicos = options['medicos']
            cant_pacientes = options['pacientes']

            # 2. Médicos
            self.stdout.write(f"-> Gerando {cant_medicos} médicos brasileiros com CRM e CPF...")
            medicos_creados = []
            used_med_names = set()
            for i in range(cant_medicos):
                genero = 'M' if random.random() > 0.5 else 'F'
                for _ in range(50):
                    nome = random.choice(NOMBRES_MASCULINOS if genero == 'M' else NOMBRES_FEMENINOS)
                    sobrenome = random.choice(SOBRENOMES)
                    if (nome, sobrenome) not in used_med_names:
                        used_med_names.add((nome, sobrenome))
                        break

                cpf = calcular_cpf_valido()
                estado_crm = random.choice(['SP', 'RJ', 'MG', 'PR', 'RS'])
                rg = gerar_rg_brasileiro(estado_crm)
                crm = str(random.randint(110000, 499999))
                esp = especialidades_objs[i % len(especialidades_objs)]
                telefone = f"+55 {random.choice([11, 21, 31, 41])} 9{random.randint(7000, 9999)}-{random.randint(1000, 9999)}"
                email = f"{nome.lower().replace(' ', '')}.{sobrenome.lower().replace(' ', '')}@hospitalmetropolitano.com.br"

                medico = Medico.objects.create(
                    crm=crm,
                    estado_crm=estado_crm,
                    cpf=cpf,
                    rg=rg,
                    sobrenome=sobrenome,
                    nome=nome,
                    especialidade=esp,
                    telefone_celular=telefone,
                    email=email
                )
                medicos_creados.append(medico)

            # 3. Pacientes
            self.stdout.write(f"-> Gerando {cant_pacientes} pacientes brasileiros com prontuários e LGPD...")
            hoy = date.today()
            used_pat_names = set(used_med_names)

            for j in range(cant_pacientes):
                genero = 'M' if random.random() > 0.5 else 'F'
                for _ in range(50):
                    nome = random.choice(NOMBRES_MASCULINOS if genero == 'M' else NOMBRES_FEMENINOS)
                    sobrenome = random.choice(SOBRENOMES)
                    if (nome, sobrenome) not in used_pat_names:
                        used_pat_names.add((nome, sobrenome))
                        break

                cpf = calcular_cpf_valido()
                logradouro, bairro, cidade, estado, cep = random.choice(LOGRADOUROS_BRASIL)
                rg = gerar_rg_brasileiro(estado)
                numero_casa = random.randint(10, 3500)
                comp = f", Apto {random.randint(11, 142)}" if random.random() > 0.4 else ""
                endereco = f"{logradouro}, {numero_casa}{comp}"

                dias_vida = random.randint(18 * 365, 80 * 365)
                data_nasc = hoy - timedelta(days=dias_vida)

                convenio = random.choice(CONVENIOS_BRASIL)
                carteirinha = f"{random.randint(100000000, 999999999)}-{random.randint(0, 9)}"

                # Seleção de médico e diagnóstico
                medico_asignado = None
                if medicos_creados:
                    if genero == 'M':
                        candidatos = [m for m in medicos_creados if m.especialidade.nome != 'Ginecologia e Obstetrícia']
                    else:
                        candidatos = medicos_creados
                    medico_asignado = random.choice(candidatos if candidatos else medicos_creados)

                if medico_asignado and medico_asignado.especialidade:
                    posibles_diag = DIAGNOSTICOS_POR_ESPECIALIDADE.get(
                        medico_asignado.especialidade.nome,
                        [("Consulta de rotina", "Avaliação clínica preventiva periódica.")]
                    )
                    if medico_asignado.especialidade.nome == 'Urologia' and genero == 'F':
                        posibles_diag = [d for d in posibles_diag if "prostática" not in d[0].lower()]
                    diag_titulo, diag_historia = random.choice(posibles_diag)
                else:
                    diag_titulo, diag_historia = ("Consulta de rotina", "Avaliação clínica preventiva periódica.")

                telefone = f"+55 {random.choice([11, 21, 31, 41])} 9{random.randint(7000, 9999)}-{random.randint(1000, 9999)}"
                email = f"{nome.lower().replace(' ', '')}.{sobrenome.lower().replace(' ', '')}{random.randint(10, 99)}@gmail.com"

                Paciente.objects.create(
                    cpf=cpf,
                    rg=rg,
                    sobrenome=sobrenome,
                    nome=nome,
                    data_nascimento=data_nasc,
                    telefone_celular=telefone,
                    email=email,
                    endereco=endereco,
                    bairro=bairro,
                    cidade=cidade,
                    estado=estado,
                    cep=cep,
                    convenio=convenio,
                    numero_carteirinha=carteirinha,
                    diagnostico=diag_titulo,
                    prontuario=diag_historia,
                    medico_responsavel=medico_asignado
                )

        self.stdout.write(self.style.SUCCESS(
            f"¡Sucesso! Criadas {len(especialidades_objs)} especialidades, {cant_medicos} médicos com CRM e {cant_pacientes} pacientes com CPFs válidos (Módulo 11)."
        ))
