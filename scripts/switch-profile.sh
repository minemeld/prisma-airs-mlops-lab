#!/bin/bash
#
# Switch AIRS credential profiles
# Usage: source scripts/switch-profile.sh [superuser|model-security]
#

profile="${1:-superuser}"

case "$profile" in
  super|superuser)
    export AIRS_PROFILE=superuser
    ;;
  model|model-security)
    export AIRS_PROFILE=model-security
    ;;
  *)
    echo "Usage: source scripts/switch-profile.sh [superuser|model-security]"
    echo "Current profile: ${AIRS_PROFILE:-superuser (default)}"
    return 1
    ;;
esac

# Trigger direnv reload by touching .envrc
touch .envrc

# Give direnv a moment to reload
sleep 0.1

# Re-export direnv environment
eval "$(direnv export bash 2>/dev/null)"

echo "✅ Switched to profile: $AIRS_PROFILE"
if [ -n "$MODEL_SECURITY_CLIENT_ID" ]; then
  echo "   Credentials: $(echo $MODEL_SECURITY_CLIENT_ID | cut -d@ -f1)"
else
  echo "   ⚠️  Credentials not loaded yet - try: cd .. && cd -"
fi
