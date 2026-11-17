import random
from datetime import date, timedelta

from core.management.seed_base import BaseSeedCommand, email_slug
from core.synthetic_identifiers import generate_us_ssn as generate_valid_ssn, generate_us_npi as generate_valid_npi, generate_us_state_id

FIRST_NAMES_MALE = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", 
    "Joseph", "Thomas", "Charles", "Daniel", "Matthew", "Anthony", "Mark", "Donald", 
    "Steven", "Andrew", "Paul", "Joshua", "Kenneth", "Kevin", "Brian", "Timothy", 
    "Ronald", "Jason", "Edward", "Jeffrey", "Ryan", "Jacob", "Gary", "Nicholas", 
    "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin", 
    "Samuel", "Gregory", "Alexander", "Patrick", "Frank", "Raymond", "Jack", "Dennis", 
    "Jerry", "Tyler", "Aaron", "Henry", "Douglas", "Peter", "Zachary", "Nathan"
]

FIRST_NAMES_FEMALE = [
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", 
    "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra", 
    "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Carol", "Amanda", "Melissa", 
    "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia", "Kathleen", "Amy", 
    "Angela", "Shirley", "Anna", "Brenda", "Pamela", "Emma", "Nicole", "Helen", 
    "Samantha", "Katherine", "Christine", "Debra", "Rachel", "Carolyn", "Janet", 
    "Catherine", "Maria", "Heather", "Diane", "Olivia", "Ava", "Sophia", "Chloe"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", 
    "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "Martin", "Lee", 
    "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", 
    "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", 
    "Nguyen", "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", 
    "Rivera", "Campbell", "Mitchell", "Carter", "Roberts", "Gomez", "Phillips", 
    "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes", 
    "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz"
]

SPECIALTIES_USA = [
    ("Cardiology", "Diagnosis and treatment of congenital and acquired heart conditions and cardiovascular diseases"),
    ("Internal Medicine", "Comprehensive long-term adult care, preventive health and multi-system pathology"),
    ("Orthopedic Surgery", "Surgical and non-surgical treatment of musculoskeletal system diseases and spine disorders"),
    ("Pediatrics", "Primary and preventive medical care for infants, children, and adolescents"),
    ("Dermatology", "Clinical diagnosis and therapeutic management of skin, mucous membranes, hair and nail diseases"),
    ("Neurology", "Investigation, management, and treatment of central and peripheral nervous system disorders"),
    ("Gastroenterology", "Clinical care of gastrointestinal tract, liver, biliary system, and pancreatic disorders"),
    ("Ophthalmology", "Comprehensive eye examinations, optical correction, and microsurgical visual treatments"),
    ("Pulmonology", "Diseases of the respiratory tract, chronic airway obstruction and cardiopulmonary disorders"),
    ("Obstetrics & Gynecology", "Comprehensive female reproductive wellness, prenatal management, labor and delivery"),
    ("Urology", "Disorders of the male and female urinary tract and the male reproductive system"),
    ("Diagnostic Radiology", "Diagnostic imaging modalities including computerized tomography (CT), MRI and sonography")
]

INSURANCE_PROVIDERS = [
    "Blue Cross Blue Shield", "UnitedHealthcare Choice Plus", "Kaiser Permanente Premier", 
    "Aetna Open Choice PPO", "Cigna Health and Life", "Humana Gold Plus", "Medicare Part B", "Medicaid Care"
]

