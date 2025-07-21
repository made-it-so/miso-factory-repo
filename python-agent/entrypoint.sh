#!/bin/sh
exec waitress-serve --host=0.0.0.0 --port=5002 src.main:app 2>&1
