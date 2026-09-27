from django.db import models


class Especialidad(models.Model):
    """
    Catálogo dinámico de especialidades médicas (evita valores hardcodeados).
    Tabla: ESPECIALIDADES
    """
    nombre = models.CharField(
        max_length=60,
        unique=True,
        db_column='NOMBRE',
        verbose_name="Nombre de la Especialidad"
    )
    descripcion = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='DESCRIPCION',
        verbose_name="Descripción"
    )

    class Meta:
        db_table = 'ESPECIALIDADES'
        verbose_name = 'Especialidad Médica'
        verbose_name_plural = 'Especialidades Médicas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Medico(models.Model):
    """
    Entidad Médica con metadata argentina estandarizada para Delphix Profiler.
    Tabla: MEDICOS
    """
    matricula_nacional = models.CharField(
        max_length=20,
        unique=True,
        db_column='MATRICULA_NACIONAL',
        verbose_name="Matrícula Nacional"
    )
    matricula_provincial = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        db_column='MATRICULA_PROVINCIAL',
        verbose_name="Matrícula Provincial"
    )
    dni = models.CharField(
        max_length=12,
        unique=True,
        db_column='DNI',
        verbose_name="DNI"
    )
    cuil = models.CharField(
        max_length=15,
        unique=True,
        db_column='CUIL',
        verbose_name="CUIL"
    )
    apellido = models.CharField(
        max_length=60,
        db_column='APELLIDO',
        verbose_name="Apellido"
    )
    nombre = models.CharField(
        max_length=60,
        db_column='NOMBRE',
        verbose_name="Nombre"
    )
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        db_column='ESPECIALIDAD_ID',
        related_name='medicos',
        verbose_name="Especialidad"
    )
    telefono_celular = models.CharField(
        max_length=25,
        db_column='TELEFONO_CELULAR',
        verbose_name="Teléfono Celular"
    )
    email = models.EmailField(
        max_length=100,
        db_column='EMAIL',
        verbose_name="Correo Electrónico"
    )

    class Meta:
        db_table = 'MEDICOS'
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        esp_nombre = self.especialidad.nombre if self.especialidad else "Sin especialidad"
        return f"Dr/a. {self.nombre} {self.apellido} ({esp_nombre}) - MN: {self.matricula_nacional}"

    @property
    def nombre_completo(self):
        return f"{self.apellido}, {self.nombre}"

    @property
    def first_name(self):
        return self.nombre

    @first_name.setter
    def first_name(self, val):
        self.nombre = val

    @property
    def last_name(self):
        return self.apellido

    @last_name.setter
    def last_name(self, val):
        self.apellido = val

    @property
    def nome(self):
        return self.nombre

    @nome.setter
    def nome(self, val):
        self.nombre = val

    @property
    def sobrenome(self):
        return self.apellido

    @sobrenome.setter
    def sobrenome(self, val):
        self.apellido = val

    @property
    def telefone_celular(self):
        return self.telefono_celular

    @telefone_celular.setter
    def telefone_celular(self, val):
        self.telefono_celular = val

    @property
    def phone_number(self):
        return self.telefono_celular

    @phone_number.setter
    def phone_number(self, val):
        self.telefono_celular = val

    @property
    def phone(self):
        return self.telefono_celular

    @phone.setter
    def phone(self, val):
        self.telefono_celular = val


class Paciente(models.Model):
    """
    Entidad Paciente con datos sensibles para demostración de Delphix Continuous Compliance.
    Tabla: PACIENTES
    """
    dni = models.CharField(
        max_length=12,
        unique=True,
        db_column='DNI',
        verbose_name="DNI"
    )
    cuil = models.CharField(
        max_length=15,
        unique=True,
        db_column='CUIL',
        verbose_name="CUIL"
    )
    apellido = models.CharField(
        max_length=60,
        db_column='APELLIDO',
        verbose_name="Apellido"
    )
    nombre = models.CharField(
        max_length=60,
        db_column='NOMBRE',
        verbose_name="Nombre"
    )
    fecha_nacimiento = models.DateField(
        db_column='FECHA_NACIMIENTO',
        verbose_name="Fecha de Nacimiento"
    )
    telefono_celular = models.CharField(
        max_length=25,
        db_column='TELEFONO_CELULAR',
        verbose_name="Teléfono Celular"
    )
    email = models.EmailField(
        max_length=100,
        db_column='EMAIL',
        verbose_name="Correo Electrónico"
    )
    direccion = models.CharField(
        max_length=120,
        db_column='DIRECCION',
        verbose_name="Dirección"
    )
    localidad = models.CharField(
        max_length=60,
        blank=True,
        default='',
        db_column='LOCALIDAD',
        verbose_name="Localidad"
    )
    provincia = models.CharField(
        max_length=60,
        blank=True,
        default='',
        db_column='PROVINCIA',
        verbose_name="Provincia"
    )
    codigo_postal = models.CharField(
        max_length=10,
        blank=True,
        default='',
        db_column='CODIGO_POSTAL',
        verbose_name="Código Postal"
    )
    obra_social = models.CharField(
        max_length=60,
        db_column='OBRA_SOCIAL',
        verbose_name="Obra Social / Cobertura"
    )
    numero_afiliado = models.CharField(
        max_length=30,
        db_column='NUMERO_AFILIADO',
        verbose_name="N° de Afiliado"
    )
    diagnostico_clinico = models.CharField(
        max_length=255,
        db_column='DIAGNOSTICO_CLINICO',
        verbose_name="Diagnóstico Principal"
    )
    historia_clinica = models.TextField(
        db_column='HISTORIA_CLINICA',
        verbose_name="Historia Clínica / Evolución"
    )
    medico_asignado = models.ForeignKey(
        Medico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='MEDICO_ID',
        related_name='pacientes',
        verbose_name="Médico de Cabecera"
    )
    fecha_ingreso = models.DateField(
        auto_now_add=True,
        db_column='FECHA_INGRESO',
        verbose_name="Fecha de Ingreso"
    )

    class Meta:
        db_table = 'PACIENTES'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.apellido}, {self.nombre} (DNI: {self.dni})"

    @property
    def nombre_completo(self):
        return f"{self.apellido}, {self.nombre}"

    @property
    def cep(self):
        return self.codigo_postal

    @property
    def zip_code(self):
        return self.codigo_postal

    @property
    def postal_code(self):
        return self.codigo_postal

    @postal_code.setter
    def postal_code(self, val):
        self.codigo_postal = val

    @property
    def first_name(self):
        return self.nombre

    @first_name.setter
    def first_name(self, val):
        self.nombre = val

    @property
    def last_name(self):
        return self.apellido

    @last_name.setter
    def last_name(self, val):
        self.apellido = val

    @property
    def nome(self):
        return self.nombre

    @nome.setter
    def nome(self, val):
        self.nombre = val

    @property
    def sobrenome(self):
        return self.apellido

    @sobrenome.setter
    def sobrenome(self, val):
        self.apellido = val

    @property
    def telefone_celular(self):
        return self.telefono_celular

    @telefone_celular.setter
    def telefone_celular(self, val):
        self.telefono_celular = val

    @property
    def phone_number(self):
        return self.telefono_celular

    @phone_number.setter
    def phone_number(self, val):
        self.telefono_celular = val

    @property
    def phone(self):
        return self.telefono_celular

    @phone.setter
    def phone(self, val):
        self.telefono_celular = val
