import toml
import json
import os
import re
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

class TemplateConfig(TypedDict):
	join: bool
	chat: bool
	population: bool
	server_performance: bool
	market: bool
	exit: bool
	character: bool
	player: bool
	demographics: bool
	client_performance: bool
	group: dict[str, int]

class MidasConfig(TypedDict):
	download: bool
	encoding_marker: str
	python: PythonConfig
	playfab: PlayFabConfig
	recorder: RecorderConfig
	build: BuildConfig
	gamepasses: dict[str, int]
	templates: TemplateConfig

class AADConfig(TypedDict):
	client_id: str
	client_secret: str
	tenant_id: str

class PlayFabAuthConfig(TypedDict):
	title_id: str
	dev_secret_key: str

class RobloxAuthConfig(TypedDict):
	cookie: str
	
class AuthConfig(TypedDict):
	playfab: PlayFabAuthConfig
	aad: AADConfig
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
	"templates": {
		"join": False,
		"chat": False,
		"population": False,
		"server_performance": False,
		"market": False,
		"exit": False,
		"character": False,
		"player": False,
		"demographics": False,
		"client_performance": False,
		"group": {},
	},
	"gamepasses": {},
	"build": {
		"server_boot_script_path": "src/Server/Analytics.luau",
		"shared_state_tree_path": "src/Shared/MidasTree.luau"
	},
}

DEFAULT_AUTH_CONFIG_TEMPLATE: AuthConfig = {
	"playfab": {
		"title_id": "123AB",
		"dev_secret_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
	},
	"aad": {
		"client_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx",
		"client_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
		"tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx",
	},
	"roblox": {
		"cookie": "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_xxxxxxxxxxxxxxxxxxxxxx",
	}
}

def init_file():
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
		print("no midas-tree.json, have you initialized?")

	tree: Any = json.loads(open(MIDAS_TREE_PATH, "r").read())

	midas_config = get_midas_config()

	if midas_config["templates"]["chat"]:
		tree["Chat"] = {
			"LastMessage": "string",
			"Count": "integer",
		}

	if midas_config["templates"]["character"]:
		tree["Character"] = {
			"IsDead": "boolean",
			"Height": "double",
			"Mass": "double",
			"State": [
				"FallingDown", 
				"Running", 
				"RunningNoPhysics", 
				"Climbing",
				"StrafingNoPhysics",
				"Ragdoll",
				"GettingUp",
				"Jumping",
				"Landed",
				"Flying",
				"Freefall",
				"Seated",
				"PlatformStanding",
				"Dead",
				"Swimming",
				"Physics",
				"None"
			],
			"WalkSpeed": "double",
			"Position": {
				"X": "double",
				"Y": "double",
			},
			"Altitude": "double",
			"JumpPower": "double",
			"Health": "double",
			"MaxHealth": "double",
			"Deaths": "integer",
		}

	if midas_config["templates"]["population"]:
		tree["Population"] = {
			"Total": "integer",
			"Team": "integer",
			"PeakFriends": "integer",
			"Friends": "integer",
			"SpeakingDistance": "integer",
		}

	if midas_config["templates"]["server_performance"]:
		if not "Performance" in tree:
			tree["Performance"] = {}

		tree["Performance"]["Server"] = {
			"EventsPerMinute": "integer",
			"Ping": "integer",
			"ServerTime": "integer",
			"HeartRate": "integer",
			"Instances": "integer",
			"MovingParts": "integer",
			"Network": {
				"Data": {
					"Send": "integer",
					"Receive": "integer",
				},
				"Physics": {
					"Send": "integer",
					"Receive": "integer",
				},
				"Memory": {
					"Internal": "integer",
					"HttpCache": "integer",
					"Instances": "integer",
					"Signals": "integer",
					"LuaHeap": "integer",
					"Script": "integer",
					"PhysicsCollision": "integer",
					"PhysicsParts": "integer",
					"CSG": "integer",
					"Particle": "integer",
					"Part": "integer",
					"MeshPart": "integer",
					"SpatialHash": "integer",
					"TerrainGraphics": "integer",
					"Textures": "integer",
					"CharacterTextures": "integer",
					"SoundsData": "integer",
					"SoundsStreaming": "integer",
					"TerrainVoxels": "integer",
					"Guis": "integer",
					"Animations": "integer",
					"Pathfinding": "integer",
				},
			},
		}

	if midas_config["templates"]["market"]:
		tree["Market"] = {
			"Spending": {
				"Gamepass": "integer",
				"Product": "integer",
				"Total": "integer",
			},
			"Gamepasses": {},
		}
		for gamepass_name in midas_config["gamepasses"]:
			formatted_pass_name = re.sub(r'\s', '', gamepass_name)
			tree["Market"]["Gamepasses"][formatted_pass_name] = "boolean"

	if len(list(midas_config["templates"]["group"].keys())) > 0:
		tree["Groups"] = {}
		for group_name, group_id in (midas_config["templates"]["group"]).items():
			formatted_group_name = re.sub(r'\s', '', group_name)
			tree["Groups"][formatted_group_name] = "boolean"

	if midas_config["templates"]["demographics"]:
		tree["Demographics"] = {
			"AccountAge": "integer",
			"RobloxLangugage": "string",
			"SystemLanguage": "string",
			"Platform": {
				"Accelerometer": "boolean",
				"Gamepad": "boolean",
				"Gyroscope": "boolean",
				"Keyboard": "boolean",
				"Mouse": "boolean",
				"Touch": "boolean",
				"ScreenSize": "integer",
				"ScreenRatio": ["16:10","16:9","5:4","5:3","3:2","4:3","9:16","uncommon"],
			},
		}

	if midas_config["templates"]["client_performance"]:
		if not "Performance" in tree:
			tree["Performance"] = {}

		tree["Performance"]["Client"] = {
			"Ping": "integer",
			"FPS": "integer",
		}

	return tree

def get_midas_config() -> MidasConfig:
	if not os.path.exists(CONFIG_TOML_PATH):
		print("no midas.toml, have you initialized?")

	config: Any = toml.loads(open(CONFIG_TOML_PATH, "r").read())
	return config

def get_auth_config() -> AuthConfig:
	if not os.path.exists(AUTH_CONFIG_TOML_PATH):
		print("no midas-auth.toml, have you initialized?")

	config: Any = toml.loads(open(AUTH_CONFIG_TOML_PATH, "r").read())
	return config
