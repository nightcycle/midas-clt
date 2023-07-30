#!/bin/bash
pyinstaller --onefile src/__init__.py -n midas --additional-hooks-dir=hooks --add-data "src/data/Packages.zip;data/"