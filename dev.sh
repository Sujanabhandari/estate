#!/bin/sh

# Author : Bishal Pun
source .env
if [ $1 = "-h" ]
then
    echo """
    Command: ./dev.sh <TICKET_NO> <TICKET_TYPE> <TICKET_NAME>

    Example: ./dev.sh 999 feature implement-cache-system-for-autocomplete
    will run with PROJECT_CODE=RBA and INITIAL_ADDONS=rb_testing:

    1. git checkout master-dev
    2. git pull
    3. git checkout -b feature/RBA-999_implement-cache-system-for-autocomplete
    4. git push -u origin feature/RBA-999_implement-cache-system-for-autocomplete
    5. docker exec -it ronba-odoo14 python3 /odoo/odoo/odoo-bin --config=/etc/odoo.conf -d RBA-999 -i rb_testing --stop-after-init --without-demo all
    6. docker exec -it ronba-odoo14 python3 /odoo/odoo/odoo-bin --config=/etc/odoo.conf -d RBA-999

    So now you are all set to start working on you ticket."""
else
    # JIIRA ticket number or any reference
    TICKET_REF=$1

    # TICKET type such as hotfix, feature, bugfix, etc
    TICKET_TYPE=$2

    # Checkout origin branch
    DEV_BRANCH_NAME="${DEV_BRANCH:-main-dev}"

    PROJECT=${PROJECT_CODE:-BASE}

    # Database name
    DB_NAME=${PROJECT}_$TICKET_REF

    # BRANCH name
    BRANCH_NAME="${TICKET_TYPE}/$PROJECT-${TICKET_REF}_${3}"

    git checkout $DEV_BRANCH_NAME
    git pull
    git checkout -b $BRANCH_NAME
    git push -u origin $BRANCH_NAME
    docker exec -it $PROJECT-ODOO python3 /usr/bin/odoo -p 9999 -d $DB_NAME -i ${INITIAL_ADDONS:-web} --stop-after-init --without-demo all
    echo "*****************"
    echo "The database named $DB_NAME has been created successfully."
    echo "*****************"
fi
