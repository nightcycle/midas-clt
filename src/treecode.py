
import copy
import math
import json
import dpath
import os
import src.config as config
from src.config import TrackerType
from typing import TypedDict, Literal, Union, Any

ENCODING_MARKER = config.ENCODING_MARKER
TREE_ENCODING_PATH = "midas.cache"
ASCII_FLOOR = 33
ASCII_CEILING = 91
BAD_ASCII_CHARACTERS = [":", "\"", "\\", "%", "'", "`", "*", ".", "$", "^", "(", ")", "[", "]", "+", "-", "?"]

class EncodingDictionary(TypedDict):
	properties: dict[str, str]
	values: dict

class EncodingTree(TypedDict):
	marker: str
	patterns: list[str]
	dictionary: EncodingDictionary
	arrays: dict

def get_code(index: int, marker: str) -> str:
	ascii_codes = []

	for i in range(ASCII_FLOOR, ASCII_CEILING):
		char = chr(i)

		if not char in BAD_ASCII_CHARACTERS and char != marker:
			ascii_codes.append(char)

	code_count = len(ascii_codes)
	max_val = code_count-1

	def read_char(index: int) -> str:
		return ascii_codes[index]

	def get_char(relative_index: int, code=f"") -> str:
		unrounded_exponent = math.log(relative_index, max_val)
		exponent = math.floor(unrounded_exponent)

		if unrounded_exponent <= 1:

			return code + read_char(relative_index)
		else:

			increment = math.pow(max_val, exponent)
			leading_value = math.floor(relative_index/increment)
			foundation = leading_value*increment
			remainder = int(relative_index-foundation)
			code += read_char(leading_value)

			if remainder == 0:

				for i in range(0, exponent):
					code += read_char(0)
				return code
			else:	

				return get_char(remainder, code)

	return marker+get_char(index)

def set_tree_encoding():
	midas_config = config.get_midas_config()
	tree_structure = midas_config["tree"]

	# read prior tree
	old_patterns: list[str] = []
	old_binary_paths: dict[str, list[str]] = {}

	if os.path.exists(TREE_ENCODING_PATH):
		encoding_tree: Any = json.loads(open(TREE_ENCODING_PATH, "r").read())
		assert encoding_tree["marker"] == ENCODING_MARKER, "markers are mismatched"
		old_patterns = encoding_tree["patterns"]
		for path, value in dpath.search(encoding_tree["arrays"], '**', yielded=True):
			if type(value) == list:
				old_binary_paths[path] = copy.deepcopy(value)

	# list of paths with an encodable property at the end
	property_paths = []

	# a list of new strings that should have codes
	new_patterns: list[str] = []

	# a list of possible values for specific paths
	value_variants: dict[str, list[str]] = {}

	# a list of boolean dictionaries that can be encoded as binary strings
	binary_arrays: dict[str, list[str]] = {}

	# read tree to fill in above values
	for path, value in dpath.search(tree_structure, '**', yielded=True):
		# filter out list paths
		path_keys = path.split("/")
		is_num = False
		for key in path_keys:
			final_key = path_keys[len(path_keys)-1]
			try:
				int(final_key)
				is_num = True
			except:
				is_num = False

		# add pattern
		if not is_num and  type(value) == str or type(value) == list:
			property_paths.append(path)

			if type(value) == list:
				value_variants[path] = []
				for v in value:
					if not v in old_patterns:
						new_patterns.append(v)
					value_variants[path].append(v)

		elif type(value) == dict:
			property_paths.append(path)
			is_all_boolean = True
			for k, v in value.items():
				if v != "boolean":
					is_all_boolean = False
			
			if is_all_boolean:
				current_values = list(value.keys())
				if path in old_binary_paths:
					for i, v in enumerate(current_values):
						if len(old_binary_paths[path])-1 >= i:
							old_v = old_binary_paths[path][i]
							assert old_v == v, f"binary sequence is desynced at entry {i} at {path}"		

					assert len(current_values) >= len(old_binary_paths[path]), f"new binary sequence at {path} is shorter, don't do this"

				binary_arrays[path] = current_values

	keys: list[str] = []

	for path in property_paths:
		for key in path.split("/"):
			keys.append(key)
			if not key in old_patterns:
				new_patterns.append(key)

	keys = list(set(keys))
	new_patterns = list(set(new_patterns))
	patterns = copy.deepcopy(old_patterns)
	for new_pattern in new_patterns:
		patterns.append(new_pattern)


	pattern_codes = {}
	for i, pattern in enumerate(patterns):
		pattern_codes[pattern] = get_code(i+1, ENCODING_MARKER)

	# print("pattern_codes", json.dumps(pattern_codes,indent=5))

	property_dict = {}
	for key in keys:
		property_dict[key] = pattern_codes[key]

	value_registry = {}
	for path, value_list in value_variants.items():
		val_entries = {}
		for val in value_list:
			val_entries[val] = pattern_codes[val]

		dpath.new(value_registry, path, val_entries)

	array_registry = {}
	for path, array in binary_arrays.items():
		dpath.new(array_registry, path, array)

	# assemble starting encoding tree
	encoding_tree: EncodingTree = {
		"marker": ENCODING_MARKER,
		"patterns": patterns,
		"dictionary": {
			"properties": property_dict,
			"values": value_registry
		},
		"arrays": array_registry
	}
	# print("encoding_tree", json.dumps(encoding_tree,indent=5))

	encoding_file = open(TREE_ENCODING_PATH, "w")
	encoding_file.write(json.dumps(encoding_tree, indent=4))
	encoding_file.close()

def get_tree_encoding() -> dict:
	encoding_file = open(TREE_ENCODING_PATH, "r")
	config = json.loads(encoding_file.read())
	return config
