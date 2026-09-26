from django.db import models


class Especialidade(models.Model):
    """
    Catálogo de especialidades médicas (Brasil).
    Tabela: ESPECIALIDADES
    """
    nome = models.CharField(
        max_length=60,
        unique=True,
        db_column='NOME',
        verbose_name="Nome da Especialidade"
    )
    descricao = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='DESCRICAO',
        verbose_name="Descrição"
    )

    class Meta:
        db_table = 'ESPECIALIDADES'
        verbose_name = 'Especialidade Médica'
        verbose_name_plural = 'Especialidades Médicas'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def nombre(self):
        return self.nome

    @nombre.setter
    def nombre(self, val):
        self.nome = val


class Medico(models.Model):
    """
    Entidade Médica (Brasil) com CRM e CPF para Delphix Profiler (LGPD).
    Tabela: MEDICOS
    """
    crm = models.CharField(
        max_length=20,
        unique=True,
        db_column='CRM',
        verbose_name="CRM"
    )
    estado_crm = models.CharField(
        max_length=10,
        default='SP',
        db_column='ESTADO_CRM',
        verbose_name="Estado do CRM"
    )
    cpf = models.CharField(
        max_length=15,
        unique=True,
        db_column='CPF',
        verbose_name="CPF"
    )
    rg = models.CharField(
        max_length=15,
        unique=True,
        db_column='RG',
        verbose_name="RG"
    )
    sobrenome = models.CharField(
        max_length=60,
        db_column='SOBRENOME',
        verbose_name="Sobrenome"
    )
    nome = models.CharField(
        max_length=60,
        db_column='NOME',
        verbose_name="Nome"
    )
    especialidade = models.ForeignKey(
        Especialidade,
        on_delete=models.PROTECT,
        db_column='ESPECIALIDADE_ID',
        related_name='medicos',
        verbose_name="Especialidade"
    )
    telefone_celular = models.CharField(
        max_length=25,
        db_column='TELEFONE_CELULAR',
        verbose_name="Telefone Celular"
    )
    email = models.EmailField(
        max_length=100,
        db_column='EMAIL',
        verbose_name="E-mail Profissional"
    )

    class Meta:
        db_table = 'MEDICOS'
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'
        ordering = ['sobrenome', 'nome']

    def __str__(self):
        esp_nome = self.especialidade.nome if self.especialidade else "Sem especialidade"
        return f"Dr(a). {self.nome} {self.sobrenome} ({esp_nome}) - CRM: {self.crm}/{self.estado_crm}"

    @property
    def matricula_nacional(self):
        return f"{self.crm}/{self.estado_crm}"

    @property
    def matricula_provincial(self):
        return self.crm

    @property
    def apellido(self):
        return self.sobrenome

    @apellido.setter
    def apellido(self, val):
        self.sobrenome = val

    @property
    def cuil(self):
        return self.cpf

    @cuil.setter
    def cuil(self, val):
        self.cpf = val

    @property
    def dni(self):
        return self.rg

    @dni.setter
    def dni(self, val):
        self.rg = val

    @property
    def especialidad(self):
        return self.especialidade

    @property
    def nombre_completo(self):
        return f"{self.sobrenome}, {self.nome}"


