# Source this script for deploy-related functions

# Assume the deploy role in this shell.
# NOTE: Must have AWS_REGION in environment.
function ibot_assume_deploy_role() {
  ENVIRONMENT="$1"
  SESSION_NAME="$2"
  shift
  shift

  if [[ "${ENVIRONMENT}" != "dev" ]]; then
    echo "Supported environments: dev"
    return 1
  fi

  ACCOUNT_ID="$(aws sts get-caller-identity --query 'Account' --output text)"
  ROLE_NAME="cdk-ibot-${ENVIRONMENT}-deploy-role-${ACCOUNT_ID}-${AWS_REGION}"
  ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
  OUTPUT="$(aws sts assume-role --role-arn ${ROLE_ARN} --role-session-name ${SESSION_NAME} --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' --output text)"
  echo "Exporting credentials for ${ROLE_NAME} in current shell"
  export $(printf "AWS_ACCESS_KEY_ID=%s AWS_SECRET_ACCESS_KEY=%s AWS_SESSION_TOKEN=%s" ${OUTPUT})
}

function ibot_clear_creds() {
  unset AWS_ACCESS_KEY_ID
  unset AWS_SECRET_ACCESS_KEY
  unset AWS_SESSION_TOKEN
}
