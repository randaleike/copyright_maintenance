#!/bin/bash
clear
coverage run -m pytest -s
coverage report --fail-under=98
