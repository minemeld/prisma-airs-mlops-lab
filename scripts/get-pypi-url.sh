#!/bin/bash
#
# Get authenticated PyPI URL for AIRS Model Security SDK
# Requires: MODEL_SECURITY_CLIENT_ID, MODEL_SECURITY_CLIENT_SECRET, TSG_ID
#

set -euo pipefail

: "${MODEL_SECURITY_CLIENT_ID:?Error: MODEL_SECURITY_CLIENT_ID not set}"
: "${MODEL_SECURITY_CLIENT_SECRET:?Error: MODEL_SECURITY_CLIENT_SECRET not set}"
: "${TSG_ID:?Error: TSG_ID not set}"

TOKEN_ENDPOINT="${MODEL_SECURITY_TOKEN_ENDPOINT:-https://auth.apps.paloaltonetworks.com/oauth2/access_token}"
API_ENDPOINT="${MODEL_SECURITY_API_ENDPOINT:-https://api.sase.paloaltonetworks.com/aims}"

# Get OAuth token
TOKEN_RESPONSE=$(curl -sf -X POST "$TOKEN_ENDPOINT" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -u "$MODEL_SECURITY_CLIENT_ID:$MODEL_SECURITY_CLIENT_SECRET" \
    -d "grant_type=client_credentials&scope=tsg_id:$TSG_ID") || {
    echo "Error: Failed to obtain access token" >&2
    exit 1
}

SCM_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')

# Get PyPI URL
PYPI_RESPONSE=$(curl -sf -X GET "$API_ENDPOINT/mgmt/v1/pypi/authenticate" \
    -H "Authorization: Bearer $SCM_TOKEN") || {
    echo "Error: Failed to retrieve PyPI URL" >&2
    exit 1
}

echo "$PYPI_RESPONSE" | jq -r '.url'
