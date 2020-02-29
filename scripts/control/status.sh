#!/bin/bash
set -euo pipefail

monitor=${1-quick}

echo "augur logs"
echo "*****************************"

if [[ $monitor == "quick" ]]; then
  tail -n 20 logs/augur.log

  for WORKER in $(ls -d workers/*/)
  do
      if [[ $WORKER == *"_worker"* ]]; then

        # make it pretty for formatting
        FORMATTED_WORKER=${WORKER/#workers\//}
        FORMATTED_WORKER=${FORMATTED_WORKER/%\//}

        echo "$FORMATTED_WORKER"
        echo "*****************************"

        cd $WORKER
        tail -n 20 *.log
        echo
        echo
        cd ../..

      fi
  done
else
  less +F logs/augur.log workers/**/*.log
fi