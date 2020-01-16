#!/bin/bash

if [[ ! -d logs ]]; then
    mkdir logs
fi

echo
echo "**********************************"
echo "Starting workers..."
echo "**********************************"
echo

for WORKER in $(ls -d workers/*/)
do
    if [[ $WORKER == *"_worker"* ]]; then

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
      nohup $WORKER_CMD > "${FORMATTED_WORKER}.log" 2> "${FORMATTED_WORKER}.err" &
      cd ../..
      sleep 30

    fi
done