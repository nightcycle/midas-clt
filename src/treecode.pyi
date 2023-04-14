from _typeshed import Incomplete
from config import TrackerType as TrackerType
from typing import TypedDict

TREE_ENCODING_PATH: str
ASCII_FLOOR: int
ASCII_CEILING: int
BAD_ASCII_CHARACTERS: Incomplete

class EncodingDictionary(TypedDict):
    properties: dict[str, str]
    values: dict

class EncodingTree(TypedDict):
    marker: str
    patterns: list[str]
    dictionary: EncodingDictionary
    arrays: dict

def get_code(index: int, marker: str) -> str: ...
def set_tree_encoding() -> None: ...
def get_tree_encoding() -> dict: ...
