import sys
import config
import treecode
import build
from typing import Any, Literal

# constants
PREFIX = "-"
INIT_TAG = "init"
BUILD_TAG = "build"

def main():
	# parse command
	assert len(sys.argv) > 1, "no arguments provided"

	if sys.argv[1] == INIT_TAG:
		config.init_file()
	elif sys.argv[1] == BUILD_TAG: 
		build.main()

main()			