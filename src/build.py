import config
import luau
from typing import TypedDict, Literal, Union, Any

def snake_case_to_pascal_case(snake_case_str: str) -> str:
    # Split the snake_case string by underscore
    words = snake_case_str.split('_')
    # Convert each word to title case (first letter uppercase, others lowercase)
    # and join them together to form the PascalCase string
    pascal_case_str = ''.join(word.title() for word in words)
    return pascal_case_str

def build_python_script():
	print("build_python_script")

def build_shared_luau_tree():
	print("build_shared_luau_tree")	

def build_client_boot():
	print("build_client_boot")	

def build_server_boot():
	auth_config = config.get_auth_config()
	midas_config = config.get_midas_config()

	midas_config[""]

	title_id = auth_config["playfab"]["title_id"]
	dev_secret_key = auth_config["playfab"]["dev_secret_key"]

	contents = [
		"--!strict"
		"local MidasAnalytics = require(game:GetService(\"ReplicatedStorage\"):WaitForChild(\"Packages\"):WaitForChild(\"MidasAnalytics\"))"
		"function init()",
		f"\tAnalytics.init(\"{title_id}\", \"{dev_secret_key}\")",
		"end",
		"",
		"init()"
	]

	content_str = "".join(contents)

def main():
	build_shared_luau_tree()
	build_python_script()
	build_client_boot()
	# build_server_boot()