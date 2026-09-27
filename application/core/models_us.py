from django.db import models


class Specialty(models.Model):
    """
    Medical Specialty Catalog (USA).
    Table: SPECIALTIES
    """
    name = models.CharField(
        max_length=60,
        unique=True,
        db_column='NAME',
        verbose_name="Specialty Name"
    )
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_column='DESCRIPTION',
        verbose_name="Description"
    )

    class Meta:
        db_table = 'SPECIALTIES'
        verbose_name = 'Medical Specialty'
        verbose_name_plural = 'Medical Specialties'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def nombre(self):
        return self.name

    @nombre.setter
    def nombre(self, val):
        self.name = val


class Doctor(models.Model):
    """
    Medical Doctor entity (USA) with NPI and State License for HIPAA compliance.
    Table: DOCTORS
    """
    npi = models.CharField(
        max_length=20,
        unique=True,
        db_column='NPI',
        verbose_name="National Provider Identifier (NPI)"
    )
    state_license = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        db_column='STATE_LICENSE',
        verbose_name="State Medical License"
    )
    ssn = models.CharField(
        max_length=15,
        unique=True,
        db_column='SSN',
        verbose_name="Social Security Number (SSN)"
    )
    state_id = models.CharField(
        max_length=15,
        unique=True,
        db_column='STATE_ID',
        verbose_name="State ID / Driver License"
    )
    last_name = models.CharField(
        max_length=60,
        db_column='LAST_NAME',
        verbose_name="Last Name"
    )
    first_name = models.CharField(
        max_length=60,
        db_column='FIRST_NAME',
        verbose_name="First Name"
    )
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.PROTECT,
        db_column='SPECIALTY_ID',
        related_name='doctors',
        verbose_name="Specialty"
    )
    phone_number = models.CharField(
        max_length=25,
        db_column='PHONE_NUMBER',
        verbose_name="Phone Number"
    )
    email = models.EmailField(
        max_length=100,
        db_column='EMAIL',
        verbose_name="Professional Email"
    )

    class Meta:
        db_table = 'DOCTORS'
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        spec_name = self.specialty.name if self.specialty else "General Practice"
        return f"Dr. {self.first_name} {self.last_name}, MD ({spec_name}) - NPI: {self.npi}"

    @property
    def matricula_nacional(self):
        return self.npi

    @property
    def matricula_provincial(self):
        return self.state_license or self.npi

    @property
    def apellido(self):
        return self.last_name

    @apellido.setter
    def apellido(self, val):
        self.last_name = val

    @property
    def nombre(self):
        return self.first_name

    @nombre.setter
    def nombre(self, val):
        self.first_name = val

    @property
    def cuil(self):
        return self.ssn

    @cuil.setter
    def cuil(self, val):
        self.ssn = val

    @property
    def dni(self):
        return self.state_id

    @dni.setter
    def dni(self, val):
        self.state_id = val

    @property
    def telefono_celular(self):
        return self.phone_number

    @telefono_celular.setter
    def telefono_celular(self, val):
        self.phone_number = val

    @property
    def telefone_celular(self):
        return self.phone_number

    @telefone_celular.setter
    def telefone_celular(self, val):
        self.phone_number = val

    @property
    def phone(self):
        return self.phone_number

    @phone.setter
    def phone(self, val):
        self.phone_number = val

    @property
    def nome(self):
        return self.first_name

    @nome.setter
    def nome(self, val):
        self.first_name = val

    @property
    def sobrenome(self):
        return self.last_name

    @sobrenome.setter
    def sobrenome(self, val):
        self.last_name = val

    @property
    def especialidad(self):
        return self.specialty

    @property
    def nombre_completo(self):
        return f"{self.last_name}, {self.first_name}"


