#!/bin/bash
# ====================================================================
# HMS 3.0 Container Deployment Script
# Multi-Country: Argentina (AR), Brazil (BR), USA (US)
# Usage: ./launch_hms.sh [prod|test] [ar|br|us]
# Default country: ar
# ====================================================================

set -euo pipefail

ENVIRONMENT="${1:-}"
COUNTRY="${2:-ar}"

if [[ -z "$ENVIRONMENT" ]]; then
    echo "ERROR: You must specify an environment."
    echo "Usage: $0 [prod|test] [ar|br|us]"
    echo "Example: $0 prod ar"
    echo "Example: $0 test us"
    exit 1
fi

ENVIRONMENT=$(echo "$ENVIRONMENT" | tr '[:upper:]' '[:lower:]')
COUNTRY=$(echo "$COUNTRY" | tr '[:upper:]' '[:lower:]')

case "$COUNTRY" in
  ar)
    COUNTRY_LABEL="Argentina (Ley 25.326)"
    ;;
  br)
    COUNTRY_LABEL="Brazil (LGPD)"
    ;;
  us)
    COUNTRY_LABEL="United States (HIPAA)"
    ;;
  *)
    echo -e "\nERROR: Invalid country '$COUNTRY'."
    echo "Valid options: 'ar', 'br', 'us'."
    exit 1
    ;;
esac

SOURCE_ENV=".env-${ENVIRONMENT}-${COUNTRY}"

case "$ENVIRONMENT" in
  prod)
    PROJECT_NAME="hms3_prod"
    PORT_HINT="8012"
    echo -e "\n-> Target Environment: PRODUCTION (${COUNTRY_LABEL})"
    ;;
  test)
    PROJECT_NAME="hms3_test"
    PORT_HINT="8013"
    echo -e "\n-> Target Environment: TEST VDB Masked (${COUNTRY_LABEL})"
    ;;
  *)
    echo -e "\nERROR: Invalid environment '$ENVIRONMENT'."
    echo "Valid options: 'prod' or 'test'."
    exit 1
    ;;
esac

if [ ! -f "$SOURCE_ENV" ]; then
    echo "CRITICAL ERROR: Configuration file '$SOURCE_ENV' does not exist."
    if [ -f "${SOURCE_ENV}.example" ]; then
        echo "Tip: Copy '${SOURCE_ENV}.example' to '$SOURCE_ENV' and configure your SQL Server credentials:"
        echo "     cp ${SOURCE_ENV}.example $SOURCE_ENV"
    fi
    exit 1
fi

echo "--------------------------------------------------------"
echo "Deploying container for project: $PROJECT_NAME"
echo "Country Configuration        : $COUNTRY_LABEL"
echo "Loaded config file           : $SOURCE_ENV"
echo "--------------------------------------------------------"

echo "-> Stopping previous containers if running..."
sudo ENV_FILE="$SOURCE_ENV" podman-compose --env-file "$SOURCE_ENV" -f docker-compose-app.yml -p "$PROJECT_NAME" down || true

echo "-> Starting container..."
sudo ENV_FILE="$SOURCE_ENV" podman-compose --env-file "$SOURCE_ENV" -f docker-compose-app.yml -p "$PROJECT_NAME" up -d --build

echo ""
echo "========================================================"
echo " SUCCESS! HMS 3.0 has been deployed."
echo " Environment : $ENVIRONMENT"
echo " Country     : $COUNTRY_LABEL"
echo " Project     : $PROJECT_NAME"
echo " URL         : http://$(hostname -I | awk '{print $1}'):${PORT_HINT}/"
echo "========================================================"
