import toml
import yaml
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
	roblox_wally_package_folder_path: str
	server_boot_script_path: str
	shared_state_tree_path: str
	client_boot_script_path: str
	midas_py_module_out_path: str

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

class ProductConfig(TypedDict):
	gamepasses: dict[str, int]
	developer_products: dict[str, int]

class VersionConfig(TypedDict):
	major: int
	minor: int
	patch: int
	hotfix: int | None

class MidasConfig(TypedDict):
	encoding_marker: str
	version: VersionConfig
	playfab: PlayFabConfig
	recorder: RecorderConfig
	build: BuildConfig
	products: ProductConfig
	templates: TemplateConfig
	state_tree: Union[BaseStateTree, dict]

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

def add_to_git_ignore(path: str, git_ignore_path=".gitignore"):
	# Create a Path object for the .gitignore file
	
	# Read the existing contents of the .gitignore file
	contents = open(git_ignore_path, "r").read()
	
	lines = contents.split("\n")
	if not path in lines:
		contents += "\n" + path
		open(git_ignore_path, "w").write(contents)


CONFIG_TOML_PATH = "midas.yaml"
AUTH_CONFIG_TOML_PATH = "midas-auth.lock"

DEFAULT_CONFIG_TEMPLATE: MidasConfig = {
	"encoding_marker": "~",
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
	"products": {
		"gamepasses": {},
		"developer_products": {}
	},
	"build": {
		"roblox_wally_package_folder_path": "game/ReplicatedStorage/Packages",
		"server_boot_script_path": "src/Server/Analytics.server.luau",
		"shared_state_tree_path": "src/Shared/MidasTree.luau",
		"client_boot_script_path": "src/Client/Analytics.client.luau",
		"midas_py_module_out_path": "path/to/script"
	},
	"state_tree": {
		"Duration": "integer",
		"IsStudio": "boolean",
		"Version": {
			"Build": "integer",
			"Major": "integer",
			"Minor": "integer",
			"Patch": "integer",
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

def remove_config():
	if os.path.exists(CONFIG_TOML_PATH):
		os.remove(CONFIG_TOML_PATH)

	if os.path.exists(AUTH_CONFIG_TOML_PATH):
		os.remove(AUTH_CONFIG_TOML_PATH)

def init_file():
	assert not os.path.exists(CONFIG_TOML_PATH), f"{CONFIG_TOML_PATH} file already exists, deleting it could break encoding"

	config_file = open(CONFIG_TOML_PATH, "w")
	config_file.write(yaml.safe_dump(DEFAULT_CONFIG_TEMPLATE))
	config_file.close()

	auth_file = open(AUTH_CONFIG_TOML_PATH, "w")
	auth_file.write(toml.dumps(DEFAULT_AUTH_CONFIG_TEMPLATE))
	auth_file.close()

	add_to_git_ignore(AUTH_CONFIG_TOML_PATH)

def get_midas_config() -> MidasConfig:
	if not os.path.exists(CONFIG_TOML_PATH):
		print("no midas.toml, have you initialized?")

	untyped_config: Any = yaml.safe_load(open(CONFIG_TOML_PATH, "r").read())
	midas_config: MidasConfig = untyped_config
	
	if midas_config["templates"]["chat"]:
		midas_config["state_tree"]["Chat"] = {
			"LastMessage": "string",
			"Count": "integer",
		}

	if midas_config["templates"]["character"]:
		midas_config["state_tree"]["Character"] = {
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
		midas_config["state_tree"]["Population"] = {
			"Total": "integer",
			"Team": "integer",
			"PeakFriends": "integer",
			"Friends": "integer",
			"SpeakingDistance": "integer",
		}

	if midas_config["templates"]["server_performance"]:
		if not "Performance" in midas_config["state_tree"]:
			midas_config["state_tree"]["Performance"] = {}

		midas_config["state_tree"]["Performance"]["Server"] = {
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
		midas_config["state_tree"]["Market"] = {
			"Spending": {
				"Gamepass": "integer",
				"Product": "integer",
				"Total": "integer",
			},
			"Gamepasses": {},
			"Purchase": {
				"Product": {
					"Name": [],
					"Price": "integer"
				},
				"Gamepass": {
					"Name": [],
					"Price": "integer"
				}
			},
		}
		for gamepass_name in midas_config["products"]["gamepasses"]:
			formatted_pass_name = re.sub(r'\s', '', gamepass_name)
			midas_config["state_tree"]["Market"]["Gamepasses"][formatted_pass_name] = "boolean"
			midas_config["state_tree"]["Market"]["Purchase"]["Gamepass"]["Name"].append(formatted_pass_name)

		for product_name in midas_config["products"]["developer_products"]:
			formatted_product_name = re.sub(r'\s', '', product_name)
			midas_config["state_tree"]["Market"]["Purchase"]["Product"]["Name"].append(formatted_product_name)

	if len(list(midas_config["templates"]["group"].keys())) > 0:
		midas_config["state_tree"]["Groups"] = {}
		for group_name, group_id in (midas_config["templates"]["group"]).items():
			formatted_group_name = re.sub(r'\s', '', group_name)
			midas_config["state_tree"]["Groups"][formatted_group_name] = "boolean"

	if midas_config["templates"]["demographics"]:
		midas_config["state_tree"]["Demographics"] = {
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
		if not "Performance" in midas_config["state_tree"]:
			midas_config["state_tree"]["Performance"] = {}

		midas_config["state_tree"]["Performance"]["Client"] = {
			"Ping": "integer",
			"FPS": "integer",
		}


	return midas_config

def get_auth_config() -> AuthConfig:
	if not os.path.exists(AUTH_CONFIG_TOML_PATH):
		print("no midas-auth.toml, have you initialized?")

	config: Any = toml.loads(open(AUTH_CONFIG_TOML_PATH, "r").read())
	return config

def set_auth_config(auth_config: AuthConfig):
	auth_file = open(AUTH_CONFIG_TOML_PATH, "w")
	auth_file.write(toml.dumps(auth_config))
	auth_file.close()

def set_config_by_console(config: dict[str, str]) -> dict[str, str]:
	for key in config:
		config[key] = input(f"{key}: ")
	return config