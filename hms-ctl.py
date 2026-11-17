#!/usr/bin/env python3
"""
HMS 3.0 Container Lifecycle & Orchestration Controller (hms-ctl.py)
Multi-Country: Argentina (AR), Brazil (BR), USA (US)
Supports both Podman and Docker engines automatically with zero host dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Base Directory & Defaults
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_IMAGE = os.getenv("HMS_IMAGE", "hms3-app:1.0")

COUNTRIES_META = {
    "ar": {
        "label": "Argentina (Ley 25.326)",
        "code": "AR",
        "compliance": "Ley 25.326 (Protección de Datos Personales)",
    },
    "br": {
        "label": "Brazil (LGPD)",
        "code": "BR",
        "compliance": "LGPD (Lei Geral de Proteção de Dados)",
    },
    "us": {
        "label": "United States (HIPAA)",
        "code": "US",
        "compliance": "HIPAA Protected Health Information (PHI)",
    },
}

ENVIRONMENTS_META = {
    "prod": {
        "name": "hms3_prod",
        "port": 8012,
        "label": "PRODUCTION",
    },
    "test": {
        "name": "hms3_test",
        "port": 8013,
        "label": "NON-PRODUCTION / NO PRODUCCIÓN",
    },
}


# Terminal Styling
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    @classmethod
    def enabled(cls) -> bool:
        return sys.stdout.isatty() and os.getenv("NO_COLOR") is None

    @classmethod
    def color(cls, text: str, col: str) -> str:
        if cls.enabled():
            return f"{col}{text}{cls.RESET}"
        return text


def print_ok(msg: str):
    print(f"{Colors.color('✔', Colors.GREEN)} {msg}")


def print_info(msg: str):
    print(f"{Colors.color('ℹ', Colors.CYAN)} {msg}")


def print_warn(msg: str):
    print(f"{Colors.color('⚠', Colors.YELLOW)} {msg}")


def print_error(msg: str):
    print(f"{Colors.color('✖', Colors.RED)} {Colors.color(msg, Colors.BOLD)}", file=sys.stderr)


# Host IP Detection
def get_host_ip() -> str:
    try:
        res = subprocess.run(["hostname", "-I"], capture_output=True, text=True, check=True)
        ips = res.stdout.strip().split()
        if ips:
            return ips[0]
    except Exception:
        pass
    return "127.0.0.1"


# Engine Detection & Command Prefix
def detect_engine(preferred: str = "auto") -> Tuple[str, List[str], str]:
    """
    Detects whether Podman or Docker should be used.
    Returns: (engine_name, command_prefix, version_string)
    """
    pref = preferred.lower() if preferred else "auto"

    chosen_engine = None
    if pref in ("podman", "docker"):
        if not shutil.which(pref):
            raise SystemExit(f"Error: Selected engine '{pref}' is not installed or not in PATH.")
        chosen_engine = pref
    else:
        # Check environment variable
        env_pref = os.getenv("CONTAINER_ENGINE", "").lower()
        if env_pref in ("podman", "docker") and shutil.which(env_pref):
            chosen_engine = env_pref
        else:
            podman_path = shutil.which("podman")
            docker_path = shutil.which("docker")

            if podman_path and docker_path:
                # Test if docker is actually a podman-docker wrapper
                try:
                    chk = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=2)
                    out = (chk.stdout + chk.stderr).lower()
                    if "podman" in out or "emulate" in out:
                        chosen_engine = "podman"
                    else:
                        chosen_engine = "docker"
                except Exception:
                    chosen_engine = "podman"
            elif podman_path:
                chosen_engine = "podman"
            elif docker_path:
                chosen_engine = "docker"
            else:
                raise SystemExit("Error: Neither 'podman' nor 'docker' was found in system PATH.")

    # Determine command prefix (sudo vs direct)
    cmd_prefix = [chosen_engine]
    if os.geteuid() != 0:
        if chosen_engine == "docker":
            # Test if docker works without sudo
            try:
                test_run = subprocess.run(["docker", "ps"], capture_output=True, timeout=2)
                if test_run.returncode != 0 and shutil.which("sudo"):
                    cmd_prefix = ["sudo", "docker"]
            except Exception:
                if shutil.which("sudo"):
                    cmd_prefix = ["sudo", "docker"]
        else:
            # Podman: Check if rootless is explicitly desired via HMS_ROOTLESS=1
            if os.getenv("HMS_ROOTLESS") == "1":
                cmd_prefix = ["podman"]
            elif shutil.which("sudo"):
                cmd_prefix = ["sudo", "podman"]

    # Ask for the sudo password once, up front and without a time limit. Otherwise the
    # prompt appears inside the checks below, which run with captured output and short
    # timeouts: it gets cut off while typing and shows up again mixed with the output.
    if cmd_prefix[0] == "sudo":
        try:
            validated = subprocess.run(["sudo", "-v"]).returncode == 0
        except KeyboardInterrupt:
            validated = False
        if not validated:
            raise SystemExit("Error: sudo authentication failed or was cancelled. "
                             "Nothing was done. (Use HMS_ROOTLESS=1 to run podman without sudo.)")

    # Retrieve engine version
    ver_str = "unknown"
    try:
        ver_run = subprocess.run(cmd_prefix + ["--version"], capture_output=True, text=True, timeout=3)
        if ver_run.returncode == 0:
            lines = [line.strip() for line in ver_run.stdout.splitlines() if line.strip() and not line.startswith("Emulate")]
            if lines:
                ver_str = lines[0]
    except Exception:
        pass

    return chosen_engine, cmd_prefix, ver_str


# Container Inspection Helpers
def container_exists(cmd_prefix: List[str], container_name: str) -> bool:
    try:
        res = subprocess.run(
            cmd_prefix + ["ps", "-a", "-q", "-f", f"name=^{container_name}$"],
            capture_output=True,
            text=True,
            check=True,
        )
        return bool(res.stdout.strip())
    except Exception:
        return False


def container_is_running(cmd_prefix: List[str], container_name: str) -> bool:
    if not container_exists(cmd_prefix, container_name):
        return False
    try:
        res = subprocess.run(
            cmd_prefix + ["inspect", "--format", "{{.State.Running}}", container_name],
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip().lower() == "true"
    except Exception:
        return False


def get_container_env_vars(cmd_prefix: List[str], container_name: str) -> Dict[str, str]:
    env_map = {}
    if not container_exists(cmd_prefix, container_name):
        return env_map
    try:
        res = subprocess.run(
            cmd_prefix + ["inspect", "--format", "{{range .Config.Env}}{{println .}}{{end}}", container_name],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in res.stdout.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                env_map[k] = v
    except Exception:
        pass
    return env_map


def get_container_country(cmd_prefix: List[str], container_name: str) -> Optional[str]:
    env_vars = get_container_env_vars(cmd_prefix, container_name)
    val = env_vars.get("HMS_COUNTRY")
    if val:
        return val.strip().lower()
    return None


def git_build_id() -> str:
    """Short commit of the repo, with '-dirty' if there are uncommitted changes."""
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(BASE_DIR), capture_output=True, text=True, check=True, timeout=5,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=str(BASE_DIR), capture_output=True, text=True, check=True, timeout=5,
        ).stdout.strip()
        return f"{sha}-dirty" if dirty else sha
    except Exception:
        return "unknown"


def build_image(cmd_prefix: List[str], tag: str, no_cache: bool = False) -> int:
    """Builds the image and stamps it with the repo commit (HMS_BUILD)."""
    build_id = git_build_id()
    print_info(f"Building container image '{tag}' (build {build_id})...")
    build_cmd = cmd_prefix + ["build", "-t", tag, "-f", "Dockerfile.django", "--build-arg", f"HMS_BUILD={build_id}"]
    if no_cache:
        build_cmd.append("--no-cache")
    build_cmd.append(".")
    res = subprocess.run(build_cmd, cwd=str(BASE_DIR))
    if res.returncode != 0:
        print_error("Failed to build container image.")
    else:
        print_ok(f"Image '{tag}' built successfully (build {build_id}).")
    return res.returncode


def fetch_health(port: str, timeout: float = 3.0) -> Optional[Dict[str, object]]:
    """
    Calls /api/health/ of the app published on the given host port.
    Returns the JSON (status UP or DOWN) or None if the app does not answer.
    """
    url = f"http://127.0.0.1:{port}/api/health/"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        # 503 = app is up but the database is not available
        try:
            return json.loads(err.read().decode("utf-8"))
        except Exception:
            return None
    except Exception:
        return None


def integrity_warning(health: Dict[str, object]) -> Optional[str]:
    """Message describing broken references between tables, or None if there are none."""
    if health.get("integrity") != "BROKEN":
        return None
    return (f"Broken references in '{health.get('database')}': "
            f"{health.get('doctors_without_specialty', 0)} doctors point to a missing specialty, "
            f"{health.get('patients_with_missing_doctor', 0)} patients point to a missing doctor. "
            f"The tables have no foreign keys, so check the masking ruleset: it must include the three tables "
            f"and must not mask the ID / relationship columns.")


def wait_for_health(port: str, seconds: int = 30) -> Optional[Dict[str, object]]:
    """Polls the health endpoint until the app answers (UP or DOWN) or the time runs out."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        health = fetch_health(port)
        if health is not None:
            return health
        time.sleep(1)
    return None


