#!/bin/bash
source .env/Scripts/Activate
sh scripts/to_exe.sh
dist/midas.exe build
# dist/midas.exe init