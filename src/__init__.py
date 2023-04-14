import sys
import os
import config
import treecode
import build
from typing import Any, Literal

# constants
INIT_TAG = "init"
BUILD_TAG = "build"
AUTH_PLAYFAB_TAG = "auth-playfab"
AUTH_AAD_TAG = "auth-aad"
AUTH_ROBLOX_TAG = "auth-roblox"
AUTH_ALL_TAG = "auth"
CLEAN_TAG = "clean"

def main():
	# parse command
	assert len(sys.argv) > 1, "no arguments provided"

	if sys.argv[1] == INIT_TAG:
		config.init_file()
	elif sys.argv[1] == BUILD_TAG: 
		treecode.set_tree_encoding()
		build.main()
	elif sys.argv[1] == AUTH_PLAYFAB_TAG:
		auth_config = config.get_auth_config()
		auth_config["playfab"] = config.set_config_by_console(auth_config["playfab"])
		config.set_auth_config(auth_config)
	elif sys.argv[1] == AUTH_AAD_TAG:
		auth_config = config.get_auth_config()
		auth_config["aad"] = config.set_config_by_console(auth_config["aad"])
		config.set_auth_config(auth_config)
	elif sys.argv[1] == AUTH_ROBLOX_TAG:
		auth_config = config.get_auth_config()
		auth_config["roblox"] = config.set_config_by_console(auth_config["roblox"])
		config.set_auth_config(auth_config)
	elif sys.argv[1] == CLEAN_TAG:
		midas_config = config.get_midas_config()
		config.remove_config()

		server_boot_build_path = midas_config["build"]["server_boot_script_path"]
		if os.path.exists(server_boot_build_path):
			os.remove(server_boot_build_path)

		client_boot_build_path = midas_config["build"]["client_boot_script_path"]
		if os.path.exists(client_boot_build_path):
			os.remove(client_boot_build_path)

		shared_tree_build_path = midas_config["build"]["shared_state_tree_path"]
		if os.path.exists(shared_tree_build_path):
			os.remove(shared_tree_build_path)

		module_build_path = midas_config["build"]["midas_py_module_out_path"]
		if os.path.exists(module_build_path):
			os.remove(module_build_path)

	elif sys.argv[1] == AUTH_ALL_TAG:
		auth_config = config.get_auth_config()
		auth_config["playfab"] = config.set_config_by_console(auth_config["playfab"])
		auth_config["aad"] = config.set_config_by_console(auth_config["aad"])
		auth_config["roblox"] = config.set_config_by_console(auth_config["roblox"])
		config.set_auth_config(auth_config)
	else:
		raise ValueError(f"{sys.argv[1]} does not match any known tags")

main()			