def report_health(container_name: str, port: str, access_url: str) -> int:
    """Verifies the app really works and prints the outcome. Returns the exit code."""
    print_info("Waiting for the application to answer its health check...")
    health = wait_for_health(port)
    if health is None:
        print_error(f"Container '{container_name}' started but the application does not answer on port {port}.")
        print_info("Check the logs with: ./hms-ctl.py logs -e <env> -c <country>")
        return 1
    if health.get("status") != "UP":
        print_warn(f"Application is running at {access_url} but the DATABASE IS NOT AVAILABLE "
                   f"({health.get('database', '-')}).")
        print_info("The app shows a 'database not available' page and recovers by itself when the database is back.")
        print_info("If the database is empty, load data with the seed command for this country.")
        return 0
    print_ok(f"Health check OK: database '{health.get('database')}' with {health.get('patients')} patients, "
             f"{health.get('doctors')} doctors, {health.get('specialties')} specialties (build {health.get('build')}).")
    warning = integrity_warning(health)
    if warning:
        print_warn(warning)
    return 0


def parse_env_file(filepath: Path) -> Dict[str, str]:
    data = {}
    if not filepath.is_file():
        return data
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip().strip("'\"")
    return data


# Commands Implementation
def cmd_start(args: argparse.Namespace) -> int:
    env_name = args.env.lower()
    country = args.country.lower()

    if env_name not in ENVIRONMENTS_META:
        print_error(f"Invalid environment '{args.env}'. Choose from 'prod' or 'test'.")
        return 1
    if country not in COUNTRIES_META:
        print_error(f"Invalid country '{args.country}'. Choose from 'ar', 'br', or 'us'.")
        return 1

    engine, cmd_prefix, ver_str = detect_engine(args.engine)
    env_meta = ENVIRONMENTS_META[env_name]
    country_meta = COUNTRIES_META[country]

    source_env_file = BASE_DIR / f".env-{env_name}-{country}"
    if not source_env_file.is_file():
        print_error(f"Configuration file '{source_env_file.name}' does not exist.")
        example_file = BASE_DIR / f".env-{env_name}-{country}.example"
        if example_file.is_file():
            print_info(f"Tip: Copy '{example_file.name}' to '{source_env_file.name}' and configure database credentials:")
            print_info(f"     cp {example_file.name} {source_env_file.name}")
        return 1

    parsed_vars = parse_env_file(source_env_file)
    container_name = parsed_vars.get("HMS_CONTAINER_NAME", env_meta["name"])
    host_port = parsed_vars.get("HOST_PORT", str(env_meta["port"]))
    db_name = parsed_vars.get("DB_NAME", "-")
    db_host = parsed_vars.get("DB_HOST", "-")

    print(Colors.color("═" * 60, Colors.CYAN))
    print(f" {Colors.color('HMS 3.0 DEPLOYMENT', Colors.BOLD)} • {Colors.color(env_meta['label'], Colors.YELLOW)}")
    print(Colors.color("─" * 60, Colors.CYAN))
    print(f" Container Engine : {Colors.color(ver_str, Colors.GREEN)}")
    print(f" Jurisdiction     : {Colors.color(country_meta['label'], Colors.WHITE)}")
    print(f" Container Name   : {Colors.color(container_name, Colors.BOLD)}")
    print(f" Configuration    : {Colors.color(source_env_file.name, Colors.DIM)}")
    print(f" Target Database  : {Colors.color(f'{db_name} @ {db_host}', Colors.DIM)}")
    print(Colors.color("═" * 60, Colors.CYAN))

    # Optional Rebuild
    if getattr(args, "build", False):
        rc = build_image(cmd_prefix, DEFAULT_IMAGE)
        if rc != 0:
            return rc

    # Check if container already exists
    if container_exists(cmd_prefix, container_name):
        existing_vars = get_container_env_vars(cmd_prefix, container_name)
        existing_country = existing_vars.get("HMS_COUNTRY", "").strip().lower()
        existing_env = existing_vars.get("HMS_ENV", env_name).strip().lower()

        act_code = COUNTRIES_META.get(existing_country, {}).get("code", existing_country.upper()) if existing_country else "UNKNOWN"
        req_code = country_meta["code"]

        if existing_country != country or existing_env != env_name:
            print_error(f"Container '{container_name}' already exists with a different configuration:")
            print(f"   Existing   : Environment '{existing_env.upper()}', Country '{act_code}'")
            print(f"   Requested  : Environment '{env_name.upper()}', Country '{req_code}'")
            print_info(f"To replace it, first remove it: './hms-ctl.py rm -e {existing_env} -c {existing_country} -f' or use 'restart'.")
            return 1

        # Same environment and country
        if container_is_running(cmd_prefix, container_name):
            host_ip = get_host_ip()
            print_warn(f"Container '{container_name}' ({req_code}) is already running at http://{host_ip}:{host_port}/")
            print_info(f"Use './hms-ctl.py restart -e {env_name} -c {country}' if you wish to recreate or restart it.")
            return 0
        else:
            print_info(f"Container '{container_name}' ({req_code}) exists but is stopped. Starting it...")
            res = subprocess.run(cmd_prefix + ["start", container_name], capture_output=True, text=True)
            if res.returncode == 0:
                print_ok(f"Container '{container_name}' ({req_code}) started.")
                return report_health(container_name, host_port, f"http://{get_host_ip()}:{host_port}/")
            else:
                print_error(f"Failed to start container:\n{res.stderr.strip()}")
                return res.returncode

    # Launch container
    print_info(f"Starting container '{container_name}' on port {host_port}...")
    run_cmd = cmd_prefix + [
        "run",
        "-d",
        "--name",
        container_name,
        "--restart",
        "always",
        "-p",
        f"{host_port}:8000",
        "--env-file",
        str(source_env_file),
        DEFAULT_IMAGE,
    ]

    res = subprocess.run(run_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print_error(f"Failed to start container:\n{res.stderr.strip()}")
        return res.returncode

    host_ip = get_host_ip()
    access_url = f"http://{host_ip}:{host_port}/"

    # The container being up is not enough: confirm the app answers and reads the database.
    rc = report_health(container_name, host_port, access_url)
    if rc != 0:
        return rc

    health = fetch_health(host_port) or {}
    healthy = health.get("status") == "UP"
    color = Colors.GREEN if healthy else Colors.YELLOW
    title = "SUCCESS! HMS 3.0 is live and running." if healthy else "HMS 3.0 is running, but the DATABASE IS NOT AVAILABLE."

    print("")
    print(Colors.color("═" * 60, color))
    print(f" {Colors.color(title, Colors.BOLD)}")
    print(Colors.color("─" * 60, color))
    print(f" Environment : {Colors.color(env_meta['label'], Colors.WHITE)}")
    print(f" Country     : {Colors.color(country_meta['label'], Colors.WHITE)}")
    print(f" Container   : {Colors.color(container_name, Colors.BOLD)}")
    print(f" URL         : {Colors.color(access_url, Colors.CYAN)}")
    print(Colors.color("═" * 60, color))
    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    env_name = args.env.lower()
    country = args.country.lower()
    if env_name not in ENVIRONMENTS_META:
        print_error(f"Invalid environment '{args.env}'. Choose from 'prod' or 'test'.")
        return 1
    if country not in COUNTRIES_META:
        print_error(f"Invalid country '{args.country}'. Choose from 'ar', 'br', or 'us'.")
        return 1

    engine, cmd_prefix, ver_str = detect_engine(args.engine)
    container_name = ENVIRONMENTS_META[env_name]["name"]
    timeout = str(args.time) if hasattr(args, "time") and args.time is not None else "2"
    req_code = COUNTRIES_META[country]["code"]

    if not container_exists(cmd_prefix, container_name):
        print_info(f"Container '{container_name}' ({req_code}) does not exist. Nothing to stop.")
        return 0

    active_country = get_container_country(cmd_prefix, container_name)
    act_code = COUNTRIES_META.get(active_country, {}).get("code", active_country.upper()) if active_country else "UNKNOWN"

    if active_country and country != active_country:
        print_info(f"Container '{container_name}' ({req_code}) is not running (current container is {act_code}). Nothing to stop.")
        return 0

    if not container_is_running(cmd_prefix, container_name):
        print_info(f"Container '{container_name}' ({act_code}) is already stopped.")
        return 0

    print_info(f"Stopping container '{container_name}' ({act_code}) using {engine} (timeout: {timeout}s)...")
    res = subprocess.run(cmd_prefix + ["stop", "-t", timeout, container_name], capture_output=True, text=True)
    if res.returncode == 0:
        print_ok(f"Container '{container_name}' ({act_code}) stopped cleanly.")
        return 0
    else:
        print_error(f"Error stopping container:\n{res.stderr.strip()}")
        return res.returncode


def cmd_rm(args: argparse.Namespace) -> int:
    env_name = args.env.lower()
    country = args.country.lower()
    if env_name not in ENVIRONMENTS_META:
        print_error(f"Invalid environment '{args.env}'. Choose from 'prod' or 'test'.")
        return 1
    if country not in COUNTRIES_META:
        print_error(f"Invalid country '{args.country}'. Choose from 'ar', 'br', or 'us'.")
        return 1

    engine, cmd_prefix, ver_str = detect_engine(args.engine)
    container_name = ENVIRONMENTS_META[env_name]["name"]
    req_code = COUNTRIES_META[country]["code"]

    if not container_exists(cmd_prefix, container_name):
        print_info(f"Container '{container_name}' ({req_code}) does not exist. Nothing to remove.")
        return 0

    active_country = get_container_country(cmd_prefix, container_name)
    act_code = COUNTRIES_META.get(active_country, {}).get("code", active_country.upper()) if active_country else "UNKNOWN"

    if active_country and country != active_country:
        print_info(f"Container '{container_name}' ({req_code}) does not exist (current container is {act_code}). Nothing to remove.")
        return 0

    if container_is_running(cmd_prefix, container_name) and not getattr(args, "force", False):
        print_warn(f"Container '{container_name}' ({act_code}) is currently running. Use '-f / --force' to remove it.")
        return 1

    print_info(f"Removing container '{container_name}' ({act_code})...")
    rm_cmd = cmd_prefix + ["rm"]
    if getattr(args, "force", False):
        rm_cmd.append("-f")
    rm_cmd.append(container_name)

    res = subprocess.run(rm_cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print_ok(f"Container '{container_name}' ({act_code}) removed.")
        return 0
    else:
        print_error(f"Error removing container:\n{res.stderr.strip()}")
        return res.returncode


def cmd_restart(args: argparse.Namespace) -> int:
    engine, cmd_prefix, ver_str = detect_engine(args.engine)
    env_name = args.env.lower()
    country = args.country.lower()

    if env_name not in ENVIRONMENTS_META:
        print_error(f"Invalid environment '{args.env}'. Choose from 'prod' or 'test'.")
        return 1
    if country not in COUNTRIES_META:
        print_error(f"Invalid country '{args.country}'. Choose from 'ar', 'br', or 'us'.")
        return 1

    container_name = ENVIRONMENTS_META[env_name]["name"]
    req_code = COUNTRIES_META[country]["code"]

    if not container_exists(cmd_prefix, container_name):
        print_error(f"Container '{container_name}' ({req_code}) does not exist. Use 'start' to create it.")
        return 1

    existing_vars = get_container_env_vars(cmd_prefix, container_name)
    existing_country = existing_vars.get("HMS_COUNTRY", "").strip().lower()
    existing_env = existing_vars.get("HMS_ENV", env_name).strip().lower()
    act_code = COUNTRIES_META.get(existing_country, {}).get("code", existing_country.upper()) if existing_country else "UNKNOWN"

    if existing_country != country or existing_env != env_name:
        print_error(f"Container '{container_name}' already exists with a different configuration:")
        print(f"   Existing   : Environment '{existing_env.upper()}', Country '{act_code}'")
        print(f"   Requested  : Environment '{env_name.upper()}', Country '{req_code}'")
        print_info(f"To switch country, first remove the existing container: './hms-ctl.py rm -e {existing_env} -c {existing_country} -f' and then start the new one.")
        return 1

    # Optional Rebuild
    if getattr(args, "build", False):
        rc = build_image(cmd_prefix, DEFAULT_IMAGE)
        if rc != 0:
            return rc
        print_info(f"Recreating container '{container_name}' ({req_code}) with new image...")
        if container_is_running(cmd_prefix, container_name):
            subprocess.run(cmd_prefix + ["stop", "-t", "2", container_name], capture_output=True)
        subprocess.run(cmd_prefix + ["rm", "-f", container_name], capture_output=True)
        args.build = False
        return cmd_start(args)

    # Standard restart of the existing container
    print_info(f"Restarting container '{container_name}' ({req_code}) using {engine}...")
    res = subprocess.run(cmd_prefix + ["restart", "-t", "2", container_name], capture_output=True, text=True)
    if res.returncode == 0:
        print_ok(f"Container '{container_name}' ({req_code}) restarted successfully.")
        port = existing_vars.get("HOST_PORT", str(ENVIRONMENTS_META[env_name]["port"]))
        return report_health(container_name, port, f"http://{get_host_ip()}:{port}/")
    else:
        print_error(f"Failed to restart container:\n{res.stderr.strip()}")
        return res.returncode


def cmd_status(args: argparse.Namespace) -> int:
    engine, cmd_prefix, ver_str = detect_engine(args.engine)
    host_ip = get_host_ip()

    repo_build = git_build_id()
    stale = False
    warnings: List[str] = []

    print(Colors.color("═" * 100, Colors.CYAN))
    print(f" {Colors.color('HMS 3.0 STATUS OVERVIEW', Colors.BOLD)} • Engine: {Colors.color(ver_str, Colors.GREEN)}"
          f" • Repo build: {repo_build}")
    print(Colors.color("═" * 100, Colors.CYAN))

    header = f"{'PROJECT':<12} {'ENV':<6} {'COUNTRY':<8} {'PORT':<6} {'STATUS':<12} {'HEALTH':<16} {'BUILD':<14} {'URL':<26}"
    print(Colors.color(header, Colors.BOLD))
    print(Colors.color("─" * 100, Colors.DIM))

    for env_key, meta in ENVIRONMENTS_META.items():
        if getattr(args, "env", None) and args.env.lower() != env_key:
            continue
        c_name = meta["name"]
        default_port = meta["port"]
        exists = container_exists(cmd_prefix, c_name)
        running = container_is_running(cmd_prefix, c_name)

        if exists:
            env_vars = get_container_env_vars(cmd_prefix, c_name)
            country_code = env_vars.get("HMS_COUNTRY", "-")
            port = env_vars.get("HOST_PORT", str(default_port))
            if getattr(args, "country", None) and args.country.upper() != country_code.upper():
                continue
            build = env_vars.get("HMS_BUILD", "unknown")
            if build != repo_build:
                stale = True
                build_str = Colors.color(f"{build} *".ljust(14), Colors.YELLOW)
            else:
                build_str = Colors.color(build.ljust(14), Colors.GREEN)
            if running:
                status_str = Colors.color("RUNNING".ljust(12), Colors.GREEN)
                url_str = Colors.color(f"http://{host_ip}:{port}/", Colors.CYAN)
                # Real check: does the app answer and can it read the database?
                health = fetch_health(port, timeout=5.0)
                if health is None:
                    health_str = Colors.color("NO RESPONSE".ljust(16), Colors.RED)
                elif health.get("status") == "UP" and integrity_warning(health):
                    health_str = Colors.color("BROKEN REFS".ljust(16), Colors.YELLOW)
                    warnings.append(f"{c_name}: {integrity_warning(health)}")
                elif health.get("status") == "UP":
                    health_str = Colors.color(f"OK ({health.get('patients')} pat.)".ljust(16), Colors.GREEN)
                else:
                    health_str = Colors.color("DB DOWN".ljust(16), Colors.RED)
            else:
                status_str = Colors.color("STOPPED".ljust(12), Colors.YELLOW)
                url_str = f"http://{host_ip}:{port}/ (offline)"
                health_str = Colors.color("-".ljust(16), Colors.DIM)
        else:
            if getattr(args, "country", None):
                continue
            country_code = "-"
            port = str(default_port)
            status_str = Colors.color("NOT CREATED".ljust(12), Colors.DIM)
            health_str = Colors.color("-".ljust(16), Colors.DIM)
            build_str = Colors.color("-".ljust(14), Colors.DIM)
            url_str = "-"

        row = f"{c_name:<12} {env_key:<6} {country_code:<8} {port:<6} {status_str} {health_str} {build_str} {url_str}"
        print(row)

    print(Colors.color("═" * 100, Colors.CYAN))
    for warning in warnings:
        print_warn(warning)
    if stale:
        print_warn(f"* Container built from a different commit than the repo ({repo_build}). "
                   f"Code changes are not applied until you rebuild: './hms-ctl.py restart -e <env> -c <country> --build'.")
    return 0


def cmd_logs(args: argparse.Namespace) -> int:
    env_name = args.env.lower()
    country = args.country.lower()
    if env_name not in ENVIRONMENTS_META:
        print_error(f"Invalid environment '{args.env}'. Choose from 'prod' or 'test'.")
        return 1
    if country not in COUNTRIES_META:
        print_error(f"Invalid country '{args.country}'. Choose from 'ar', 'br', or 'us'.")
        return 1

    engine, cmd_prefix, ver_str = detect_engine(args.engine)
    container_name = ENVIRONMENTS_META[env_name]["name"]
    req_code = COUNTRIES_META[country]["code"]

    if not container_exists(cmd_prefix, container_name):
        print_error(f"Container '{container_name}' ({req_code}) does not exist.")
        return 1

    active_country = get_container_country(cmd_prefix, container_name)
    act_code = COUNTRIES_META.get(active_country, {}).get("code", active_country.upper()) if active_country else "UNKNOWN"

    if active_country and country != active_country:
        print_error(f"Container '{container_name}' is running for {act_code}, not requested {req_code}.")
        return 1

    log_cmd = cmd_prefix + ["logs"]
    if getattr(args, "follow", False):
        log_cmd.append("-f")
    if getattr(args, "tail", None):
        log_cmd.extend(["--tail", str(args.tail)])
    log_cmd.append(container_name)

    try:
        proc = subprocess.run(log_cmd)
        return proc.returncode
    except KeyboardInterrupt:
        return 0


def cmd_build(args: argparse.Namespace) -> int:
    engine, cmd_prefix, ver_str = detect_engine(args.engine)
    tag = getattr(args, "tag", DEFAULT_IMAGE) or DEFAULT_IMAGE

    return build_image(cmd_prefix, tag, no_cache=getattr(args, "no_cache", False))


# CLI Parser Construction
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hms-ctl.py",
        description="HMS 3.0 Container Orchestration & Lifecycle Manager (Podman & Docker).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./hms-ctl.py start -e prod -c ar       Start Production container for Argentina
  ./hms-ctl.py start -e test -c br       Start Test (masked) container for Brazil
  ./hms-ctl.py restart -e prod -c ar     Restart Production container cleanly
  ./hms-ctl.py stop -e prod -c ar        Stop Production container cleanly
  ./hms-ctl.py rm -e prod -c ar -f       Force remove Production container
  ./hms-ctl.py status                    Display live status of all environments
  ./hms-ctl.py logs -e prod -c ar -f     Follow live logs for Production Argentina
  ./hms-ctl.py build                     Rebuild the HMS container image
""",
    )

    subparsers = parser.add_subparsers(dest="command", title="Commands", metavar="<command>")

    # Helper function to add common arguments
    def add_common(sub):
        sub.add_argument(
            "--engine",
            choices=["podman", "docker", "auto"],
            default="auto",
            help="Force specific container engine (default: auto)",
        )

    # Command: start
    p_start = subparsers.add_parser("start", help="Start an HMS container environment")
    p_start.add_argument("-e", "--env", required=True, choices=["prod", "test"], help="Environment: 'prod' or 'test'")
    p_start.add_argument("-c", "--country", required=True, choices=["ar", "br", "us"], help="Country: 'ar', 'br', or 'us'")
    p_start.add_argument("-b", "--build", action="store_true", help="Rebuild container image before starting")
    add_common(p_start)

    # Command: stop
    p_stop = subparsers.add_parser("stop", help="Stop an HMS container environment cleanly")
    p_stop.add_argument("-e", "--env", required=True, choices=["prod", "test"], help="Environment: 'prod' or 'test'")
    p_stop.add_argument("-c", "--country", required=True, choices=["ar", "br", "us"], help="Country: 'ar', 'br', or 'us'")
    p_stop.add_argument("-t", "--time", type=int, default=2, help="Graceful stop timeout in seconds (default: 2)")
    add_common(p_stop)

    # Command: restart
    p_restart = subparsers.add_parser("restart", help="Restart an HMS container environment")
    p_restart.add_argument("-e", "--env", required=True, choices=["prod", "test"], help="Environment: 'prod' or 'test'")
    p_restart.add_argument("-c", "--country", required=True, choices=["ar", "br", "us"], help="Country: 'ar', 'br', or 'us'")
    p_restart.add_argument("-b", "--build", action="store_true", help="Rebuild image before restarting")
    add_common(p_restart)

    # Command: rm
    p_rm = subparsers.add_parser("rm", aliases=["remove"], help="Remove an HMS container")
    p_rm.add_argument("-e", "--env", required=True, choices=["prod", "test"], help="Environment: 'prod' or 'test'")
    p_rm.add_argument("-c", "--country", required=True, choices=["ar", "br", "us"], help="Country: 'ar', 'br', or 'us'")
    p_rm.add_argument("-f", "--force", action="store_true", help="Force remove running container")
    add_common(p_rm)

    # Command: status
    p_status = subparsers.add_parser("status", help="Show overview and status of HMS environments")
    p_status.add_argument("-e", "--env", choices=["prod", "test"], help="Filter by environment (optional)")
    p_status.add_argument("-c", "--country", choices=["ar", "br", "us"], help="Filter by country (optional)")
    add_common(p_status)

    # Command: logs
    p_logs = subparsers.add_parser("logs", help="View container logs")
    p_logs.add_argument("-e", "--env", required=True, choices=["prod", "test"], help="Environment: 'prod' or 'test'")
    p_logs.add_argument("-c", "--country", required=True, choices=["ar", "br", "us"], help="Country: 'ar', 'br', or 'us'")
    p_logs.add_argument("-f", "--follow", action="store_true", help="Follow log output")
    p_logs.add_argument("-n", "--tail", type=int, default=50, help="Number of lines to show (default: 50)")
    add_common(p_logs)

    # Command: build
    p_build = subparsers.add_parser("build", help="Rebuild the container image")
    p_build.add_argument("-t", "--tag", default=DEFAULT_IMAGE, help=f"Image tag (default: {DEFAULT_IMAGE})")
    p_build.add_argument("--no-cache", action="store_true", help="Do not use cache when building image")
    add_common(p_build)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    cmd_dispatch = {
        "start": cmd_start,
        "stop": cmd_stop,
        "restart": cmd_restart,
        "rm": cmd_rm,
        "remove": cmd_rm,
        "status": cmd_status,
        "logs": cmd_logs,
        "build": cmd_build,
    }

    handler = cmd_dispatch.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
