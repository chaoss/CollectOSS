#!/bin/bash
set -euo pipefail

echo
echo "**********************************"
echo "Starting workers..."
echo "**********************************"
echo

for WORKER in $(ls -d workers/*/)
do
    if [[ $WORKER == *"_worker"* ]]; then

      if [[ $WORKER != *"spdx_worker"* && $WORKER != *"value_worker"* ]]; then

        # make it pretty for formatting
        FORMATTED_WORKER=${WORKER/#workers\//}
        FORMATTED_WORKER=${FORMATTED_WORKER/%\//}

        echo
        echo "**********************************"
        echo "Starting $FORMATTED_WORKER..."
        echo "**********************************"
        echo

        cd $WORKER
        WORKER_CMD="_start"
        WORKER_CMD="${FORMATTED_WORKER}_start"
        nohup $WORKER_CMD 1> /dev/null 2> /dev/null &
        cd ../..
        sleep 30
      fi
    fi
done