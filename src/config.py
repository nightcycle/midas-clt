import toml
import yaml
import os
import re
from typing import TypedDict, Literal, Union, Any
import keyring

TrackerType = Literal["boolean", "integer", "double", "float", "string"]

class VersionData(TypedDict):
	Build: TrackerType
	Major: TrackerType
	Minor: TrackerType
	Patch: TrackerType

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
	shared_event_tree_path: str
	client_boot_script_path: str

class RecorderTargetConfig(TypedDict):
	place_id: int
	group_id: int

class RecorderConfig(TypedDict):
	interval: int
	out_path: str
	branch: str
	id: RecorderTargetConfig

class TemplateConfig(TypedDict):
	chat: bool
	population: bool
	server_performance: bool
	market: bool
	character: bool
	demographics: bool
	client_performance: bool
	group: dict[str, int]

class VersionConfig(TypedDict):
	major: int
	minor: int
	patch: int
	hotfix: int | None

class MonetizationConfig(TypedDict):
	products: dict
	gamepasses: dict

class MidasConfig(TypedDict):
	version: VersionConfig
	recorder: RecorderConfig
	build: BuildConfig
	templates: TemplateConfig
	monetization: MonetizationConfig
	tree: Union[BaseStateTree, dict]

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

ENCODING_MARKER = "~"

CONFIG_TOML_PATH = "midas.yaml"

DEFAULT_CONFIG_TEMPLATE: MidasConfig = {
	"version": {
		"major": 1,
		"minor": 0,
		"patch": 0,
		"hotfix": 0,
	},
	"recorder": {
		"interval": 60,
		"out_path": "data",
		"branch": "midas-record-data",
		"id": {
			"place_id": 12345,
			"group_id": 67890,
		}
	},
	"templates": {
		"chat": False,
		"population": False,
		"server_performance": False,
		"market": False,
		"character": False,
		"demographics": False,
		"client_performance": False,
		"group": {},
	},
	"build": {
		"server_boot_script_path": "src/Server/Analytics.server.luau",
		"shared_state_tree_path": "src/Shared/MidasStateTree.luau",
		"shared_event_tree_path": "src/Shared/MidasEventTree.luau",
		"client_boot_script_path": "src/Client/Analytics.client.luau",
	},
	"monetization": {
		"products": {

		},
		"gamepasses": {

		}
	},
	"tree": {
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

def remove_config():
	if os.path.exists(CONFIG_TOML_PATH):
		os.remove(CONFIG_TOML_PATH)

def init_file():
	assert not os.path.exists(CONFIG_TOML_PATH), f"{CONFIG_TOML_PATH} file already exists, deleting it could break encoding"

	config_file = open(CONFIG_TOML_PATH, "w")
	config_file.write(yaml.safe_dump(DEFAULT_CONFIG_TEMPLATE))
	config_file.close()

def get_midas_config() -> MidasConfig:
	if not os.path.exists(CONFIG_TOML_PATH):
		print("no midas.toml, have you initialized?")

	untyped_config: Any = yaml.safe_load(open(CONFIG_TOML_PATH, "r").read())
	midas_config: Any = untyped_config
	
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

CREDENTIAL_USERNAME = os.path.abspath("") + "Midas"

def get_auth_config() -> AuthConfig:
	title_id = keyring.get_password("title_id", CREDENTIAL_USERNAME)
	dev_secret_key = keyring.get_password("dev_secret_key", CREDENTIAL_USERNAME)
	client_id = keyring.get_password("client_id", CREDENTIAL_USERNAME)
	client_secret = keyring.get_password("client_secret", CREDENTIAL_USERNAME)
	tenant_id = keyring.get_password("tenant_id", CREDENTIAL_USERNAME)
	cookie = keyring.get_password("cookie", CREDENTIAL_USERNAME)

	if not title_id:
		title_id = ""

	if not dev_secret_key:
		dev_secret_key = ""

	if not client_id:
		client_id = ""
		
	if not client_secret:
		client_secret = ""

	if not tenant_id:
		tenant_id = ""
		
	if not cookie:
		cookie = ""

	auth_config: AuthConfig = {
		"playfab": {
			"title_id": title_id,
			"dev_secret_key": dev_secret_key,
		},
		"aad": {
			"client_id": client_id,
			"client_secret": client_secret,
			"tenant_id": tenant_id,
		},
		"roblox": {
			"cookie": cookie,
		}
	}
	return auth_config