DIAGNOSES_BY_SPECIALTY = {
    "Cardiology": [
        ("Stage 2 Essential Hypertension", "Patient presents with persistent blood pressure measurements exceeding 150/95 mmHg. Adjusted oral enalapril 10mg daily and dietary sodium restriction."),
        ("Paroxysmal Atrial Fibrillation", "Acute episode converted spontaneously. Ordered 24-hour ambulatory Holter electrocardiography and initiated direct oral anticoagulant prophylaxis."),
        ("Chronic Ischemic Heart Disease", "Exertional angina pectoris Canadian Class II. Transthoracic echocardiogram shows preserved ejection fraction (55%). Up-titrated beta-blocker therapy.")
    ],
    "Internal Medicine": [
        ("Type 2 Diabetes Mellitus with Hyperglycemia", "Quarterly glycemic evaluation. Glycated hemoglobin (HbA1c) measured at 7.9%. Metformin dosage titrated and clinical nutritionist consultation requested."),
        ("Chronic Peripheral Venous Insufficiency", "Bilateral dependent lower extremity pitting edema worse in evenings. Prescribed graduated compression stockings (20-30 mmHg) and daily walking."),
        ("Metabolic Syndrome with Mixed Dyslipidemia", "Elevated fasting triglycerides and depressed HDL cholesterol. Counseled on therapeutic lifestyle modifications and initiated atorvastatin 20mg.")
    ],
    "Orthopedic Surgery": [
        ("Acute Lumbosacral Strain", "Severe disabling lower back pain following lifting mechanical stress. Lumbar radiographs demonstrate no vertebral fracture. Prescribed 72h rest and NSAID regimen."),
        ("Right Knee Medial Collateral Ligament Sprain (Grade I)", "Valgus stress tenderness without joint instability. Conservative management with functional knee brace and outpatient physical rehabilitation."),
        ("Rotator Cuff Tendinopathy", "Nocturnal shoulder discomfort with painful arc on active abduction. Diagnostic ultrasound reveals subacromial impingement and supraspinatus thickening.")
    ],
    "Pediatrics": [
        ("Routine Well-Child Examination & Growth Milestones", "Normal pediatric developmental progress at 50th percentile for stature and weight. Immunization schedule complete. Age-appropriate anticipatory guidance provided."),
        ("Mild Acute Viral Bronchiolitis", "Infant presents with low-grade coryza and mild expiratory wheezing. Adequate room air oxygen saturation (98%). Outpatient symptomatic hydration therapy."),
        ("Acute Viral Pediatric Gastroenteritis", "24-hour history of loose non-bloody stools without clinical dehydration. Prescribed oral rehydration solution (Pedialyte) and bland nutrition.")
    ],
    "Dermatology": [
        ("Moderate Atopic Dermatitis", "Erythematous pruriginous flexural eczema on antecubital and popliteal folds. Prescribed topical corticosteroid burst therapy and ceramide emollient maintenance."),
        ("Plaque Psoriasis (Moderate)", "Well-demarcated erythematous scaly plaques over bilateral extensor surfaces of knees and elbows. Initiated combination topical calcipotriene ointment."),
        ("Dermoscopic Melanocytic Nevus Surveillance", "Full-body cutaneous examination without malignant asymmetry, border irregularity, or color variegation. Advised broad-spectrum SPF 50+ photoprotection.")
    ],
    "Neurology": [
        ("Episodic Tension-Type Headache", "Bilateral non-pulsatile pressing cranial pain associated with workplace fatigue. Brain magnetic resonance imaging (MRI) unremarkable. Initiated prophylactic regimen."),
        ("Classic Migraine with Visual Aura", "Hemicranial throbbing headache preceded by scintillating scotomas and photophobia. Prescribed sumatriptan 50mg for acute abortive therapy at onset."),
        ("Mild Distal Symmetrical Polyneuropathy", "Bilateral stocking-distribution sensory dysesthesias. Scheduled nerve conduction studies (NCS) and electromyography to evaluate peripheral axonal integrity.")
    ],
    "Gastroenterology": [
        ("Acute Viral Gastroenteritis", "48-hour history of nausea, emesis and watery non-inflammatory diarrhea. Oral electrolyte rehydration well tolerated without signs of hypovolemia."),
        ("Gastroesophageal Reflux Disease (GERD)", "Nocturnal retrosternal pyrosis and acid regurgitation. Initiated therapeutic 8-week course of proton pump inhibitor (pantoprazole 40mg daily)."),
        ("Irritable Bowel Syndrome with Mixed Pattern", "Recurrent lower quadrant cramping relieved by defecation. Normal diagnostic serology. Transitioned to structured low-FODMAP dietary intervention.")
    ],
    "Ophthalmology": [
        ("Compound Myopic Astigmatism", "Bilateral blurred distance vision progression. Dilated fundoscopic examination unremarkable. Updated corrective spectacle prescription provided."),
        ("Acute Bacterial Conjunctivitis", "Bilateral conjunctival hyperemia with copious mucopurulent exudate. Prescribed topical ophthalmic tobramycin drops every 6 hours for 7 days."),
        ("Open-Angle Glaucoma Suspect", "Bilateral intraocular pressure elevation (22 mmHg). Ordered baseline automated Humphrey visual field perimetry and optical coherence tomography of optic nerve.")
    ],
    "Pulmonology": [
        ("Mild Acute Asthma Exacerbation", "Diagnostic spirometry confirms reversible expiratory airway obstruction. Optimized inhaled corticosteroid and long-acting beta-agonist (ICS/LABA) maintenance."),
        ("Moderate Acute COPD Exacerbation", "Chronic tobacco smoker with increased cough and exertional dyspnea (mMRC grade 2). Prescribed short-course oral prednisone and dual bronchodilator therapy."),
        ("Community-Acquired Lobar Pneumonia", "Chest radiograph confirms right lower lobe consolidation with fever and productive cough. Initiated outpatient oral antibiotic therapy with amoxicillin/clavulanate.")
    ],
    "Obstetrics & Gynecology": [
        ("Annual Well-Woman Gynecological Exam", "Cervical cytology (Pap smear) and pelvic bimanual exam without palpable masses or cervical atypia. Normal clinical breast examination."),
        ("First-Trimester Prenatal Care (10 Weeks)", "Intrauterine gestational sac identified on pelvic sonogram with positive embryonic cardiac motion (168 bpm). Initiated prenatal vitamin and folic acid supplementation."),
        ("Polycystic Ovary Syndrome (PCOS)", "Oligomenorrhea with biochemical hyperandrogenism and pelvic sonographic confirmation. Prescribed oral combined hormonal contraceptive therapy.")
    ],
    "Urology": [
        ("Benign Prostatic Hyperplasia (BPH)", "Lower urinary tract obstructive symptoms with weak stream and nocturia. Serum PSA within age-adjusted range (1.6 ng/mL). Prescribed tamsulosin 0.4mg daily."),
        ("Ureteral Calculus with Renal Colic", "Acute unilateral flank pain radiating to groin. Non-contrast abdominopelvic CT confirms 3.8mm obstructing stone in distal ureter. Conservative medical expulsion therapy."),
        ("Uncomplicated Lower Urinary Tract Infection", "48-hour dysuria and urinary frequency without costovertebral tenderness. Midstream urinalysis confirms pyuria. Initiated oral antibiotic regimen.")
    ],
    "Diagnostic Radiology": [
        ("Thyroid Nodule Sonographic Assessment (TI-RADS 3)", "High-resolution neck ultrasound demonstrates a solitary 1.2cm solid iso-echoic nodule. Recommended repeat surveillance sonogram in 12 months."),
        ("Lumbosacral Radiculopathy - L5-S1 Disc Herniation", "Lumbar spine MRI reveals a focal paracentral posterior disc protrusion contacting the traversing S1 nerve root."),
        ("Diffuse Hepatic Steatosis (Grade II)", "Upper abdominal sonogram reveals diffusely increased hepatic parenchymal echogenicity consistent with non-alcoholic fatty liver disease.")
    ]
}

