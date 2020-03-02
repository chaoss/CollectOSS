#!/bin/bash

function reset_env () {
    pip freeze > temp.txt;
    cat temp.txt;
    pip uninstall -r temp.txt -y --quiet;
    rm temp.txt;
}

if [[ "$VIRTUAL_ENV" ]]; then
    echo
    echo "Saving your environment:"
    pip freeze > pyenv.txt

    reset_env

    echo
    echo "Exporting prod dependencies:"
    pip install . --quiet
    pip freeze > requirements.txt

    reset_env

    echo
    echo "Exporting dev dependencies:"
    pip install .[dev] --quiet
    pip freeze > dev_requirements.txt

    reset_env

    echo
    echo "Loading your environment:"
    pip install -r pyenv.txt --quiet
fi

