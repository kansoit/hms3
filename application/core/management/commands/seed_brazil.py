import random
from datetime import date, timedelta

from core.management.seed_base import BaseSeedCommand, email_slug
from core.synthetic_identifiers import generate_br_cpf as calcular_cpf_valido, generate_br_rg as gerar_rg_brasileiro

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
    ("Av. Paulista", "São Paulo", "SP", "01311-200"),
    ("Av. Brigadeiro Faria Lima", "São Paulo", "SP", "01452-000"),
    ("Rua Oscar Freire", "São Paulo", "SP", "01426-001"),
    ("Av. Ibirapuera", "São Paulo", "SP", "04028-000"),
    ("Rua Vergueiro", "São Paulo", "SP", "04101-000"),
    ("Av. Morumbi", "São Paulo", "SP", "05650-000"),
    ("Av. Atlântica", "Rio de Janeiro", "RJ", "22070-000"),
    ("Av. Vieira Souto", "Rio de Janeiro", "RJ", "22420-000"),
    ("Av. Afonso Pena", "Belo Horizonte", "MG", "30130-002"),
    ("Rua das Flores", "Curitiba", "PR", "80020-000")
]


class Command(BaseSeedCommand):
    help = 'Povoa a base de dados brasileira com CPFs sintéticos (Módulo 11), RGs, CRMs e Prontuários para LGPD.'
    country = 'BR'

    # Sem FOREIGN KEY de propósito: permite o TRUNCATE do masking on-the-fly.
    ddl = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ESPECIALIDADES')
        CREATE TABLE ESPECIALIDADES (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            ESPECIALIDADE NVARCHAR(60) NOT NULL UNIQUE,
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
            ESPECIALIDADE_ID INT NOT NULL,
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
            CIDADE NVARCHAR(60) NOT NULL,
            ESTADO NVARCHAR(10) NOT NULL,
            CEP NVARCHAR(10) NOT NULL,
            CONVENIO NVARCHAR(60) NOT NULL,
            NUMERO_CARTEIRINHA NVARCHAR(30) NOT NULL,
            DIAGNOSTICO NVARCHAR(150) NOT NULL,
            PRONTUARIO NVARCHAR(MAX) NOT NULL,
            MEDICO_ID INT NULL,
            DATA_INTERNACAO DATE NOT NULL DEFAULT GETDATE()
        );
    """

    def get_models(self):
        from core.models_br import Especialidade, Medico, Paciente
        return (Especialidade, Medico, Paciente)

    def populate(self, cant_medicos, cant_pacientes):
        Especialidade, Medico, Paciente = self.get_models()

        # 1. Especialidades
        self.stdout.write("-> Criando catálogo de especialidades médicas (Brasil)...")
        especialidades_objs = [
            Especialidade.objects.create(especialidade=esp_nome, descricao=esp_desc)
            for esp_nome, esp_desc in ESPECIALIDADES_BRASIL
        ]

        # 2. Médicos
        self.stdout.write(f"-> Gerando {cant_medicos} médicos brasileiros com CRM e CPF...")
        medicos_creados = []
        used_names = set()
        used_cpfs, used_rgs, used_crms = set(), set(), set()

        for i in range(cant_medicos):
            genero, nome, sobrenome = self.pick_person(NOMBRES_MASCULINOS, NOMBRES_FEMENINOS, SOBRENOMES, used_names)

            cpf = self.unique(calcular_cpf_valido, used_cpfs)
            estado_crm = random.choice(['SP', 'RJ', 'MG', 'PR', 'RS'])
            rg = self.unique(lambda: gerar_rg_brasileiro(estado_crm), used_rgs)
            crm = self.unique(lambda: str(random.randint(110000, 499999)), used_crms)
            esp = especialidades_objs[i % len(especialidades_objs)]
            telefone = f"+55 {random.choice([11, 21, 31, 41])} 9{random.randint(7000, 9999)}-{random.randint(1000, 9999)}"
            email = f"{email_slug(nome)}.{email_slug(sobrenome)}@hospitalmetropolitano.com.br"

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
        used_cpfs, used_rgs = set(), set()

        for j in range(cant_pacientes):
            genero, nome, sobrenome = self.pick_person(NOMBRES_MASCULINOS, NOMBRES_FEMENINOS, SOBRENOMES, used_names)

            cpf = self.unique(calcular_cpf_valido, used_cpfs)
            logradouro, cidade, estado, cep = random.choice(LOGRADOUROS_BRASIL)
            rg = self.unique(lambda: gerar_rg_brasileiro(estado), used_rgs)
            numero_casa = random.randint(10, 3500)
            comp = f", Apto {random.randint(11, 142)}" if random.random() > 0.4 else ""
            endereco = f"{logradouro}, {numero_casa}{comp}"

            dias_vida = random.randint(18 * 365, 80 * 365)
            data_nasc = hoy - timedelta(days=dias_vida)

            convenio = random.choice(CONVENIOS_BRASIL)
            carteirinha = f"{random.randint(100000000, 999999999)}-{random.randint(0, 9)}"

            # Seleção de médico e diagnóstico
            if genero == 'M':
                candidatos = [m for m in medicos_creados if m.especialidade.especialidade != 'Ginecologia e Obstetrícia']
            else:
                candidatos = medicos_creados
            medico_asignado = random.choice(candidatos if candidatos else medicos_creados)

            posibles_diag = DIAGNOSTICOS_POR_ESPECIALIDADE.get(
                medico_asignado.especialidade.especialidade,
                [("Consulta de rotina", "Avaliação clínica preventiva periódica.")]
            )
            if medico_asignado.especialidade.especialidade == 'Urologia' and genero == 'F':
                posibles_diag = [d for d in posibles_diag if "prostática" not in d[0].lower()]
            diag_titulo, diag_historia = random.choice(posibles_diag)

            telefone = f"+55 {random.choice([11, 21, 31, 41])} 9{random.randint(7000, 9999)}-{random.randint(1000, 9999)}"
            email = f"{email_slug(nome)}.{email_slug(sobrenome)}{random.randint(10, 99)}@gmail.com"

            Paciente.objects.create(
                cpf=cpf,
                rg=rg,
                sobrenome=sobrenome,
                nome=nome,
                data_nascimento=data_nasc,
                telefone_celular=telefone,
                email=email,
                endereco=endereco,
                cidade=cidade,
                estado=estado,
                cep=cep,
                convenio=convenio,
                numero_carteirinha=carteirinha,
                diagnostico=diag_titulo,
                prontuario=diag_historia,
                medico_responsavel=medico_asignado
            )

        return (
            f"Sucesso! Criadas {len(especialidades_objs)} especialidades, {cant_medicos} médicos com CRM "
            f"e {cant_pacientes} pacientes com CPFs sintéticos (Módulo 11)."
        )
