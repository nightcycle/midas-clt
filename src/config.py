import toml
import os
from typing import TypedDict

class MidasConfig(TypedDict):
	out_path: str

class AuthConfig(TypedDict):
	secret_key: str

CONFIG_TOML_PATH = "midas.toml"
AUTH_CONFIG_TOML_PATH = "midas-auth.toml"
DEFAULT_CONFIG_TEMPLATE: MidasConfig = {
	"out_path": ""
}
DEFAULT_AUTH_CONFIG_TEMPLATE: AuthConfig = {
	"secret_key": ""
}

def init_file():
	print("init file")
	assert not os.path.exists(CONFIG_TOML_PATH), f"{CONFIG_TOML_PATH} file already exists, deleting it could break encoding"

	file = open(CONFIG_TOML_PATH, "w")
	file.write(toml.dumps(DEFAULT_CONFIG_TEMPLATE))
	file.close()

	auth_file = open(AUTH_CONFIG_TOML_PATH, "w")
	auth_file.write(toml.dumps(DEFAULT_AUTH_CONFIG_TEMPLATE))
	auth_file.close()

def get_midas_config() -> MidasConfig:
	config = toml.load(open(CONFIG_TOML_PATH, "r").read())
	return config

def get_auth_config() -> AuthConfig:
	config = toml.load(open(AUTH_CONFIG_TOML_PATH, "r").read())
	return config
