from _typeshed import Incomplete
from typing import TypedDict, Union

TrackerType: Incomplete

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

def add_to_git_ignore(path: str, git_ignore_path: str = ...): ...

CONFIG_TOML_PATH: str
AUTH_CONFIG_TOML_PATH: str
DEFAULT_CONFIG_TEMPLATE: MidasConfig
DEFAULT_AUTH_CONFIG_TEMPLATE: AuthConfig

def remove_config() -> None: ...
def init_file() -> None: ...
def get_midas_config() -> MidasConfig: ...
def get_auth_config() -> AuthConfig: ...
def set_auth_config(auth_config: AuthConfig): ...
def set_config_by_console(config: dict[str, str]) -> dict[str, str]: ...
