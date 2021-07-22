#!/bin/bash

if ! docker info >/dev/null 2>&1
then
  echo "ERROR: docker not running"
  exit 1
fi

python - << EOF
import sys

if not (sys.version_info.major == 3 and sys.version_info.minor == 8):
    print("You must use Python 3.8.X")
    print("You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
    sys.exit(1)

EOF

exit_status=$?

if [[ $exit_status != 1 ]]; then
            
    USER_ID=$ARTIFACTORY_USER
    API_KEY=$ARTIFACTORY_TOKEN


    #REQ_FILES=(lambdas/mock_encrypted_credential_get/requirements.txt)

    echo "sam_full_build started"

    #echo "add-extra-index-url for ${REQ_FILES[0]}"
    #add-extra-index-url "$USER_ID" "$API_KEY" --req-file "${REQ_FILES[0]}"

    echo "sam build --use-container"
    sam build --use-container

    #echo "remove-extra-index-url for ${REQ_FILES[0]}"
    #remove-extra-index-url --req-file "${REQ_FILES[0]}"

    echo "sam_full_build completed"
fi