class Paciente(models.Model):
    """
    Entidade Paciente (Brasil) com CPF, RG, CEP e Prontuário para LGPD.
    Tabela: PACIENTES
    """
    cpf = models.CharField(
        max_length=15,
        unique=True,
        db_column='CPF',
        verbose_name="CPF"
    )
    rg = models.CharField(
        max_length=15,
        unique=True,
        db_column='RG',
        verbose_name="RG"
    )
    sobrenome = models.CharField(
        max_length=60,
        db_column='SOBRENOME',
        verbose_name="Sobrenome"
    )
    nome = models.CharField(
        max_length=60,
        db_column='NOME',
        verbose_name="Nome"
    )
    data_nascimento = models.DateField(
        db_column='DATA_NASCIMENTO',
        verbose_name="Data de Nascimento"
    )
    telefone_celular = models.CharField(
        max_length=25,
        db_column='TELEFONE_CELULAR',
        verbose_name="Telefone Celular"
    )
    email = models.EmailField(
        max_length=100,
        db_column='EMAIL',
        verbose_name="E-mail"
    )
    endereco = models.CharField(
        max_length=120,
        db_column='ENDERECO',
        verbose_name="Endereço"
    )
    bairro = models.CharField(
        max_length=60,
        default='Centro',
        db_column='BAIRRO',
        verbose_name="Bairro"
    )
    cidade = models.CharField(
        max_length=60,
        default='São Paulo',
        db_column='CIDADE',
        verbose_name="Cidade"
    )
    estado = models.CharField(
        max_length=10,
        default='SP',
        db_column='ESTADO',
        verbose_name="Estado (UF)"
    )
    cep = models.CharField(
        max_length=10,
        default='01310-100',
        db_column='CEP',
        verbose_name="CEP"
    )
    convenio = models.CharField(
        max_length=60,
        db_column='CONVENIO',
        verbose_name="Convênio Médico"
    )
    numero_carteirinha = models.CharField(
        max_length=30,
        db_column='NUMERO_CARTEIRINHA',
        verbose_name="Número da Carteirinha"
    )
    diagnostico = models.CharField(
        max_length=150,
        db_column='DIAGNOSTICO',
        verbose_name="Diagnóstico Principal"
    )
    prontuario = models.TextField(
        db_column='PRONTUARIO',
        verbose_name="Prontuário Médico / Evolução Clínica"
    )
    medico_responsavel = models.ForeignKey(
        Medico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='MEDICO_ID',
        related_name='pacientes',
        verbose_name="Médico Responsável"
    )
    data_internacao = models.DateField(
        auto_now_add=True,
        db_column='DATA_INTERNACAO',
        verbose_name="Data de Internação"
    )

    class Meta:
        db_table = 'PACIENTES'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['sobrenome', 'nome']

    def __str__(self):
        return f"{self.sobrenome}, {self.nome} (CPF: {self.cpf})"

    # Aliases de interface para compatibilidade universal
    @property
    def cuil(self):
        return self.cpf

    @cuil.setter
    def cuil(self, val):
        self.cpf = val

    @property
    def dni(self):
        return self.rg

    @dni.setter
    def dni(self, val):
        self.rg = val

    @property
    def apellido(self):
        return self.sobrenome

    @apellido.setter
    def apellido(self, val):
        self.sobrenome = val

    @property
    def fecha_nacimiento(self):
        return self.data_nascimento

    @fecha_nacimiento.setter
    def fecha_nacimiento(self, val):
        self.data_nascimento = val

    @property
    def direccion(self):
        return self.endereco

    @direccion.setter
    def direccion(self, val):
        self.endereco = val

    @property
    def localidad(self):
        return self.cidade

    @localidad.setter
    def localidad(self, val):
        self.cidade = val

    @property
    def provincia(self):
        return self.estado

    @provincia.setter
    def provincia(self, val):
        self.estado = val

    @property
    def obra_social(self):
        return self.convenio

    @obra_social.setter
    def obra_social(self, val):
        self.convenio = val

    @property
    def numero_afiliado(self):
        return self.numero_carteirinha

    @numero_afiliado.setter
    def numero_afiliado(self, val):
        self.numero_carteirinha = val

    @property
    def diagnostico_clinico(self):
        return self.diagnostico

    @diagnostico_clinico.setter
    def diagnostico_clinico(self, val):
        self.diagnostico = val

    @property
    def historia_clinica(self):
        return self.prontuario

    @historia_clinica.setter
    def historia_clinica(self, val):
        self.prontuario = val

    @property
    def medico_asignado(self):
        return self.medico_responsavel

    @medico_asignado.setter
    def medico_asignado(self, val):
        self.medico_responsavel = val

    @property
    def medico_asignado_id(self):
        return self.medico_responsavel_id

    @medico_asignado_id.setter
    def medico_asignado_id(self, val):
        self.medico_responsavel_id = val

    @property
    def nombre_completo(self):
        return f"{self.sobrenome}, {self.nome}"
