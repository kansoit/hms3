#!/usr/bin/env bash
# Construye la imagen de HMS 3.0 y la sube al Container Registry.
# Es la única herramienta que toca la imagen: hms-ctl.py solo gestiona contenedores.
#
#   ./build-and-push.sh              construye y sube al registry
#   ./build-and-push.sh --no-cache   lo mismo, sin usar el caché del build
#
# Los contenedores se lanzan desde la imagen local que deja este script; la copia
# en el registry es un resguardo. Para que un entorno use la imagen nueva:
#   ./hms-ctl.py restart -e <prod|test> -c <ar|br|us>
#
# El destino del push se lee de .env-registry (local, fuera de git; ver
# .env-registry.example) o de la variable HMS_REGISTRY_IMAGE. Antes del primer
# push hay que hacer login una vez:  sudo podman login <host-del-registry> -u <usuario>
# Usa "sudo podman", igual que hms-ctl.py; con HMS_ROOTLESS=1 usa "podman" sin sudo.
set -euo pipefail
cd "$(dirname "$0")"

BUILD_OPTS=()
for arg in "$@"; do
    case "$arg" in
        --no-cache) BUILD_OPTS+=(--no-cache) ;;
        -h|--help) sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "ERROR: opción desconocida: $arg (ver --help)" >&2; exit 2 ;;
    esac
done

LOCAL_IMAGE=${HMS_IMAGE:-hms3-app:1.0}
if [ "${HMS_ROOTLESS:-}" = 1 ]; then ENGINE=(podman); else ENGINE=(sudo podman); fi

[ -f .env-registry ] && . ./.env-registry
: "${HMS_REGISTRY_IMAGE:?Falta HMS_REGISTRY_IMAGE. Copiá .env-registry.example a .env-registry y completalo.}"
TAGS=${HMS_REGISTRY_TAGS:-"1.0 latest"}
REGISTRY_HOST=${HMS_REGISTRY_IMAGE%%/*}
# Sin login el push falla recién al final, después de todo el build: se verifica antes.
if ! "${ENGINE[@]}" login --get-login "$REGISTRY_HOST" >/dev/null 2>&1; then
    echo "ERROR: no hay sesión en $REGISTRY_HOST. Ejecutá: ${ENGINE[*]} login $REGISTRY_HOST -u <usuario>" >&2
    exit 1
fi

# La imagen queda marcada con el commit del repo: se ve en el pie de la app,
# en /api/health/ y en hms-ctl.py status.
BUILD_ID=$(git rev-parse --short HEAD 2>/dev/null || echo unknown)
if [ -n "$(git status --porcelain --untracked-files=no 2>/dev/null)" ]; then
    BUILD_ID="$BUILD_ID-dirty"
    echo "AVISO: hay cambios sin commitear; la imagen quedará marcada como '$BUILD_ID'." >&2
fi

echo "Construyendo la imagen '$LOCAL_IMAGE' (build $BUILD_ID)..."
"${ENGINE[@]}" build -t "$LOCAL_IMAGE" -f Dockerfile.django \
    --build-arg "HMS_BUILD=$BUILD_ID" ${BUILD_OPTS[@]+"${BUILD_OPTS[@]}"} .
echo "OK: imagen '$LOCAL_IMAGE' construida (build $BUILD_ID)."

for tag in $TAGS; do
    "${ENGINE[@]}" tag "$LOCAL_IMAGE" "$HMS_REGISTRY_IMAGE:$tag"
    "${ENGINE[@]}" push "$HMS_REGISTRY_IMAGE:$tag"
done
echo "OK: imagen subida a $HMS_REGISTRY_IMAGE (tags: $TAGS)."

echo "Para aplicarla a un entorno: ./hms-ctl.py restart -e <prod|test> -c <ar|br|us>"
