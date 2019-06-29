#!/bin/sh

export FLASK_APP=restAPI
export FLASK_ENV=development

flask init-db

flask run
