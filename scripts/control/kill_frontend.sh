#!/bin/bash

echo "Stopping frontend processes..."
ps -efx | grep augur | pgrep -f "vue-cli-service serve" | xargs kill