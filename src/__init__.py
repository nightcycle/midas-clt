import os
import shutil
import sys
import config
from typing import Any, Literal

# constants
PREFIX = "-"
INIT_TAG = "init"
BUILD_TAG = "build"
ENCODE_UPDATE = "update-encoding"

def initialize():
	config.init_file()

def build():
	print("building")

def update_encoding():
	print("update encoding")

def main():
	# parse command
	assert len(sys.argv) > 1, "no arguments provided"

	if sys.argv[1] == INIT_TAG:
		initialize()
	elif sys.argv[1] == BUILD_TAG: 
		build()
	elif sys.argv[1] == ENCODE_UPDATE:
		update_encoding()

main()			