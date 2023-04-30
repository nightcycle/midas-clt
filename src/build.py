import src.config as config
import src.treecode as treecode
import luau
import dpath
import sys
import os
from luau import import_type, indent_block
from luau.convert import from_any, mark_as_literal
from luau.roblox import write_script, get_package_require, get_module_require
from luau.path import remove_all_path_variants, get_if_module_script, get_if_using_lua_or_luau_ext
from luau.roblox.rojo import get_roblox_path_from_env_path
from typing import TypedDict, Literal, Union, Any

GENERATED_HEADER_WARNING_COMMENT = "-- this script was generated by nightcycle/midas-clt, do not manually edit"

def get_package_zip_path() -> str:
	base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
	print(base_path)
	for sub_path in os.listdir(base_path):
		print(sub_path)

	return os.path.join(base_path, "data\\Packages.zip")

def get_midas_require_path():
	midas_config = config.get_midas_config()
	midas_package_path = os.path.splitext(midas_config["build"]["shared_state_tree_path"])[0] + "/Packages/MidasAnalytics.lua"
	rbx_midas_package_path = get_roblox_path_from_env_path(midas_package_path)
	return get_module_require(rbx_midas_package_path)

def build_shared_luau_tree():

	midas_config = config.get_midas_config()
	build_path = midas_config["build"]["shared_state_tree_path"]

	remove_all_path_variants(build_path)

	tree_paths = {}
	literals = {}

	for path, value in dpath.search(midas_config["state_tree"], '**', yielded=True):
		path_keys = path.split("/")
		has_num_key = False
		for key in path_keys:
			try:
				int(key)
				has_num_key = True
			except:
				has_num_key = False
		if not has_num_key:
			if type(value) == list:
				literal_type_name = path.replace("/", "") + "Type"
				literals[literal_type_name] = ""
				for v in value:
					if v != "nil":
						literals[literal_type_name] += from_any(v) + " | "
				literals[literal_type_name] = literals[literal_type_name][0:(len(literals[literal_type_name])-3)]	
				tree_paths[path] = literal_type_name
			elif not isinstance(value, dict):
				tree_paths[path] = value

	contents = [
		"--!strict",
		GENERATED_HEADER_WARNING_COMMENT,	
		"\n-- Packages",
		"local Midas = " + get_midas_require_path(),
		"\n-- Types",
		"export type TrackerAccessNode<T> = (player: Player, solver: () -> T) -> nil",
	]

	for type_name, type_def in literals.items():
		contents.append(f"export type {type_name} = {type_def}")

	tree_data = {}
	for tree_path, tree_type in tree_paths.items():
		base_type = tree_type
		end_marker = ""
		if base_type[len(base_type)-1] == "?":
			base_type = base_type[0:(len(base_type)-1)]
			end_marker = "?"
		if base_type == "string" or base_type == "boolean":
			dpath.new(tree_data, tree_path, mark_as_literal(f"constructTracker(\"{tree_path}\", nil) :: TrackerAccessNode<{tree_type}>"))
		elif base_type == "integer":
			dpath.new(tree_data, tree_path, mark_as_literal(f"constructTracker(\"{tree_path}\", 0) :: TrackerAccessNode<number{end_marker}>"))
		elif base_type == "double":
			dpath.new(tree_data, tree_path, mark_as_literal(f"constructTracker(\"{tree_path}\", 2) :: TrackerAccessNode<number{end_marker}>"))
		elif base_type == "float":
			dpath.new(tree_data, tree_path, mark_as_literal(f"constructTracker(\"{tree_path}\", nil) :: TrackerAccessNode<number{end_marker}>"))	
		elif base_type in literals:
			dpath.new(tree_data, tree_path, mark_as_literal(f"constructTracker(\"{tree_path}\", nil) :: TrackerAccessNode<{tree_type}>"))
		else:
			dpath.new(tree_data, tree_path, mark_as_literal(f"constructTracker(\"{tree_path}\", nil) :: TrackerAccessNode<any{end_marker}>"))		
	
	contents += [
		"\n-- Class",
		"function constructTracker<T>(path: string, decimalCount: number?): TrackerAccessNode<T>",
		] + indent_block([
			"return function(player: Player, solver: () -> T)",
			] + indent_block([
				"local keys: {[number]: string} = path:split(\"/\")",
				"local propertyName = keys[#keys]",
				"table.remove(keys, #keys)",
				"local basePath = table.concat(keys, \"/\")",
				f"local tracker = Midas:GetTracker(player, basePath)",
				"tracker:SetState(propertyName, solver)",
				"if decimalCount then",
				"\ttracker:SetRoundingPrecision(decimalCount)",
				"end",
				"return nil",
			], 2) + [
			"end",
		]) + [		
		"end",
		f"\nreturn {from_any(tree_data, indent_count=0, add_comma_at_end=False, multi_line=True, skip_initial_indent=True)}"
	]

	write_script(build_path, "\n".join(contents), packages_dir_zip_file_path=get_package_zip_path())


