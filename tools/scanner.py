"""
Tool scanner: discovers tool modules on disk, syncs config/tools.yaml,
and builds a populated ToolRegistry.

Convention: a tool module must expose:
  NAME        (str)  — unique tool identifier, must match a callable
  DESCRIPTION (str)  — human-readable description passed to the LLM
  SCHEMA      (dict) — JSON Schema for the tool's input parameters
  <NAME>      (fn)   — callable that implements the tool
"""
import importlib.util
import sys
from pathlib import Path

import yaml

from tools.registry import Tool, ToolRegistry

_CONFIG_PATH = Path("config/tools.yaml")
_DEFAULT_SCAN_PATHS = ["tools/builtin"]


# ── Config I/O ─────────────────────────────────────────────────────────────

def _load_config() -> dict:
    if not _CONFIG_PATH.exists():
        return {"scan_paths": list(_DEFAULT_SCAN_PATHS), "tools": {}}
    raw = yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8"))
    return raw if raw else {}


def _save_config(config: dict) -> None:
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CONFIG_PATH.write_text(
        yaml.dump(
            config,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


# ── File-level tool discovery ───────────────────────────────────────────────

class _DiscoveredTool:
    __slots__ = ("name", "description", "schema", "fn", "module_path")

    def __init__(self, name, description, schema, fn, module_path):
        self.name = name
        self.description = description
        self.schema = schema
        self.fn = fn
        self.module_path = module_path


def _to_module_path(file: Path, root: Path) -> str:
    return (
        str(file.relative_to(root).with_suffix(""))
        .replace("\\", "/")
        .replace("/", ".")
    )


def _scan_directory(directory: Path, root: Path) -> list[_DiscoveredTool]:
    if not directory.exists():
        return []
    found = []
    for file in sorted(directory.glob("*.py")):
        if file.name.startswith("_"):
            continue
        mod_path = _to_module_path(file, root)
        try:
            if mod_path in sys.modules:
                mod = sys.modules[mod_path]
            else:
                spec = importlib.util.spec_from_file_location(mod_path, file)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[mod_path] = mod
                spec.loader.exec_module(mod)
        except Exception:
            continue

        name = getattr(mod, "NAME", None)
        description = getattr(mod, "DESCRIPTION", None)
        schema = getattr(mod, "SCHEMA", None)
        if not (name and description and schema):
            continue
        fn = getattr(mod, name, None)
        if not callable(fn):
            continue
        found.append(_DiscoveredTool(name, description, schema, fn, mod_path))
    return found


# ── Public API ──────────────────────────────────────────────────────────────

def sync_and_build(project_root: Path | None = None) -> ToolRegistry:
    """
    Scan all directories listed under scan_paths in config/tools.yaml,
    sync the config (add new tools, remove missing ones, preserve enabled
    state), save the config, and return a ToolRegistry with all enabled tools.

    Creates config/tools.yaml automatically on first run.
    """
    root = project_root or Path.cwd()
    config = _load_config()
    scan_paths: list[str] = config.get("scan_paths", list(_DEFAULT_SCAN_PATHS))
    tools_cfg: dict = config.get("tools", {})

    # Discover all tools from all scan paths
    discovered: dict[str, _DiscoveredTool] = {}
    for path_str in scan_paths:
        for dt in _scan_directory(root / path_str, root):
            discovered[dt.name] = dt

    # Remove tools no longer present on disk
    for name in [n for n in list(tools_cfg) if n not in discovered]:
        del tools_cfg[name]

    # Add newly found tools (enabled by default); refresh module path
    for name, dt in discovered.items():
        if name not in tools_cfg:
            tools_cfg[name] = {"module": dt.module_path, "enabled": True}
        else:
            tools_cfg[name]["module"] = dt.module_path

    config["tools"] = tools_cfg
    _save_config(config)

    # Build registry with enabled tools only
    registry = ToolRegistry()
    for name, entry in tools_cfg.items():
        if not entry.get("enabled", True):
            continue
        dt = discovered[name]
        registry.register(Tool(
            name=dt.name,
            description=dt.description,
            params=dt.schema,
            fn=dt.fn,
        ))
    return registry


def list_tools() -> list[dict]:
    """
    Return all known tools (enabled and disabled) from config/tools.yaml.
    Each entry: {"name": str, "enabled": bool, "module": str}.
    """
    config = _load_config()
    return [
        {
            "name": name,
            "enabled": entry.get("enabled", True),
            "module": entry.get("module", ""),
        }
        for name, entry in config.get("tools", {}).items()
    ]


def set_tool_enabled(name: str, enabled: bool) -> bool:
    """
    Enable or disable a named tool in config/tools.yaml.
    Returns True if the tool was found, False otherwise.
    Call sync_and_build() afterwards to apply the change to a live registry.
    """
    config = _load_config()
    tools_cfg = config.get("tools", {})
    if name not in tools_cfg:
        return False
    tools_cfg[name]["enabled"] = enabled
    config["tools"] = tools_cfg
    _save_config(config)
    return True
