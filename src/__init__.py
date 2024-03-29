import sys
import os
import keyring
import multiprocessing
import pandas as pd
from pandas import DataFrame
import midas.playfab as playfab
import midas.data_encoder as data_encoder
from midas.playfab import PlayFabClient
import src.config as config
import src.treecode as treecode
import src.build as build
from src.config import CREDENTIAL_USERNAME

# constants
INIT_TAG = "init"
BUILD_LUAU_TAG = "build"
AUTH_PLAYFAB_TAG = "auth-playfab"
AUTH_AAD_TAG = "auth-aad"
AUTH_ROBLOX_TAG = "auth-roblox"
AUTH_ALL_TAG = "auth"
CLEAN_TAG = "clean"
DOWNLOAD_TAG = "download"
RAW_TAG = "-raw"

def download(json_path: str, download_start_data: str, download_window: int, user_limit: int, is_raw: bool):
	abs_json_path = os.path.abspath(json_path)

	# midas_config = config.get_midas_config()

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
		user_join_floor=playfab.get_datetime_from_playfab_str(download_start_data),
		join_window_in_days=download_window,
		user_limit= user_limit
	))

	if not is_raw:
		print("decoding")
		decoded_df = data_encoder.decode_raw_df(df, treecode.get_tree_encoding())

		print("writing to json")
		decoded_df.to_json(abs_json_path, indent=4, orient="records")
		
		return decoded_df
	else:
		print("writing raw to json")
		df.to_json(abs_json_path, indent=4, orient="records")

		return df

def main():
	# parse command
	assert len(sys.argv) > 1, "no arguments provided"

	if sys.argv[1] == INIT_TAG:

		config.init_file()

	elif sys.argv[1] == BUILD_LUAU_TAG: 

		treecode.set_tree_encoding()
		if len(sys.argv) > 2:
			keyring.set_password("title_id", CREDENTIAL_USERNAME, sys.argv[2])
			keyring.set_password("dev_secret_key", CREDENTIAL_USERNAME, sys.argv[3])

		build.main()

	elif sys.argv[1] == AUTH_PLAYFAB_TAG:

		keyring.set_password("title_id", CREDENTIAL_USERNAME, input("playfab title id: "))
		keyring.set_password("dev_secret_key", CREDENTIAL_USERNAME, input("playfab dev secret key: "))

	elif sys.argv[1] == AUTH_AAD_TAG:

		keyring.set_password("client_id", CREDENTIAL_USERNAME, input("aad client id: "))
		keyring.set_password("client_secret", CREDENTIAL_USERNAME, input("aad client secret value (not id): "))
		keyring.set_password("tenant_id", CREDENTIAL_USERNAME, input("aad tenant id: "))

	elif sys.argv[1] == AUTH_ROBLOX_TAG:

		keyring.set_password("cookie", CREDENTIAL_USERNAME, input("roblox security cookie: "))

	elif sys.argv[1] == DOWNLOAD_TAG:

		download(
			json_path=sys.argv[2], 
			download_start_data=sys.argv[3], 
			download_window=int(sys.argv[4]), 
			user_limit=int(sys.argv[5]),
			is_raw=(RAW_TAG in sys.argv)
		)

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

		# module_build_path = midas_config["build"]["midas_py_module_out_path"]
		# if os.path.exists(module_build_path):
		# 	os.remove(module_build_path)

	elif sys.argv[1] == AUTH_ALL_TAG:

		keyring.set_password("title_id", CREDENTIAL_USERNAME, input("playfab title id: "))
		keyring.set_password("dev_secret_key", CREDENTIAL_USERNAME, input("playfab dev secret key: "))
		keyring.set_password("client_id", CREDENTIAL_USERNAME, input("aad client id: "))
		keyring.set_password("client_secret", CREDENTIAL_USERNAME, input("aad client secret: "))
		keyring.set_password("tenant_id", CREDENTIAL_USERNAME, input("aad tenant id: "))
		keyring.set_password("cookie", CREDENTIAL_USERNAME, input("roblox security cookie: "))

	else:

		raise ValueError(f"{sys.argv[1]} does not match any known tags")

# prevent from running twice
if __name__ == '__main__':
	multiprocessing.freeze_support()
	main()		
