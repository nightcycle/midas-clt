import sys
import os
import pandas as pd
from pandas import DataFrame
import midas.data_encoder as data_encoder
from midas.playfab import PlayFabClient
import src.config as config
import src.treecode as treecode
import src.build as build

# constants
INIT_TAG = "init"
BUILD_LUAU_TAG = "build"
AUTH_PLAYFAB_TAG = "auth-playfab"
AUTH_AAD_TAG = "auth-aad"
AUTH_ROBLOX_TAG = "auth-roblox"
AUTH_ALL_TAG = "auth"
CLEAN_TAG = "clean"
DOWNLOAD_TAG = "download"

def download(csv_path: str):
	abs_csv_path = os.path.abspath(csv_path)

	midas_config = config.get_midas_config()

	auth_config = config.get_auth_config()
	pf_auth_config = auth_config["playfab"]
	aad_auth_config = auth_config["aad"]

	pf_client = PlayFabClient(
		client_id = aad_auth_config["client_id"],
		client_secret = aad_auth_config["client_secret"],
		tenant_id = aad_auth_config["tenant_id"],
		title_id = pf_auth_config["title_id"]
	)
	df = DataFrame(pf_client.download_all_event_data(
		user_join_floor=data_encoder.get_datetime_from_playfab_str(midas_config["playfab"]["download_start_date"]),
		join_window_in_days=midas_config["playfab"]["download_window"],
		user_limit= midas_config["playfab"]["user_limit"]
	))

	print("decoding")
	decoded_df = data_encoder.decode_raw_df(df, treecode.get_tree_encoding())

	print("writing to csv")
	decoded_df.to_csv(abs_csv_path)

	return decoded_df

def main():
	# parse command
	assert len(sys.argv) > 1, "no arguments provided"

	if sys.argv[1] == INIT_TAG:

		config.init_file()

	elif sys.argv[1] == BUILD_LUAU_TAG: 

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

	elif sys.argv[1] == DOWNLOAD_TAG:

		download(sys.argv[2])

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