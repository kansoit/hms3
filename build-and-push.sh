#!/usr/bin/env bash
# Construye la imagen de HMS 3.0 y la sube al Container Registry de GitLab.
#
#   ./build-and-push.sh
#
# El destino se lee de .env-registry (local, fuera de git; ver .env-registry.example)
# o de la variable HMS_REGISTRY_IMAGE. Antes hay que haber hecho login una vez:
#   sudo podman login <host-del-registry> -u <usuario>
# Usa "sudo podman", igual que hms-ctl.py; con HMS_ROOTLESS=1 usa "podman" sin sudo.
set -euo pipefail
cd "$(dirname "$0")"

[ -f .env-registry ] && . ./.env-registry
: "${HMS_REGISTRY_IMAGE:?Falta HMS_REGISTRY_IMAGE. Copiá .env-registry.example a .env-registry y completalo.}"
LOCAL_IMAGE=${HMS_IMAGE:-hms3-app:1.0}
TAGS=${HMS_REGISTRY_TAGS:-"1.0 latest"}
REGISTRY_HOST=${HMS_REGISTRY_IMAGE%%/*}

if [ "${HMS_ROOTLESS:-}" = 1 ]; then ENGINE=(podman); else ENGINE=(sudo podman); fi

# Sin login el push falla recién al final, después de todo el build: se verifica antes.
if ! "${ENGINE[@]}" login --get-login "$REGISTRY_HOST" >/dev/null 2>&1; then
    echo "ERROR: no hay sesión en $REGISTRY_HOST. Ejecutá: ${ENGINE[*]} login $REGISTRY_HOST -u <usuario>" >&2
    exit 1
fi

if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    echo "AVISO: hay cambios sin commitear; la imagen quedará marcada como '-dirty'." >&2
fi

HMS_IMAGE="$LOCAL_IMAGE" ./hms-ctl.py build

for tag in $TAGS; do
    "${ENGINE[@]}" tag "$LOCAL_IMAGE" "$HMS_REGISTRY_IMAGE:$tag"
    "${ENGINE[@]}" push "$HMS_REGISTRY_IMAGE:$tag"
done

echo "OK: imagen subida a $HMS_REGISTRY_IMAGE (tags: $TAGS, build $(git rev-parse --short HEAD))."