def build_client_boot():
	midas_config = config.get_midas_config()
	build_path = midas_config["build"]["client_boot_script_path"]

	remove_all_path_variants(build_path, "client")
	contents = [
		"--!strict",
		GENERATED_HEADER_WARNING_COMMENT,	
	]

	init_function_content = indent_block([
		"\n -- needs to be required on client to set up remote event listeners",
		"local _Midas = " + get_midas_require_path(),
		"return nil"
	], 1)


	if get_if_module_script(build_path):
		script_name = build_path.split("/")[len(build_path.split("/"))-1]
		if get_if_using_lua_or_luau_ext(build_path) == "luau":
			script_name = script_name.replace(".luau", "")
		else:
			script_name = script_name.replace(".lua", "")

		
		contents += [
			"\n-- packages",
			"local Maid = " + get_package_require("Maid"),
			"type Maid = Maid.Maid",
			"\nlocal " + script_name + " = {}",
			f"\nfunction {script_name}.init(maid: Maid): nil",
		] + init_function_content + [	
			f"end"
			f"\nreturn {script_name}"
		]
	else:
		contents += [
			f"function init(): nil",
		] + init_function_content + [
			f"end",
			f"init()"
		]

	write_script(build_path, "\n".join(contents), packages_dir_zip_file_path=get_package_zip_path())

def build_server_boot():
	auth_config = config.get_auth_config()
	midas_config = config.get_midas_config()
	encoding_config = treecode.get_tree_encoding()

	build_path = midas_config["build"]["server_boot_script_path"]
	remove_all_path_variants(build_path, "server")
	
	title_id = auth_config["playfab"]["title_id"]
	dev_secret_key = auth_config["playfab"]["dev_secret_key"]

	config_table = {
		"Version": {
			"Major": midas_config["version"]["major"],
			"Minor": midas_config["version"]["minor"],
			"Patch": midas_config["version"]["patch"],
		},
		"Encoding": {
			"Marker": encoding_config["marker"],
			"Dictionary": {
				"Properties": encoding_config["dictionary"]["properties"],
				"Values": encoding_config["dictionary"]["values"]
			},
			"Arrays": encoding_config["arrays"]
		},
		"SendDeltaState": False,
		"PrintLog": False,
		"SendDataToPlayFab": True,
		"Templates": {
			"Join": midas_config["templates"]["join"],
			"Chat": midas_config["templates"]["chat"],
			"Population": midas_config["templates"]["population"],
			"ServerPerformance": midas_config["templates"]["server_performance"],
			"Market": midas_config["templates"]["market"],
			"Exit": midas_config["templates"]["exit"],
			"Character": midas_config["templates"]["character"],
			"Player": midas_config["templates"]["player"],
			"Demographics": midas_config["templates"]["demographics"],
			"ClientPerformance": midas_config["templates"]["client_performance"],
			"Group": midas_config["templates"]["group"],
		},
	}

	if "hotfix" in midas_config["version"]:
		config_table["Version"]["hotfix"] = midas_config["version"]["hotfix"]
	
	contents = [
		"--!strict",
		GENERATED_HEADER_WARNING_COMMENT,
		"\n-- packages",
		"local Maid = " + get_package_require("Maid"),
		"local Midas = " + get_midas_require_path(),
		"\ntype Maid = Maid.Maid",
	]

	config_text = f"-- configure package \nMidas:Configure({from_any(config_table, indent_count=1, skip_initial_indent=True, add_comma_at_end=False, multi_line=True)})"
	init_text = f"-- initialize playfab http request variables \nMidas.init(\"{title_id}\", \"{dev_secret_key}\")"

	init_function_content = indent_block([
		f"\n{config_text}",
		f"\n{init_text}",
		f"\nmaid:GiveTask(Midas)",
		f"\nreturn nil",
	])
	
	if get_if_module_script(build_path):
		script_name = build_path.split("/")[len(build_path.split("/"))-1]
		if get_if_using_lua_or_luau_ext(build_path) == "luau":
			script_name = script_name.replace(".luau", "")
		else:
			script_name = script_name.replace(".lua", "")

		contents += [
			"\nlocal "+script_name+" = {}"
			f"\n\nfunction {script_name}.init(maid: Maid): nil",
		] + init_function_content + [
			f"end"
			f"\nreturn {script_name}"
		]
	else:
		contents += [
			f"\nfunction init(maid: Maid): nil",
		] + init_function_content + [
			f"end",
			f"\nlocal maid = Maid.new()",
			f"maid:GiveTask(script.Destroying:Connect(function() maid:Destroy() end))",
			f"init(maid)"
		]

	write_script(build_path, "\n".join(contents), packages_dir_zip_file_path=get_package_zip_path())

def main():
	build_shared_luau_tree()
	build_client_boot()
	build_server_boot()