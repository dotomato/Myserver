#!/usr/bin/env bash
uwsgi --http 0.0.0.0:5001 -w main:app --master --processes 4 --threads 4