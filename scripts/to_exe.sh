#!/bin/bash
# HEY REMEMBER YOU NEED TO CHANGE A SCRIPT IN AZURE
# env\Lib\site-packages\azure\kusto\data\kusto_trusted_endpoints.py
# COPY AND PASTE THE JSON TO THE VARIABLE DIRECTLY, IT CANT FIND THE JSON FILE IN THE EXE
pyinstaller --onefile src/__init__.py -n midas
