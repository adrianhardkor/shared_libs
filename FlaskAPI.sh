#!/bin/bash

cd /opt/FlaskAPI/shared_libs
/etc/.pyenv/shims/python3 ./FlaskAPI.py | /usr/bin/logger --tag FlaskAPI
