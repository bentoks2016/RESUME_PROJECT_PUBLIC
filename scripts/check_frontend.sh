#!/usr/bin/env bash

set -euo pipefail

echo "Checking JavaScript syntax..."

for file in app/static/*.js
do
    node --check "$file"
    echo "  ✓ $file"
done

echo
echo "Checking for inline event handlers..."

if grep -R -nE \
    'on(click|change|input|submit|load|keyup|keydown)=' \
    app/templates/index.html \
    app/static/*.js
then
    echo
    echo "ERROR: inline event handlers found."
    exit 1
fi

echo "  ✓ none found"

echo
echo "Frontend structural checks passed."
