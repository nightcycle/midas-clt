import toml
import yaml
import json
import os
import re
from typing import TypedDict, Literal, Union, Optional, Any
import keyring
from copy import deepcopy
import dpath
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
	midas_package_rbx_path: str
	server_boot_script_path: str
	shared_state_tree_path: str
	shared_event_tree_path: str
	client_boot_script_path: str

class RecorderTargetConfig(TypedDict):
	place_id: int
	group_id: int


class VersionConfig(TypedDict):
	major: int
	minor: int
	patch: int
	hotfix: int | None

class MonetizationConfig(TypedDict):
	products: dict
	gamepasses: dict

class TemplateConfig(TypedDict):
	State: dict
	Event: dict

class MidasConfig(TypedDict):
	version: VersionConfig
	build: BuildConfig
	template: TemplateConfig
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

TEMPLATE_STATE_TYPE_TREE = {
	"Chat": {
		"LastMessage": "string",
		"Count": "integer",
	},
	"Character": {
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
	},
	"Population": {
		"Total": "integer",
		"Team": "integer",
		"PeakFriends": "integer",
		"Friends": "integer",
		"SpeakingDistance": "integer",
	},
	"Performance": {
		"Client": {
			"Ping": "integer",
			"FPS": "integer",
		},
		"Server": {
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
	},
	"Spending": {
		"Spending": {
			"Product": "integer",
			"Gamepass": "integer",
			"Total": "integer",
		},
		"Gamepasses": {},		
		"Purchase": {
			"Product": {
				"Name": ["dev_product_name_1", "dev_product_name_2"],
				"Price": "integer"
			},
			"Gamepass": {
				"Name": ["gamepass_name_1", "gamepass_name_2"],
				"Price": "integer"
			}
		},
	},

	"Groups": {},
	"Badges": {},
	"Demographics": {
		"AccountAge": "integer",
		"RobloxLanguage": [
			"en-us",
			"pt-br",
			"en-uk",
		],
		"SystemLanguage": [
			"en-us",
			"pt-br",
			"en-uk",
		],
		"UserSettings": {
			"GamepadCameraSensitivity": "double",
			"MouseSensitivity": "double",
			"SavedQualityLevel": "integer",
		},
		"Platform": {
			"Accelerometer": "boolean",
			"Gamepad": "boolean",
			"Gyroscope": "boolean",
			"Keyboard": "boolean",
			"Mouse": "boolean",
			"Touch": "boolean",
			"VR": "boolean",
			"ScreenSize": "integer",
			"ScreenRatio": ["16:10","16:9","5:4","5:3","3:2","4:3","9:16","uncommon"],
		},
	},
}

DEFAULT_CONFIG_TEMPLATE: MidasConfig = {
	"version": {
		"major": 1,
		"minor": 0,
		"patch": 0,
		"hotfix": 0,
	},
	"template": {
		"State": {
			"Chat": {
				"LastMessage": False,
				"Count": False,
			},
			"Character": {
				"IsDead": False,
				"Height": False,
				"Mass": False,
				"State": False,
				"WalkSpeed": False,
				"Position": False,
				"Altitude": False,
				"JumpPower": False,
				"Health": False,
				"MaxHealth": False,
				"Deaths": False,
			},
			"Population": {
				"Total": False,
				"Team": False,
				"PeakFriends": False,
				"Friends": False,
				"SpeakingDistance": False,
			},
			"Performance": {
				"Client": {
					"Ping": False,
					"FPS": False,
				},
				"Server": {
					"EventsPerMinute": False,
					"Ping": False,
					"ServerTime": False,
					"HeartRate": False,
					"Instances": False,
					"MovingParts": False,
					"Network": {
						"Data": {
							"Send": False,
							"Receive": False,
						},
						"Physics": {
							"Send": False,
							"Receive": False,
						},
					},
					"Memory": {
						"Internal": False,
						"HttpCache": False,
						"Instances": False,
						"Signals": False,
						"LuaHeap": False,
						"Script": False,
						"PhysicsCollision": False,
						"PhysicsParts": False,
						"CSG": False,
						"Particle": False,
						"Part": False,
						"MeshPart": False,
						"SpatialHash": False,
						"TerrainGraphics": False,
						"Textures": False,
						"CharacterTextures": False,
						"SoundsData": False,
						"SoundsStreaming": False,
						"TerrainVoxels": False,
						"Guis": False,
						"Animations": False,
						"Pathfinding": False,
					},
				},
			},
			"Spending": {
				"Product": False,
				"Gamepass": False,
				"Total": False,
			},
			"Groups": {},
			"Badges": {},
			"Demographics": {
				"AccountAge": False,
				"RobloxLanguage": False,
				"SystemLanguage": False,
				"UserSettings": {
					"GamepadCameraSensitivity": False,
					"MouseSensitivity": False,
					"SavedQualityLevel": False,
				},
				"Platform": {
					"Accelerometer": False,
					"Gamepad": False,
					"Gyroscope": False,
					"Keyboard": False,
					"Mouse": False,
					"Touch": False,
					"VR": False,
					"ScreenSize": False,
					"ScreenRatio": False,
				},
			},
		},
		"Event": {
			"Interval": 15,
			"Join": {
				"Teleport": False,
				"Enter": False,
			},
			"Chat": {
				"Spoke": False,
			},
			"Character": {
				"Died": False,
			},
			"Spending": {
				"Purchase": {
					"Product": False,
					"Gamepass": False,
				},
			},
			"Exit": {
				"Quit": False,
				"Disconnect": False,
				"Close": False,
			},
		},
	},
	"build": {
		"midas_package_rbx_path": "game/ReplicatedStorage/Packages/Midas",
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

	for path, value in dpath.search(TEMPLATE_STATE_TYPE_TREE, '**', yielded=True):
		status = dpath.get(midas_config["template"]["State"], path, default=None)
		if status == None:
			status = dpath.get(midas_config["template"]["Event"], path, default=None)
		if (type(status) == bool and status == True) or type(status) == int:
			dpath.new(midas_config["tree"], path, value)
	
	for gamepass_name in midas_config["monetization"]["gamepasses"]:
		formatted_pass_name = re.sub(r'\s', '', gamepass_name)
		midas_config["tree"]["Spending"]["Gamepasses"][formatted_pass_name] = "boolean"
		midas_config["tree"]["Spending"]["Purchase"]["Gamepass"]["Name"].append(formatted_pass_name)

	for product_name in midas_config["monetization"]["products"]:
		formatted_product_name = re.sub(r'\s', '', product_name)
		midas_config["tree"]["Spending"]["Purchase"]["Product"]["Name"].append(formatted_product_name)

	if len(list(midas_config["template"]["State"]["Groups"].keys())) > 0:
		midas_config["tree"]["Groups"] = {}
		for group_name, group_id in (midas_config["template"]["State"]["Groups"]).items():
			formatted_group_name = re.sub(r'\s', '', group_name)
			midas_config["tree"]["Groups"][formatted_group_name] = "integer"

	if len(list(midas_config["template"]["State"]["Badges"].keys())) > 0:
		midas_config["tree"]["Badges"] = {}
		for badge_name, group_id in (midas_config["template"]["State"]["Badges"]).items():
			formatted_badge_name = re.sub(r'\s', '', badge_name)
			midas_config["tree"]["Badges"][formatted_badge_name] = "boolean"

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
