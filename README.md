# HMS 3.0 - Metropolitan Hospital Management System
### Delphix Continuous Compliance & Continuous Data (Data Virtualization) Demonstration Platform

[![Delphix Continuous Compliance](https://img.shields.io/badge/Delphix-Continuous%20Compliance-blue.svg)](https://www.delphix.com)
[![Delphix Data Virtualization](https://img.shields.io/badge/Delphix-Data%20Virtualization-green.svg)](https://www.delphix.com)
[![Microsoft SQL Server](https://img.shields.io/badge/Database-SQL%20Server%202019%2F2022-red.svg)](https://www.microsoft.com/sql-server)
[![Python 3.11 / Django 5](https://img.shields.io/badge/Backend-Django%205%20%7C%20Python%203.11-092E20.svg)](https://www.djangoproject.com)
[![Podman / Docker](https://img.shields.io/badge/Container-Podman%20%2F%20Docker-892CA0.svg)](https://podman.io)

---

## 📋 Executive Overview

**HMS 3.0** is a hospital management reference application built specifically for **Presales Engineers, Solution Architects, and Technical Consultants** demonstrating the power of the **Delphix DevOps Data Platform** against **Microsoft SQL Server**.

It showcases end-to-end data lifecycle capabilities:
1. **Automated Sensitive Data Discovery & Profiling**: Native table and column naming conventions tailored for Delphix Profilers across three international regulatory jurisdictions.
2. **Deterministic & Referential Data Masking**: Replaces Personally Identifiable Information (PII) and Protected Health Information (PHI) with synthetically valid, referentially intact masked equivalents.
3. **Instant Virtual Database (VDB) Provisioning**: Delivers near-instant, zero-storage-footprint virtual copies of SQL Server databases for development and test (UAT/QA).
4. **Self-Service VDB Lifecycle (Rewind / Refresh)**: Allows instant rollback of accidental data deletion or corruption in seconds directly via Delphix Data Control Tower (DCT).

---

## 🌍 Multi-Country Regulatory Architecture

HMS 3.0 supports **three independent country modes**, dynamically selected via the `HMS_COUNTRY` and `DB_NAME` environment variables. The application adapts its database schema, table names, sensitive column identifiers, UI language, clinical terminologies, and regulatory compliance notices accordingly.

```
                      ┌──────────────────────────────────────┐
                      │          HMS 3.0 Application         │
                      │       Environment: HMS_COUNTRY       │
                      └──────────────────┬───────────────────┘
                                         │
         ┌───────────────────────────────┼──────────────────────────────┐
         ▼                               ▼                              ▼
  🇦🇷 ARGENTINA                    🇧🇷 BRAZIL                      🇺🇸 UNITED STATES
  ───────────────────────         ───────────────────────        ───────────────────────
  Standard: Ley 25.326            Standard: LGPD (13.709)        Standard: HIPAA (PHI)
  Language: Spanish               Language: Portuguese           Language: English
  Prod DB : hms3_ar               Prod DB : hms3_br              Prod DB : hms3_us
  Test VDB: vhms3_ar              Test VDB: vhms3_br             Test VDB: vhms3_us
```

### Country Comparison Matrix

| Attribute / Field | 🇦🇷 Argentina (AR) | 🇧🇷 Brazil (BR) | 🇺🇸 United States (US) |
| :--- | :--- | :--- | :--- |
| **Regulatory Law** | Ley 25.326 (Protección Datos) | LGPD (Lei 13.709/2018) | HIPAA (45 CFR § 164.514) |
| **Production Database** | `hms3_ar` | `hms3_br` | `hms3_us` |
| **Test Virtual Database** | `vhms3_ar` | `vhms3_br` | `vhms3_us` |
| **Patients Table** | `dbo.PACIENTES` | `dbo.PACIENTES` | `dbo.PATIENTS` |
| **Doctors Table** | `dbo.MEDICOS` | `dbo.MEDICOS` | `dbo.DOCTORS` |
| **Specialties Table** | `dbo.ESPECIALIDADES` | `dbo.ESPECIALIDADES` | `dbo.SPECIALTIES` |
| **Primary National ID** | `DNI` (Documento Nacional) | `CPF` (Cadastro de Pessoas Físicas) | `SSN` (Social Security Number) |
| **Secondary National ID**| `CUIL` (Módulo 11) | `RG` (Registro Geral) | `STATE_ID` (Driver License) |
| **Medical License ID** | `MATRICULA_NACIONAL` (MN) | `CRM` (Conselho Regional) | `NPI` (National Provider Identifier) |
| **Postal Code** | `CODIGO_POSTAL` (CP) | `CEP` | `ZIP_CODE` |
| **Health Insurance** | `OBRA_SOCIAL` / `NUMERO_AFILIADO` | `CONVENIO` / `NUMERO_CARTEIRINHA`| `INSURANCE_PROVIDER` / `POLICY_NUMBER` |
| **Clinical Notes (PHI)** | `HISTORIA_CLINICA` | `PRONTUARIO` | `CLINICAL_NOTES` |

---

## 🎯 Native Delphix Profiler Discovery Architecture

Delphix Continuous Compliance profilers discover sensitive columns using regular expression pattern matching on column and table metadata. 

### Why Native Schemas Matter for Presales
In traditional demonstration applications, column names often fail to trigger out-of-the-box Delphix Profiler rules (e.g. naming a Brazilian CPF column `national_id_number` or `doc_2`). 

HMS 3.0 uses **native uppercase schemas** for each country:
* **Brazil**: Columns `CPF`, `RG`, and `CRM` immediately trigger Delphix built-in or custom Brazilian profilers.
* **USA**: Columns `SSN`, `STATE_ID`, `NPI`, `ZIP_CODE`, and `CLINICAL_NOTES` trigger 100% of Delphix HIPAA and US PII built-in profiling rules without requiring manual profiling adjustments.
* **Argentina**: Columns `DNI` and `CUIL` trigger Argentine custom plugin profilers (`AR_DNI` and `AR_CUILT`) and/or `AR_CUIT` in standard Perforce Profile Sets.

---

## ⚡ Zero-Cache Multi-Environment Architecture

A critical challenge during live demonstrations is comparing **Production (Port 8012)** against **Masked Test VDB (Port 8013)** simultaneously. HMS 3.0 solves all browser caching and cookie collision issues:

1. **Environment Cookie Isolation**:
   * Session cookies and CSRF tokens are dynamically suffixed with the active environment:
     ```python
     SESSION_COOKIE_NAME = f'hms3_session_{HMS_ENV}'
     CSRF_COOKIE_NAME = f'hms3_csrf_{HMS_ENV}'
     ```
   * This permits opening Production and Test VDB in **adjacent tabs of the exact same browser window** without session collisions or CSRF invalidations.

2. **Strict HTTP Anti-Cache Middleware (`NoCacheMiddleware`)**:
   * Every HTTP response emits strict anti-caching headers:
     ```http
     Cache-Control: no-cache, no-store, must-revalidate, max-age=0, post-check=0, pre-check=0
     Pragma: no-cache
     Expires: 0
     X-Accel-Expires: 0
     ```

3. **Client-Side Cache Bypass**:
   * A prominent **`[🔄 Refresh Data]`** button in the top navigation bar forces a clean browser reload appending a dynamic timestamp query (`?_nocache=<timestamp>`), bypassing modern browser Back-Forward Cache (bfcache).

4. **Visual Environment Banners**:
   * **Production (Port 8012)**: Crimson red banner with warning icons and legal notice:
     `PRODUCTION ENVIRONMENT: REAL SENSITIVE DATA (HIPAA / PHI) | DB: hms3_us | Port: 8012`
   * **Test VDB (Port 8013)**: Forest green banner indicating Delphix continuous compliance:
     `TEST VDB ENVIRONMENT: MASKED BY DELPHIX | DB: vhms3_us | Port: 8013`
   * **Live Microsecond Clock**: Millisecond-precision server clock in the navbar confirms data was dynamically queried from SQL Server without stale rendering.

---

## 📦 Container Image Building

HMS 3.0 uses an optimized multi-stage `Dockerfile.django` based on `python:3.11-slim-bookworm` with Microsoft's official ODBC Driver 18 for SQL Server.

### Build the Image
From the repository root:
```bash
sudo podman build -t hms3-app:1.0 -f Dockerfile.django .
```

*Note: If using standard Docker, substitute `sudo podman` with `docker`.*

---

## ⚙️ Configuration & Environment Templates

HMS 3.0 provides pre-configured template files (`.example`) for each environment and jurisdiction:

| Template File | Environment | Country | Port | Database | Real Config (Local Only) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `.env-prod-ar.example` | Production | Argentina (`AR`) | `8012` | `hms3_ar` | `.env-prod-ar` |
| `.env-test-ar.example` | Test VDB | Argentina (`AR`) | `8013` | `vhms3_ar` | `.env-test-ar` |
| `.env-prod-br.example` | Production | Brazil (`BR`) | `8012` | `hms3_br` | `.env-prod-br` |
| `.env-test-br.example` | Test VDB | Brazil (`BR`) | `8013` | `vhms3_br` | `.env-test-br` |
| `.env-prod-us.example` | Production | USA (`US`) | `8012` | `hms3_us` | `.env-prod-us` |
| `.env-test-us.example` | Test VDB | USA (`US`) | `8013` | `vhms3_us` | `.env-test-us` |

> **Security Notice**: All real `.env*` configuration files containing active database credentials are strictly excluded via `.gitignore`. Copy the appropriate `.example` file to its corresponding `.env-*` filename and configure your local SQL Server connection credentials.

### Environment Variable Reference

```ini
# Core Configuration
DJANGO_SECRET_KEY=hms3-secret-key-replace-in-production
ALLOWED_HOSTS=*
DEBUG=True

# Environment & Localization
HMS_ENV=prod                  # 'prod' (8012) or 'test' (8013)
HMS_COUNTRY=US                # 'AR', 'BR', or 'US'
HMS_CONTAINER_NAME=hms3_prod  # 'hms3_prod' or 'hms3_test'
HOST_PORT=8012                # Port mapped on the host

# SQL Server Instance Connection
DB_HOST=10.0.0.10             # SQL Server IP or Hostname
DB_PORT=1433                  # Default SQL Server Port
DB_NAME=hms3_us               # Target Database
DB_USER=sa                    # SQL Server User
DB_PASSWORD=YourStrongPasswordHere  # SQL Server Password
```

---

## 🚀 Container Orchestration CLI (`hms-ctl.py`)

HMS 3.0 includes an all-in-one Python CLI controller (**`hms-ctl.py`**) that supports both **Podman** and **Docker** automatically with zero host dependencies (uses Python standard library).

```bash
./hms-ctl.py <command> -e <prod|test> -c <ar|br|us>
```

### Available Commands

| Command | Arguments | Description |
| :--- | :--- | :--- |
| `start` | `-e <prod\|test> -c <ar\|br\|us> [-b]` | Starts the specified container environment (optionally `-b` to rebuild image). |
| `stop` | `-e <prod\|test> [-t seconds]` | Cleanly stops the container (default graceful timeout: 2s). |
| `restart` | `-e <prod\|test> -c <ar\|br\|us>` | Restarts the container with the selected configuration. |
| `status` | *(none)* | Displays a live summary table of all environments (ports 8012 & 8013). |
| `logs` | `-e <prod\|test> [-f] [-n lines]` | Displays or follows live container logs. |
| `rm` | `-e <prod\|test> [-f]` | Removes the specified container cleanly without throwing errors if missing. |
| `build` | `[-t tag] [--no-cache]` | Rebuilds the HMS 3.0 container image. |

### CLI Examples

```bash
# Start environments
./hms-ctl.py start -e prod -c ar       # Production Argentina on port 8012
./hms-ctl.py start -e test -c br       # Non-Production (masked) Brazil on port 8013

# Check status of both environments
./hms-ctl.py status

# Follow logs in real time
./hms-ctl.py logs -e prod -f

# Clean stop and removal
./hms-ctl.py stop -e prod
./hms-ctl.py rm -e prod -f
```

---

## 📜 Legacy Deployment Script (`launch_hms.sh`)

Deploying can also be done via the legacy bash script:

```bash
./launch_hms.sh [prod|test] [ar|br|us]
```
*(If the country argument is omitted, it defaults to `ar`)*.

### Deployment Examples

#### 1. Argentina Deployments
```bash
# Launch Production Argentina on port 8012 (DB: hms3_ar)
./launch_hms.sh prod ar

# Launch Test VDB Argentina on port 8013 (DB: vhms3_ar)
./launch_hms.sh test ar
```

#### 2. Brazil Deployments
```bash
# Launch Production Brazil on port 8012 (DB: hms3_br)
./launch_hms.sh prod br

# Launch Test VDB Brazil on port 8013 (DB: vhms3_br)
./launch_hms.sh test br
```

#### 3. USA Deployments
```bash
# Launch Production USA on port 8012 (DB: hms3_us)
./launch_hms.sh prod us

# Launch Test VDB USA on port 8013 (DB: vhms3_us)
./launch_hms.sh test us
```

---

## 🧪 Database Seeding & Synthetic Data Generators

HMS 3.0 includes dedicated Django management commands to populate production databases with realistic, regulatory-compliant synthetic data.

### 1. Seeding Argentina (`seed_argentina`)
* **Identifiers**: Generates valid Argentine DNIs and mathematical Modulo 11 CUILs (`20-XXXXXXXX-X`, `27-XXXXXXXX-X`, `23-XXXXXXXX-X`).
* **Medical Licensing**: Generates valid Matrícula Nacional (MN) and Provincial (MP).
* **Command Syntax**:
  ```bash
  # Seed Production Argentina (Resets ID sequences to 1):
  sudo podman exec hms3_prod python manage.py seed_argentina --clean
  ```

### 2. Seeding Brazil (`seed_brazil`)
* **Identifiers**: Generates official Receita Federal CPFs with 2 check digits verified via Modulo 11 (`XXX.XXX.XXX-XX`), and realistic RGs.
* **Medical Licensing**: Generates Conselho Regional de Medicina (CRM) with State codes (`CRM/SP`, `CRM/RJ`).
* **Command Syntax**:
  ```bash
  # Seed Production Brazil (Resets ID sequences to 1):
  sudo podman exec hms3_prod python manage.py seed_brazil --clean
  ```

### 3. Seeding USA (`seed_usa`)
* **Identifiers**: Generates Social Security Numbers (SSN) compliant with Social Security Administration rules (no `000` area, `00` group, `0000` serial, or `666` prefix) formatted as `XXX-XX-XXXX`, plus State IDs.
* **Medical Licensing**: Generates CMS National Provider Identifiers (NPI) validated with the **Luhn Modulo 10 check digit** algorithm (standard 10-digit NPIs starting with `1` or `2`).
* **Command Syntax**:
  ```bash
  # Seed Production USA (Resets ID sequences to 1):
  sudo podman exec hms3_prod python manage.py seed_usa --clean
  ```

### Seeding Command Options
All three seeding commands accept the following options:
* `--clean`: Resets the database state: truncates existing tables, executes `DBCC CHECKIDENT ('<TABLE>', RESEED, 0)` in SQL Server, and ensures new records begin sequentially at **ID 1**.
* `--pacientes <N>`: Number of patients to generate (default: `40`).
* `--medicos <M>`: Number of physicians to generate (default: `10`).

### Clinical & Diagnostic Consistency
All seeders enforce strict clinical logic:
* Each patient is assigned an attending physician.
* The patient's diagnosis and confidential clinical history (`HISTORIA_CLINICA` / `PRONTUARIO` / `CLINICAL_NOTES`) directly match the assigned physician's medical specialty (e.g., Cardiology $\to$ Acute Myocardial Infarction / Hypertension; Pulmonology $\to$ COPD / Bronchial Asthma; Neurology $\to$ Migraine / Epilepsy).
* Gender consistency is enforced for gender-specific specialties (e.g., Gynecology vs Urology).

---

## 🎬 Presales Demonstration Playbook

This step-by-step walkthrough demonstrates how to deliver an impactful Delphix Continuous Compliance & Data Virtualization presentation following the official Delphix presales methodology:

### Step 1: Deploy Production & Generate Fresh Data
```bash
# 1. Deploy Production (Port 8012) - Example: Argentina
./launch_hms.sh prod ar

# 2. Populate fresh, clean records starting at ID 1
sudo podman exec hms3_prod python manage.py seed_argentina --clean
```
*Show the audience the Production UI at `http://<HOST-IP>:8012/`.* Point out the unmasked DNIs, CUILs, patient names, addresses, and confidential medical histories under the crimson red Production banner.

### Step 2: Ingest Production (dSource) & Virtualize (VDB Provisioning)
1. In the **Delphix Engine / Data Control Tower (DCT)**, link the production SQL Server database (`hms3_ar`, `hms3_br`, or `hms3_us`) as a **dSource**.
2. Run the initial sync (**SnapSync**) to establish the Timeflow baseline.
3. Instantly provision a **Virtual Database (VDB)** named `vhms3_ar` (or `vhms3_br` / `vhms3_us`) to the non-production target SQL Server environment.
   * *Highlight to the customer*: The VDB provisions in seconds and consumes near-zero incremental disk storage, completely independent of database size.

### Step 3: Profile the Non-Production VDB
1. Connect the **Delphix Continuous Compliance Engine** to the newly provisioned non-production VDB (`vhms3_ar`).
2. Execute the **Delphix Profiler** directly against the VDB.
   * *Critical Presales Advantage*: Profiling the virtual copy eliminates all performance overhead, query locking, or compliance exposure on the active production database.
3. Demonstrate automated discovery:
   * 🇦🇷 **Argentina**: `DNI`, `CUIL` (matched by `AR_DNI`, `AR_CUILT` and/or `AR_CUIT` in Perforce Profile Sets), `APELLIDO`, `NOMBRE`, `DIRECCION`, `HISTORIA_CLINICA`.
   * 🇧🇷 **Brazil**: `CPF`, `RG`, `CRM`, `SOBRENOME`, `NOME`, `CEP`, `PRONTUARIO`.
   * 🇺🇸 **USA**: `SSN`, `STATE_ID`, `NPI`, `LAST_NAME`, `FIRST_NAME`, `ZIP_CODE`, `CLINICAL_NOTES`.

### Step 4: Execute In-Place Masking on the VDB
1. Assign the appropriate algorithms in the Inventory / Rule Set (e.g., `AR_DNI`, `AR_CUILT`, `dlpx-core:Phone Unique`, `First Name`, `Last Name`, `Address`, `Comment / Free Text`).
2. Run the Delphix Masking Job **in-place directly on the VDB**.
   * *Highlight to the customer*: Delphix masks the data in-place on the target environment. Sensitive data never leaves the security perimeter, and referential integrity across related tables is mathematically preserved.
3. Once the masking job completes, capture a snapshot / bookmark of the VDB in Delphix DCT to establish a clean "Masked Baseline".

### Step 5: Deploy Test Application & Verify Side-by-Side
1. Deploy the Test VDB application container:
   ```bash
   ./launch_hms.sh test ar
   ```
2. Open both environments in adjacent browser tabs:
   * **Left Tab (Prod)**: `http://<HOST-IP>:8012/` (Red Banner - Real Production Data)
   * **Right Tab (Test VDB)**: `http://<HOST-IP>:8013/` (Green Banner - Masked by Delphix)
3. **Key Points to Highlight to the Customer**:
   * Record counts and primary keys (IDs 1 to 40) are identical between Prod and Test VDB.
   * Names, identification numbers, contact information, and diagnoses are realistically and consistently masked.
   * The hospital application operates 100% normally without any application changes.

### Step 6: Simulate UAT Accidental Data Deletion & Regression
1. On the **Test VDB (Port 8013)**, open a patient record (e.g., Patient ID #1).
2. Click **`[🗑️ Delete Record]`** and confirm deletion.
3. Verify that Patient #1 has been physically removed from the SQL Server database.
4. **The Traditional Database Restore Bottleneck**:
   * In traditional DevOps environments, recovering from accidental record deletion, broken migrations, or corrupted test runs requires requesting a full physical database restore from DBA / IT operations.
   * This process routinely takes hours or days, leaving QA and development teams blocked.

### Step 7: Instant VDB Rewind via Delphix Data Control Tower (DCT)
1. Navigate to **Delphix DCT / Virtualization Engine**.
2. Select the VDB (`vhms3_ar`, `vhms3_br`, or `vhms3_us`).
3. Click **Rewind** and select the snapshot taken in Step 4 (immediately after masking).
4. Within **seconds**, Delphix rolls back the database blocks to the clean masked state.
5. In the HMS 3.0 Test application (Port 8013), click **`[🔄 Refresh Data]`**:
   * Patient ID #1 is instantly restored to its exact original state.
   * No physical backup restoration, no storage waste, and zero downtime for the team.

---

## 🌐 REST API Endpoints Specification

HMS 3.0 provides a standardized, English-first RESTful API for programmatically inspecting, creating, updating, and verifying data across production and test environments:

| Method | Endpoint | Description | Request Payload |
|---|---|---|---|
| `GET` | `/api/health/` | Service health status, environment, database, masking state | None |
| `GET` | `/api/patients/` | List all patients (supports `?q=<search_term>` query) | Query params |
| `GET` | `/api/patient/<id>/` | Detailed PHI record for a specific patient | None |
| `POST` | `/api/patient/save/` | Create or update a patient record | JSON or Form Data |
| `POST` | `/api/patient/<id>/delete/` | Delete patient record (simulates UAT data corruption) | None / Form CSRF |
| `GET` | `/api/doctors/` | List all medical doctors and their specialties | None |

### API Usage Examples

#### 1. System Health Check
```bash
curl -s http://localhost:8012/api/health/ | jq .
```
```json
{
  "status": "UP",
  "environment": "prod",
  "country": "AR",
  "database": "hms3_ar",
  "masked": false
}
```

#### 2. Query Patient PHI Record
```bash
curl -s http://localhost:8012/api/patient/1/ | jq .
```
```json
{
  "id": 1,
  "first_name": "Martin",
  "last_name": "Aguirre",
  "doc_primary": "43456607",
  "doc_secondary": "20-43456607-0",
  "phone": "+54 9 11 2798-6423",
  "email": "martin.aguirre55@gmail.com",
  "address": "Av. Rivadavia 299",
  "city": "Córdoba Capital",
  "state": "Córdoba",
  "postal_code": "X5000",
  "insurance_provider": "Medifé",
  "insurance_number": "87720024/4",
  "diagnosis": "Síndrome metabólico y dislipidemia",
  "doctor": "Dr/a. Camila Ruiz (Clínica Médica) - MN: 141453"
}
```

#### 3. Create or Update Patient (JSON)
```bash
curl -s -X POST http://localhost:8012/api/patient/save/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Mariana",
    "last_name": "Vidal",
    "doc_primary": "33889911",
    "doc_secondary": "27-33889911-4",
    "phone": "+54 9 11 4455-8899",
    "email": "m.vidal@hospital.com.ar",
    "address": "Av. Callao 1540",
    "city": "CABA",
    "state": "Buenos Aires",
    "insurance": "OSDE",
    "diagnosis": "Routine consultation"
  }' | jq .
```

#### 4. Delete Patient (UAT Failure Simulation)
```bash
curl -s -X POST http://localhost:8013/api/patient/1/delete/ | jq .
```

---

## 📂 Project Directory Structure

```
hms3/
├── application/
│   ├── manage.py
│   ├── hms_project/
│   │   ├── __init__.py
│   │   ├── settings.py          # Cookie isolation, MSSQL engine config
│   │   ├── middleware.py        # NoCacheMiddleware & Demo Context Processor
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── core/
│   │   ├── admin.py             # Multi-country dynamic Django Admin
│   │   ├── i18n.py              # Localization dictionary (AR, BR, US)
│   │   ├── models.py            # Dynamic model selector based on HMS_COUNTRY
│   │   ├── models_ar.py         # Argentine schema (PACIENTES, MEDICOS, DNI, CUIL)
│   │   ├── models_br.py         # Brazilian schema (PACIENTES, MEDICOS, CPF, RG, CRM)
│   │   ├── models_us.py         # US schema (PATIENTS, DOCTORS, SSN, NPI, ZIP)
│   │   ├── views.py             # Multi-country dashboard, detail API, save/delete
│   │   └── management/
│   │       └── commands/
│   │           ├── seed_argentina.py  # DNI + Modulo 11 CUIL generator
│   │           ├── seed_brazil.py     # CPF + Modulo 11 + CRM generator
│   │           └── seed_usa.py        # SSN + Modulo 10 Luhn NPI generator
│   ├── templates/
│   │   ├── base.html            # Dynamic banners, environment clocks, anti-cache
│   │   └── dashboard.html       # KPI cards, patient roster, physicians, modals
│   └── requirements.txt         # Django, mssql-django, pyodbc, gunicorn, whitenoise
├── docker-compose-app.yml       # Podman Compose service definition
├── Dockerfile.django            # Multi-stage build with Microsoft ODBC Driver 18
├── launch_hms.sh                # Unified multi-country deployment script
├── .env.example                 # Master environment configuration template
├── .env-prod-ar.example         # Production Argentina configuration template
├── .env-test-ar.example         # Test VDB Argentina configuration template
├── .env-prod-br.example         # Production Brazil configuration template
├── .env-test-br.example         # Test VDB Brazil configuration template
├── .env-prod-us.example         # Production USA configuration template
├── .env-test-us.example         # Test VDB USA configuration template
└── README.md                    # Comprehensive documentation
```

---

## 🔒 Security & Privacy Notice
All patient and physician data generated by `seed_argentina`, `seed_brazil`, and `seed_usa` is **100% synthetically generated** using algorithmic pseudo-random permutations. Any resemblance to real persons, living or deceased, or actual medical records is purely coincidental.

---
*Developed for Delphix Continuous Compliance & Data Virtualization Demonstration Environments.*
