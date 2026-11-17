"""
Base común de los seeders (seed_argentina, seed_brazil, seed_usa).

Los seeders son los dueños del schema: crean la base y las tablas con su propio
DDL (Django no las gestiona: managed = False, sin migrations). Las tablas no
tienen FOREIGN KEY a propósito, para que el masking on-the-fly de Delphix pueda
hacer TRUNCATE.

Reglas de seguridad, pensadas para no perder datos antes de una demo:
  * Cada seeder solo corre si HMS_COUNTRY coincide con su país.
  * Sin --clean nunca borra nada: si las tablas ya tienen datos o un schema
    distinto, aborta y explica cómo seguir.
  * Con --clean borra y recrea únicamente las tablas de su país.
"""
import random
import unicodedata

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction


def email_slug(text):
    """'Joaquín González' -> 'joaquingonzalez' (sin acentos ni espacios, para emails)."""
    ascii_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return ''.join(ch for ch in ascii_text.lower() if ch.isalnum())


class BaseSeedCommand(BaseCommand):
    # Cada seeder define:
    country = None      # 'AR', 'BR' o 'US'
    ddl = ''            # CREATE TABLE de las tres tablas (T-SQL), de padres a hijas

    def get_models(self):
        """Devuelve (Especialidad, Medico, Paciente) del país, de padres a hijas."""
        raise NotImplementedError

    def populate(self, cant_medicos, cant_pacientes):
        """Inserta los datos sintéticos. Devuelve el mensaje final de éxito."""
        raise NotImplementedError

    # ------------------------------------------------------------------ CLI
    def add_arguments(self, parser):
        parser.add_argument('--pacientes', type=int, default=40,
                            help='Number of patients to generate (default: 40)')
        parser.add_argument('--medicos', type=int, default=10,
                            help='Number of doctors to generate (default: 10)')
        parser.add_argument('--clean', action='store_true',
                            help='Drop and recreate the tables of this country before seeding. '
                                 'Without it, the command never deletes data: it aborts if the '
                                 'tables already contain rows.')
        parser.add_argument('--seed', type=int, default=None,
                            help='Random seed: the same number always generates the same people '
                                 '(useful for a scripted demo).')

    def handle(self, *args, **options):
        if settings.HMS_COUNTRY != self.country:
            raise CommandError(
                f"This seeder is for HMS_COUNTRY={self.country}, but this environment is configured "
                f"as HMS_COUNTRY={settings.HMS_COUNTRY} (database '{settings.DB_NAME}'). "
                f"Nothing was changed."
            )
        if options['medicos'] < 1 or options['pacientes'] < 0:
            raise CommandError("--medicos must be at least 1 and --pacientes cannot be negative.")

        if options['seed'] is not None:
            random.seed(options['seed'])

        self.stdout.write(f"-> Target: database '{settings.DB_NAME}' @ {settings.DB_HOST} "
                          f"(country {self.country}, environment {settings.HMS_ENV})")

        if connection.vendor == 'microsoft':
            self.ensure_database()
            self.prepare_tables_mssql(options['clean'])
        else:
            # SQLite (smoke tests): las tablas ya existen; solo se controlan los datos.
            self.prepare_tables_generic(options['clean'])

        with transaction.atomic():
            message = self.populate(options['medicos'], options['pacientes'])
        self.stdout.write(self.style.SUCCESS(message))

    # ------------------------------------------------------- helpers de datos
    def unique(self, generator, used, attempts=1000):
        """Llama a generator() hasta obtener un valor que no esté en used."""
        for _ in range(attempts):
            value = generator()
            if value not in used:
                used.add(value)
                return value
        raise CommandError("Could not generate a unique synthetic value; try smaller --medicos/--pacientes.")

    def pick_person(self, male_names, female_names, last_names, used):
        """Elige (genero, nombre, apellido) evitando repetir la combinación si es posible."""
        genero = 'M' if random.random() > 0.5 else 'F'
        for _ in range(50):
            nombre = random.choice(male_names if genero == 'M' else female_names)
            apellido = random.choice(last_names)
            if (nombre, apellido) not in used:
                break
        used.add((nombre, apellido))
        return genero, nombre, apellido

    # ------------------------------------------------------------ SQL Server
    def table_names(self):
        """Tablas del país, de hijas a padres (orden seguro para borrar)."""
        return [m._meta.db_table for m in reversed(self.get_models())]

    def ensure_database(self):
        """Crea la base de datos en SQL Server si aún no existe (Día 0)."""
        import pyodbc

        db_conf = settings.DATABASES['default']
        target_db = db_conf['NAME']
        options = db_conf.get('OPTIONS', {})
        conn_str = (
            f"DRIVER={{{options.get('driver', 'ODBC Driver 18 for SQL Server')}}};"
            f"SERVER={db_conf['HOST']},{db_conf.get('PORT', '1433')};DATABASE=master;"
            f"UID={db_conf.get('USER', 'sa')};PWD={db_conf.get('PASSWORD', '')};"
            f"{options.get('extra_params', 'TrustServerCertificate=yes;')}"
        )
        try:
            conn = pyodbc.connect(conn_str, autocommit=True, timeout=10)
        except Exception as exc:
            raise CommandError(f"Cannot connect to SQL Server {db_conf['HOST']}:{db_conf.get('PORT', '1433')}: {exc}")
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT database_id FROM sys.databases WHERE name = ?", (target_db,))
            if cursor.fetchone():
                self.stdout.write(f"-> Database '{target_db}' found.")
            else:
                self.stdout.write(self.style.WARNING(f"-> Database '{target_db}' does not exist. Creating it..."))
                cursor.execute(f"CREATE DATABASE [{target_db.replace(']', ']]')}];")
                self.stdout.write(self.style.SUCCESS(f"-> Database '{target_db}' created."))
        except Exception as exc:
            raise CommandError(f"Error checking/creating database '{target_db}': {exc}")
        finally:
            conn.close()
        # Descarta cualquier conexión previa de Django para que tome la base recién creada.
        connection.close()

    def prepare_tables_mssql(self, clean):
        models = self.get_models()
        tables = self.table_names()
        with connection.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(tables))
            cursor.execute(
                f"SELECT name FROM sys.tables WHERE schema_id = SCHEMA_ID('dbo') AND name IN ({placeholders})",
                tables,
            )
            existing = {row[0].upper() for row in cursor.fetchall()}

            if clean:
                self.stdout.write(self.style.WARNING(
                    f"-> --clean: dropping and recreating {', '.join(tables)} (IDs restart at 1)..."))
                for table in tables:
                    cursor.execute(f"IF OBJECT_ID('dbo.{table}', 'U') IS NOT NULL DROP TABLE dbo.{table};")
                cursor.execute(self.ddl)
                return

            if not existing:
                self.stdout.write(f"-> Creating tables {', '.join(reversed(tables))}...")
                cursor.execute(self.ddl)
                return

            # Hay tablas previas: sin --clean no se toca nada que tenga datos o no coincida.
            problems = []
            for model in models:
                table = model._meta.db_table
                if table.upper() not in existing:
                    problems.append(f"table {table} is missing")
                    continue
                cursor.execute(
                    "SELECT UPPER(name) FROM sys.columns WHERE object_id = OBJECT_ID(%s)",
                    [f'dbo.{table}'],
                )
                actual = {row[0] for row in cursor.fetchall()}
                expected = {f.column.upper() for f in model._meta.concrete_fields}
                missing = sorted(expected - actual)
                if missing:
                    problems.append(f"table {table} lacks columns {', '.join(missing)}")
            if problems:
                raise CommandError(
                    f"Database '{settings.DB_NAME}' has tables that do not match the {self.country} schema "
                    f"({'; '.join(problems)}). Nothing was changed. "
                    f"Re-run with --clean to drop and recreate them."
                )

            self.abort_if_data(models)

            # Tablas vacías: se reinician los IDENTITY para que los IDs arranquen en 1.
            for table in tables:
                cursor.execute(
                    f"IF (SELECT last_value FROM sys.identity_columns WHERE object_id = OBJECT_ID('dbo.{table}')) "
                    f"IS NOT NULL DBCC CHECKIDENT ('dbo.{table}', RESEED, 0);"
                )

    # ------------------------------------------------------ SQLite (tests)
    def prepare_tables_generic(self, clean):
        models = self.get_models()
        if clean:
            for model in reversed(models):
                model.objects.all().delete()
            return
        self.abort_if_data(models)

    def abort_if_data(self, models):
        counts = {m._meta.db_table: m.objects.count() for m in models}
        if any(counts.values()):
            detail = ', '.join(f"{table}={n}" for table, n in counts.items())
            raise CommandError(
                f"Database '{settings.DB_NAME}' already has data ({detail}). Nothing was changed. "
                f"Re-run with --clean to delete it and generate new data."
            )