class Patient(models.Model):
    """
    Patient entity (USA) with SSN, State ID, Insurance and HIPAA Protected Health Information (PHI).
    Table: PATIENTS
    """
    ssn = models.CharField(
        max_length=15,
        unique=True,
        db_column='SSN',
        verbose_name="Social Security Number (SSN)"
    )
    state_id = models.CharField(
        max_length=15,
        unique=True,
        db_column='STATE_ID',
        verbose_name="State ID / Driver License"
    )
    last_name = models.CharField(
        max_length=60,
        db_column='LAST_NAME',
        verbose_name="Last Name"
    )
    first_name = models.CharField(
        max_length=60,
        db_column='FIRST_NAME',
        verbose_name="First Name"
    )
    date_of_birth = models.DateField(
        db_column='DATE_OF_BIRTH',
        verbose_name="Date of Birth (DOB)"
    )
    phone_number = models.CharField(
        max_length=25,
        db_column='PHONE_NUMBER',
        verbose_name="Phone Number"
    )
    email = models.EmailField(
        max_length=100,
        db_column='EMAIL',
        verbose_name="Email Address"
    )
    address = models.CharField(
        max_length=120,
        db_column='ADDRESS',
        verbose_name="Street Address"
    )
    city = models.CharField(
        max_length=60,
        default='New York',
        db_column='CITY',
        verbose_name="City"
    )
    state = models.CharField(
        max_length=10,
        default='NY',
        db_column='STATE',
        verbose_name="State Code"
    )
    zip_code = models.CharField(
        max_length=10,
        default='10001',
        db_column='ZIP_CODE',
        verbose_name="ZIP Code"
    )
    insurance_provider = models.CharField(
        max_length=60,
        db_column='INSURANCE_PROVIDER',
        verbose_name="Health Insurance Provider"
    )
    policy_number = models.CharField(
        max_length=30,
        db_column='POLICY_NUMBER',
        verbose_name="Policy / Member ID"
    )
    diagnosis = models.CharField(
        max_length=150,
        db_column='DIAGNOSIS',
        verbose_name="Primary Clinical Diagnosis"
    )
    clinical_notes = models.TextField(
        db_column='CLINICAL_NOTES',
        verbose_name="Confidential Clinical Notes & Medical History (PHI)"
    )
    assigned_doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='DOCTOR_ID',
        related_name='patients',
        verbose_name="Attending Physician"
    )
    admission_date = models.DateField(
        auto_now_add=True,
        db_column='ADMISSION_DATE',
        verbose_name="Admission Date"
    )

    class Meta:
        db_table = 'PATIENTS'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name}, {self.first_name} (SSN: {self.ssn})"

    # Aliases de interface para compatibilidad universal
    @property
    def cuil(self):
        return self.ssn

    @cuil.setter
    def cuil(self, val):
        self.ssn = val

    @property
    def dni(self):
        return self.state_id

    @dni.setter
    def dni(self, val):
        self.state_id = val

    @property
    def apellido(self):
        return self.last_name

    @apellido.setter
    def apellido(self, val):
        self.last_name = val

    @property
    def nombre(self):
        return self.first_name

    @nombre.setter
    def nombre(self, val):
        self.first_name = val

    @property
    def fecha_nacimiento(self):
        return self.date_of_birth

    @fecha_nacimiento.setter
    def fecha_nacimiento(self, val):
        self.date_of_birth = val

    @property
    def telefono_celular(self):
        return self.phone_number

    @telefono_celular.setter
    def telefono_celular(self, val):
        self.phone_number = val

    @property
    def telefone_celular(self):
        return self.phone_number

    @telefone_celular.setter
    def telefone_celular(self, val):
        self.phone_number = val

    @property
    def phone(self):
        return self.phone_number

    @phone.setter
    def phone(self, val):
        self.phone_number = val

    @property
    def nome(self):
        return self.first_name

    @nome.setter
    def nome(self, val):
        self.first_name = val

    @property
    def sobrenome(self):
        return self.last_name

    @sobrenome.setter
    def sobrenome(self, val):
        self.last_name = val

    @property
    def direccion(self):
        return self.address

    @direccion.setter
    def direccion(self, val):
        self.address = val

    @property
    def localidad(self):
        return self.city

    @localidad.setter
    def localidad(self, val):
        self.city = val

    @property
    def provincia(self):
        return self.state

    @provincia.setter
    def provincia(self, val):
        self.state = val

    @property
    def codigo_postal(self):
        return self.zip_code

    @codigo_postal.setter
    def codigo_postal(self, val):
        self.zip_code = val

    @property
    def cep(self):
        return self.zip_code

    @cep.setter
    def cep(self, val):
        self.zip_code = val

    @property
    def postal_code(self):
        return self.zip_code

    @postal_code.setter
    def postal_code(self, val):
        self.zip_code = val

    @property
    def obra_social(self):
        return self.insurance_provider

    @obra_social.setter
    def obra_social(self, val):
        self.insurance_provider = val

    @property
    def numero_afiliado(self):
        return self.policy_number

    @numero_afiliado.setter
    def numero_afiliado(self, val):
        self.policy_number = val

    @property
    def diagnostico_clinico(self):
        return self.diagnosis

    @diagnostico_clinico.setter
    def diagnostico_clinico(self, val):
        self.diagnosis = val

    @property
    def historia_clinica(self):
        return self.clinical_notes

    @historia_clinica.setter
    def historia_clinica(self, val):
        self.clinical_notes = val

    @property
    def medico_asignado(self):
        return self.assigned_doctor

    @medico_asignado.setter
    def medico_asignado(self, val):
        self.assigned_doctor = val

    @property
    def medico_asignado_id(self):
        return self.assigned_doctor_id

    @medico_asignado_id.setter
    def medico_asignado_id(self, val):
        self.assigned_doctor_id = val

    @property
    def nombre_completo(self):
        return f"{self.last_name}, {self.first_name}"
