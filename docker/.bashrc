NOCOLOR='\001\033[0m\002'

RED='\001\033[00;31m\002'
GREEN='\001\033[00;32m\002'
BLUE='\001\033[00;34m\002'
PURPLE='\001\033[00;35m\002'

ENVIRONMENT=${ENVIRONMENT:-unknown}

case ${ENVIRONMENT} in
  "prod"|"pro"|"production")
    ENV_COLOR="$RED"
    ;;
  "local")
    ENV_COLOR="$BLUE"
    ;;
  *)
    ENV_COLOR="$PURPLE"
    ;;
esac

ENV_PROMPT="${ENV_COLOR}(${PROJECT_NAME}_${ENVIRONMENT})${NOCOLOR}"

get_env_prompt() {
  echo "$ENV_PROMPT"
}

PS1="$(get_env_prompt) $PS1"