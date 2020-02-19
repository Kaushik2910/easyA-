#!/bin/bash
export FLASK_APP=easyA
export FLASK_ENV=development

python -m flask run

echo "localhost:5000"
