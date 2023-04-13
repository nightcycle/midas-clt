import toml
import json
import os
from typing import TypedDict, Literal, Union, Any

TrackerType = Literal["boolean", "integer", "double", "float", "string"]

class VersionData(TypedDict):
	Build: TrackerType
	Major: TrackerType
	Minor: TrackerType

class IndexData(TypedDict):
	Total: TrackerType
	Event: TrackerType

class IdentificationData(TypedDict):
	Place: TrackerType
	Session: TrackerType
	User: TrackerType
	
class BaseStateTree(TypedDict):
	Version: VersionData
	IsStudio: TrackerType
	Index: IndexData
	Duration: TrackerType
	Id: IdentificationData

class BuildConfig(TypedDict):
	server_boot_script_path: str
	shared_state_tree_path: str

class RecorderTargetConfig(TypedDict):
	place_id: int
	group_id: int

class RecorderConfig(TypedDict):
	interval: int
	out_path: str
	id: RecorderTargetConfig

class PlayFabConfig(TypedDict):
	download_start_date: str
	download_window: int
	user_limit: int

class PythonConfig(TypedDict):
	midas_module_out_path: str

class MidasConfig(TypedDict):
	download: bool
	encoding_marker: str
	python: PythonConfig
	playfab: PlayFabConfig
	recorder: RecorderConfig
	build: BuildConfig

class PlayFabAuthConfig(TypedDict):
	title_id: str
	client_id: str
	client_secret: str
	tenant_id: str

class RobloxAuthConfig(TypedDict):
	cookie: str
	
class AuthConfig(TypedDict):
	playfab: PlayFabAuthConfig
	roblox: RobloxAuthConfig

CONFIG_TOML_PATH = "midas.toml"
MIDAS_TREE_PATH = "midas-tree.json"
AUTH_CONFIG_TOML_PATH = "midas-auth.toml"

DEFAULT_TREE: Union[BaseStateTree, dict] = {
	"Duration": "integer",
	"IsStudio": "boolean",
	"Version": {
		"Build": "integer",
		"Major": "integer",
		"Minor": "integer",
	},
	"Index": {
		"Total": "integer",
		"Event": "integer",
	},
	"Id": {
		"Place": "string",
		"User": "string",
		"Session": "string",
	}
}

DEFAULT_CONFIG_TEMPLATE: MidasConfig = {
	"download": True,
	"encoding_marker": "~",
	"python": {
		"midas_module_out_path": "path/to/script"
	},
	"playfab": {
		"download_start_date": "1970-1-01 00:00:00.000000",
		"download_window": 30,
		"user_limit": 10000000,
	},
	"recorder": {
		"interval": 60,
		"out_path": "path/to/data/record/dir/here",
		"id": {
			"place_id": 12345,
			"group_id": 67890,
		}
	},
	"build": {
		"server_boot_script_path": "src/Server/Analytics.luau",
		"shared_state_tree_path": "src/Shared/MidasTree.luau"
	},
}

DEFAULT_AUTH_CONFIG_TEMPLATE: AuthConfig = {
	"playfab": {
		"title_id": "123AB",
		"client_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx",
		"client_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
		"tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx",
	},
	"roblox": {
		"cookie": "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_xxxxxxxxxxxxxxxxxxxxxx",
	}
}

def init_file():
	print("init file")
	assert not os.path.exists(CONFIG_TOML_PATH), f"{CONFIG_TOML_PATH} file already exists, deleting it could break encoding"

	config_file = open(CONFIG_TOML_PATH, "w")
	config_file.write(toml.dumps(DEFAULT_CONFIG_TEMPLATE))
	config_file.close()

	auth_file = open(AUTH_CONFIG_TOML_PATH, "w")
	auth_file.write(toml.dumps(DEFAULT_AUTH_CONFIG_TEMPLATE))
	auth_file.close()

	tree_file = open(MIDAS_TREE_PATH, "w")
	tree_file.write(json.dumps(DEFAULT_TREE, indent=5))
	tree_file.close()

def get_midas_tree() -> Union[BaseStateTree, dict]:
	if not os.path.exists(MIDAS_TREE_PATH):
		print("no midas-tree.json")

	tree: Any = json.loads(open(MIDAS_TREE_PATH, "r").read())
	return tree

def get_midas_config() -> MidasConfig:
	if not os.path.exists(CONFIG_TOML_PATH):
		print("no midas.toml")

	config: Any = toml.loads(open(CONFIG_TOML_PATH, "r").read())
	return config

def get_auth_config() -> AuthConfig:
	if not os.path.exists(AUTH_CONFIG_TOML_PATH):
		print("no midas-auth.toml")

	config: Any = toml.loads(open(AUTH_CONFIG_TOML_PATH, "r").read())
	return config
