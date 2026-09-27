"""
Common synthetic identifier generators and collision-avoidance logic for HMS 3.0.

Provides shared, mathematically consistent algorithms for:
- Argentina: DNI (8 digits) and CUIL (Modulo 11 with prefixes 20/27/23).
- Brazil: RG (Registro Geral) and CPF (Modulo 11 check digits).
- USA: State ID and SSN (structural area/group/serial exclusions).

These generators are used consistently across seed commands and manual patient creation.
"""

import random
from typing import Optional, Tuple


# --- Argentina Algorithms ---

def generate_ar_dni() -> str:
    """Generates an 8-digit realistic Argentine DNI."""
    return str(random.randint(30000000, 48999999))


def generate_ar_cuil(dni: Optional[str] = None, genero: Optional[str] = None) -> str:
    """
    Calculates an Argentine CUIL (Modulo 11 check digit) compliant with Delphix ar-mask rules.
    """
    if not dni:
        dni = generate_ar_dni()
    if not genero:
        genero = random.choice(('M', 'F'))

    prefix = 27 if genero == 'F' else 20
    dni_int = int(dni)
    weights = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

    def _eval(p, d):
        digits = [int(x) for x in f"{p:02d}{d:08d}"]
        s = sum(w * d for w, d in zip(weights, digits))
        return s % 11

    residue = _eval(prefix, dni_int)
    if residue == 0:
        dv = 0
    elif residue == 1:
        prefix = 23
        residue2 = _eval(prefix, dni_int)
        dv = 0 if residue2 == 0 else (11 - residue2)
    else:
        dv = 11 - residue

    return f"{prefix}-{dni}-{dv}"


# --- Brazil Algorithms ---

def generate_br_rg(estado: Optional[str] = None) -> str:
    """Generates a realistic Brazilian RG (Registro Geral)."""
    if not estado:
        estado = random.choice(["SP", "RJ", "MG", "PR", "RS", "BA", "SC", "PE", "CE", "DF"])
    p1 = random.randint(10, 60)
    p2 = random.randint(100, 999)
    p3 = random.randint(100, 999)
    dv = random.choice([str(random.randint(0, 9)), "X"])
    return f"{estado}-{p1}.{p2}.{p3}-{dv}"


def generate_br_cpf() -> str:
    """
    Generates a synthetic Brazilian CPF with both check digits calculated via Modulo 11
    for LGPD demonstration rule sets.
    """
    nove_digitos = [random.randint(0, 9) for _ in range(9)]

    # 1st Check Digit
    soma1 = sum(d * (10 - i) for i, d in enumerate(nove_digitos))
    resto1 = soma1 % 11
    d1 = 0 if resto1 < 2 else (11 - resto1)

    # 2nd Check Digit
    dez_digitos = nove_digitos + [d1]
    soma2 = sum(d * (11 - i) for i, d in enumerate(dez_digitos))
    resto2 = soma2 % 11
    d2 = 0 if resto2 < 2 else (11 - resto2)

    digs = "".join(str(d) for d in nove_digitos)
    return f"{digs[:3]}.{digs[3:6]}.{digs[6:9]}-{d1}{d2}"


# --- USA Algorithms ---

def generate_us_state_id(state: Optional[str] = None) -> str:
    """Generates a realistic US State Driver License / State ID."""
    if not state:
        state = random.choice(['NY', 'CA', 'IL', 'TX', 'GA', 'MA', 'FL', 'WA'])
    return f"{state}-DL{random.randint(10000000, 99999999)}"


def generate_us_ssn() -> str:
    """
    Generates a synthetic SSN adhering to standard structural exclusion rules:
    - Area (AAA): not 000, not 666, not 900-999
    - Group (GG): not 00
    - Serial (SSSS): not 0000
    """
    valid_areas = [a for a in range(1, 900) if a != 666]
    area = random.choice(valid_areas)
    group = random.randint(1, 99)
    serial = random.randint(1, 9999)
    return f"{area:03d}-{group:02d}-{serial:04d}"


def generate_us_npi() -> str:
    """
    Generates a synthetic 10-digit National Provider Identifier (NPI) format with
    Luhn algorithm (Modulo 10) check digit, prefixed by 80840.
    """
    base_9 = "1" + "".join(str(random.randint(0, 9)) for _ in range(8))
    full_prefix = "80840" + base_9
    digits = [int(c) for c in full_prefix]

    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 0:
            doubled = d * 2
            total += (doubled - 9) if doubled > 9 else doubled
        else:
            total += d
    check_digit = (10 - (total % 10)) % 10
    return base_9 + str(check_digit)


# --- Collision-Resistant Unique Identifiers for Views ---

def generate_unique_identifier(
    generator_func,
    paciente_model,
    field_name: str,
    max_retries: int = 20,
    exclude_id: Optional[int] = None,
    *args,
    **kwargs
) -> str:
    """
    Generates candidate identifier and checks database for collisions.
    Retries up to `max_retries` before raising RuntimeError.
    """
    for _ in range(max_retries):
        candidate = generator_func(*args, **kwargs)
        lookup = {field_name: candidate}
        qs = paciente_model.objects.filter(**lookup)
        if exclude_id is not None:
            qs = qs.exclude(pk=exclude_id)
        if not qs.exists():
            return candidate

    raise RuntimeError(
        f"Could not generate unique synthetic identifier for field '{field_name}' after {max_retries} attempts."
    )


def generate_unique_patient_identifiers(
    country: str,
    paciente_model,
    doc_primary: Optional[str] = None,
    doc_secondary: Optional[str] = None,
    exclude_id: Optional[int] = None,
    max_retries: int = 20
) -> Tuple[str, str]:
    """
    Generates unique primary and secondary documents for a patient record
    according to regional country model, avoiding collisions in the database.

    AR:
      doc_primary   -> DNI  (field: dni)
      doc_secondary -> CUIL (field: cuil)
    BR:
      doc_primary   -> RG   (field: rg)
      doc_secondary -> CPF  (field: cpf)
    US:
      doc_primary   -> STATE_ID (field: state_id)
      doc_secondary -> SSN      (field: ssn)
    """
    country = (country or 'AR').upper()

    if country == 'BR':
        if not doc_primary:
            doc_primary = generate_unique_identifier(
                generate_br_rg, paciente_model, 'rg', max_retries, exclude_id
            )
        if not doc_secondary:
            doc_secondary = generate_unique_identifier(
                generate_br_cpf, paciente_model, 'cpf', max_retries, exclude_id
            )
    elif country == 'US':
        if not doc_primary:
            doc_primary = generate_unique_identifier(
                generate_us_state_id, paciente_model, 'state_id', max_retries, exclude_id
            )
        if not doc_secondary:
            doc_secondary = generate_unique_identifier(
                generate_us_ssn, paciente_model, 'ssn', max_retries, exclude_id
            )
    else:  # AR
        if not doc_primary:
            doc_primary = generate_unique_identifier(
                generate_ar_dni, paciente_model, 'dni', max_retries, exclude_id
            )
        if not doc_secondary:
            for _ in range(max_retries):
                candidate_cuil = generate_ar_cuil(dni=doc_primary)
                qs = paciente_model.objects.filter(cuil=candidate_cuil)
                if exclude_id is not None:
                    qs = qs.exclude(pk=exclude_id)
                if not qs.exists():
                    doc_secondary = candidate_cuil
                    break
            else:
                raise RuntimeError(
                    f"Could not generate unique synthetic CUIL after {max_retries} attempts."
                )

    return doc_primary, doc_secondary