LOCATIONS_USA = [
    ("Fifth Avenue", "New York", "NY", "10022"),
    ("Broadway", "New York", "NY", "10003"),
    ("Michigan Avenue", "Chicago", "IL", "60611"),
    ("Sunset Boulevard", "Los Angeles", "CA", "90028"),
    ("Peachtree Street", "Atlanta", "GA", "30309"),
    ("Beacon Street", "Boston", "MA", "02116"),
    ("Market Street", "San Francisco", "CA", "94102"),
    ("Biscayne Boulevard", "Miami", "FL", "33132"),
    ("Congress Avenue", "Austin", "TX", "78701"),
    ("Pike Street", "Seattle", "WA", "98101")
]


class Command(BaseSeedCommand):
    help = 'Populates the US database with realistic SSNs, NPIs, and clinical history for HIPAA compliance.'
    country = 'US'

    # No FOREIGN KEY on purpose: allows the TRUNCATE of on-the-fly masking.
    ddl = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SPECIALTIES')
        CREATE TABLE SPECIALTIES (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            SPECIALTY NVARCHAR(60) NOT NULL UNIQUE,
            DESCRIPTION NVARCHAR(255) NULL
        );

        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DOCTORS')
        CREATE TABLE DOCTORS (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            NPI NVARCHAR(20) NOT NULL UNIQUE,
            STATE_LICENSE NVARCHAR(20) NULL,
            SSN NVARCHAR(15) NOT NULL UNIQUE,
            STATE_ID NVARCHAR(15) NOT NULL UNIQUE,
            LAST_NAME NVARCHAR(60) NOT NULL,
            FIRST_NAME NVARCHAR(60) NOT NULL,
            SPECIALTY_ID INT NOT NULL,
            PHONE_NUMBER NVARCHAR(25) NOT NULL,
            EMAIL NVARCHAR(100) NOT NULL
        );

        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PATIENTS')
        CREATE TABLE PATIENTS (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            SSN NVARCHAR(15) NOT NULL UNIQUE,
            STATE_ID NVARCHAR(15) NOT NULL UNIQUE,
            LAST_NAME NVARCHAR(60) NOT NULL,
            FIRST_NAME NVARCHAR(60) NOT NULL,
            DATE_OF_BIRTH DATE NOT NULL,
            PHONE_NUMBER NVARCHAR(25) NOT NULL,
            EMAIL NVARCHAR(100) NOT NULL,
            ADDRESS NVARCHAR(120) NOT NULL,
            CITY NVARCHAR(60) NOT NULL,
            STATE NVARCHAR(10) NOT NULL,
            ZIP_CODE NVARCHAR(10) NOT NULL,
            INSURANCE_PROVIDER NVARCHAR(60) NOT NULL,
            POLICY_NUMBER NVARCHAR(30) NOT NULL,
            DIAGNOSIS NVARCHAR(150) NOT NULL,
            CLINICAL_NOTES NVARCHAR(MAX) NOT NULL,
            DOCTOR_ID INT NULL,
            ADMISSION_DATE DATE NOT NULL DEFAULT GETDATE()
        );
    """

    def get_models(self):
        from core.models_us import Specialty, Doctor, Patient
        return (Specialty, Doctor, Patient)

    def populate(self, cant_medicos, cant_pacientes):
        Specialty, Doctor, Patient = self.get_models()

        # 1. Specialties
        self.stdout.write("-> Creating medical specialties catalog (USA)...")
        specialties_objs = [
            Specialty.objects.create(specialty=s_name, description=s_desc)
            for s_name, s_desc in SPECIALTIES_USA
        ]

        # 2. Doctors
        self.stdout.write(f"-> Generating {cant_medicos} US physicians with NPI and State Licenses...")
        doctors_created = []
        used_names = set()
        used_npis, used_ssns, used_state_ids = set(), set(), set()

        for i in range(cant_medicos):
            gender, first_name, last_name = self.pick_person(FIRST_NAMES_MALE, FIRST_NAMES_FEMALE, LAST_NAMES, used_names)

            npi = self.unique(generate_valid_npi, used_npis)
            ssn = self.unique(generate_valid_ssn, used_ssns)
            state_code = random.choice(['NY', 'CA', 'IL', 'TX', 'GA', 'MA'])
            state_id = self.unique(lambda: f"{state_code}-D{random.randint(1000000, 9999999)}", used_state_ids)
            state_lic = f"MD-{state_code}-{random.randint(10000, 99999)}"
            spec = specialties_objs[i % len(specialties_objs)]
            phone = f"+1 ({random.randint(201, 989)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
            email = f"dr.{email_slug(first_name)}.{email_slug(last_name)}@metropolitanhospital.org"

            doc = Doctor.objects.create(
                npi=npi,
                state_license=state_lic,
                ssn=ssn,
                state_id=state_id,
                last_name=last_name,
                first_name=first_name,
                specialty=spec,
                phone_number=phone,
                email=email
            )
            doctors_created.append(doc)

        # 3. Patients
        self.stdout.write(f"-> Generating {cant_pacientes} US patients with HIPAA-compliant PHI data...")
        today = date.today()
        used_ssns, used_state_ids = set(), set()

        for j in range(cant_pacientes):
            gender, first_name, last_name = self.pick_person(FIRST_NAMES_MALE, FIRST_NAMES_FEMALE, LAST_NAMES, used_names)

            ssn = self.unique(generate_valid_ssn, used_ssns)
            street, city, state, zip_code = random.choice(LOCATIONS_USA)
            state_id = self.unique(lambda: generate_us_state_id(state), used_state_ids)
            street_num = random.randint(10, 9999)
            apt = f", Apt {random.randint(1, 24)}{random.choice(['A', 'B', 'C', 'D'])}" if random.random() > 0.4 else ""
            address = f"{street_num} {street}{apt}"

            age_days = random.randint(18 * 365, 80 * 365)
            dob = today - timedelta(days=age_days)

            insurance = random.choice(INSURANCE_PROVIDERS)
            policy = f"POL-{random.choice(['A', 'B', 'C', 'X'])}{random.randint(10000000, 99999999)}"

            # Physician & Diagnosis match
            if gender == 'M':
                candidates = [d for d in doctors_created if d.specialty.specialty != 'Obstetrics & Gynecology']
            else:
                candidates = doctors_created
            assigned_doc = random.choice(candidates if candidates else doctors_created)

            possible_diags = DIAGNOSES_BY_SPECIALTY.get(
                assigned_doc.specialty.specialty,
                [("Routine Clinical Preventive Checkup", "Comprehensive periodic health examination without acute complaints.")]
            )
            if assigned_doc.specialty.specialty == 'Urology' and gender == 'F':
                possible_diags = [d for d in possible_diags if "prostatic" not in d[0].lower()]
            diag_title, diag_notes = random.choice(possible_diags)

            phone = f"+1 ({random.randint(201, 989)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
            email = f"{email_slug(first_name)}.{email_slug(last_name)}{random.randint(10, 99)}@gmail.com"

            Patient.objects.create(
                ssn=ssn,
                state_id=state_id,
                last_name=last_name,
                first_name=first_name,
                date_of_birth=dob,
                phone_number=phone,
                email=email,
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                insurance_provider=insurance,
                policy_number=policy,
                diagnosis=diag_title,
                clinical_notes=diag_notes,
                assigned_doctor=assigned_doc
            )

        return (
            f"Success! Created {len(specialties_objs)} specialties, {cant_medicos} physicians with synthetic NPIs, "
            f"and {cant_pacientes} patients with formatted SSNs."
        )
