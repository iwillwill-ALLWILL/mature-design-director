#!/usr/bin/env python3
"""Validate the portable mature-design-director contracts without cataloguing capabilities in code."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import stat
import unicodedata
import zipfile
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
REGISTRY = ROOT / "references" / "capability-registry.json"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REPOSITORY_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
TOP_LEVEL_FRONTMATTER = {
    "name", "description", "version", "author", "license", "platforms", "metadata",
}
HERMES_FRONTMATTER = {"tags", "related_skills"}
CATALOG_FIELDS = {
    "name", "layer", "layer_family", "tags", "repository", "official_url",
    "license_hint", "accepted_spdx", "manual_license_review", "license_source_url",
    "license_verified_at", "best_for", "risk", "last_verified", "repository_provider",
}
CATALOG_OPTIONAL_FIELDS = {"repository_provider"}
REPOSITORY_PROVIDERS = {"github", "gitlab"}
REGISTRY_FIELDS = {
    "schema_version", "skill", "authority", "layer_contract", "artifact_lifecycle",
    "flow", "evidence_types", "capabilities", "ecosystem", "resources", "learning",
}
CAPABILITY_FIELDS = {"id", "contract", "accepts", "outputs", "foundations", "delegates", "evidence"}
ARTIFACT_RECORD_FIELDS = {
    "schema_version", "registry_schema_version", "registry_sha256", "artifact_id", "capability_id", "producer",
    "creative_authority", "artifact_state", "final_audience", "requester_reviewer",
    "native_medium", "primary_artifact", "creative_foundations", "assembly_mechanics", "evidence",
    "state_history", "delegations", "rejection_reason",
}
NATIVE_MEDIUM_FIELDS = {"requested", "actual", "classification", "output_class"}
OUTPUT_CONTRACT_FIELDS = {
    "id", "requires_foundations", "requires_delegates", "allowed_classifications", "artifact_suffixes",
}
PRIMARY_ARTIFACT_FIELDS = {"ref", "sha256"}
RECORD_FOUNDATION_FIELDS = {"role", "source_class", "source", "evidence"}
RECORD_MECHANICS_FIELDS = {"role", "candidate", "tool", "evidence"}
EVIDENCE_ITEM_FIELDS = {"ref", "sha256", "subject_sha256", "description", "reviewer", "benchmarks"}
STATE_HISTORY_FIELDS = {"state", "evidence"}
RECORD_DELEGATION_FIELDS = {
    "task_id", "status", "artifact_ref", "artifact_sha256", "accepted_by", "acceptance_evidence",
}
PORTABLE_SUPPORT_DIRS = ("references", "templates", "scripts", "maintenance")
PORTABLE_SUPPORT_REF = re.compile(
    r"`((?:references|templates|scripts|maintenance)/[^`\s]+)`"
)


def _atom(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("empty scalar")
    if value[0] in "\"'" or value[-1] in "\"'":
        if len(value) < 2 or value[0] != value[-1] or value[0] not in "\"'":
            raise ValueError("unterminated or mismatched quoted scalar")
        if value[0] == '"':
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError("invalid double-quoted scalar") from exc
            if not isinstance(parsed, str):
                raise ValueError("quoted scalar must decode to a string")
            return parsed
        inner = value[1:-1]
        if "'" in inner:
            raise ValueError("single-quoted scalar escapes are unsupported")
        return inner
    if value.startswith(("|", ">", "{", "&", "*", "!")):
        raise ValueError("unsupported YAML construct in strict frontmatter subset")
    return value


def _scalar(value: str):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [] if not inner else [_atom(part) for part in inner.split(",")]
    if value.startswith("[") or value.endswith("]"):
        raise ValueError("unterminated inline list")
    if value in {"true", "false"}:
        return value == "true"
    return _atom(value)


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        raise ValueError("frontmatter must start at byte 0")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("frontmatter is not closed")
    root: dict = {}
    stack = [(-1, root)]
    for lineno, raw in enumerate(text[4:end].splitlines(), start=2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw:
            raise ValueError(f"frontmatter line {lineno} contains a tab")
        indent = len(raw) - len(raw.lstrip(" "))
        if indent % 2:
            raise ValueError(f"frontmatter line {lineno} has invalid indentation")
        body = raw.strip()
        if ":" not in body:
            raise ValueError(f"frontmatter line {lineno} has no key separator")
        key, value = (part.strip() for part in body.split(":", 1))
        if not KEY.fullmatch(key):
            raise ValueError(f"frontmatter line {lineno} has an invalid key")
        while stack[-1][0] >= indent:
            stack.pop()
        expected_indent = 0 if stack[-1][0] == -1 else stack[-1][0] + 2
        if indent != expected_indent:
            raise ValueError(f"frontmatter line {lineno} jumps or attaches to a scalar")
        parent = stack[-1][1]
        if key in parent:
            raise ValueError(f"frontmatter line {lineno} duplicates {key}")
        if value:
            parent[key] = _scalar(value)
        else:
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
    return root


def validate_frontmatter(data: dict) -> None:
    missing = sorted(TOP_LEVEL_FRONTMATTER - set(data))
    unknown = sorted(set(data) - TOP_LEVEL_FRONTMATTER)
    if missing or unknown:
        raise ValueError(f"frontmatter fields missing={missing} unknown={unknown}")
    if data["name"] != "mature-design-director":
        raise ValueError("frontmatter name must equal mature-design-director")
    description = data["description"]
    if not isinstance(description, str) or not description.startswith("Use when ") or len(description) > 1024:
        raise ValueError("description must be a <=1024 character 'Use when ...' trigger")
    if not isinstance(data["version"], str) or not SEMVER.fullmatch(data["version"]):
        raise ValueError("version must be semantic x.y.z")
    if not all(isinstance(data[key], str) and data[key].strip() for key in ("author", "license")):
        raise ValueError("author and license must be non-empty strings")
    platforms = data["platforms"]
    if not _unique_strings(platforms, slugged=True):
        raise ValueError("platforms must be a non-empty unique slug list")
    metadata = data["metadata"]
    if not isinstance(metadata, dict) or set(metadata) != {"hermes"}:
        raise ValueError("metadata must contain only the hermes mapping")
    hermes = metadata["hermes"]
    if not isinstance(hermes, dict) or set(hermes) != HERMES_FRONTMATTER:
        raise ValueError("metadata.hermes must contain only tags and related_skills")
    for key in HERMES_FRONTMATTER:
        if not _unique_strings(hermes[key], slugged=True):
            raise ValueError(f"metadata.hermes.{key} must be a non-empty unique slug list")


def _unique_strings(value: object, *, slugged: bool = False, allow_empty: bool = False) -> bool:
    if not isinstance(value, list) or (not allow_empty and not value):
        return False
    if not all(isinstance(item, str) and item.strip() for item in value):
        return False
    normalized = [item.strip() for item in value]
    return len(normalized) == len(set(normalized)) and all(
        not slugged or SLUG.fullmatch(item) for item in normalized
    )


def _normalized_identity(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", unicodedata.normalize("NFKC", value))
    visible = "".join(
        character
        for character in normalized
        if not unicodedata.category(character).startswith(("C", "M"))
    )
    return " ".join(visible.split()).casefold()


def _reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonstandard_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant is forbidden: {value}")


def loads_json_strict(text: str) -> Any:
    try:
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=_reject_nonstandard_json_constant,
        )
    except RecursionError as exc:
        raise ValueError("JSON nesting exceeds the validation limit") from exc


def load_json_strict(path: Path) -> Any:
    return loads_json_strict(path.read_text(encoding="utf-8"))


def _file(root: Path, value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value.startswith("/"):
        raise ValueError(f"{label} must be a non-empty relative path")
    path = root / value
    if path.is_symlink():
        raise ValueError(f"{label} must not be a symlink: {value}")
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} escapes the skill root") from exc
    if not path.is_file():
        raise ValueError(f"{label} is missing: {value}")
    return value


def _record_slug(value: object, label: str) -> str:
    if not isinstance(value, str) or not SLUG.fullmatch(value):
        raise ValueError(f"{label} must be a slug")
    return value


def _record_file(root: Path, value: object, label: str) -> Path:
    relative = _file(root, value, label)
    current = root
    for part in PurePosixPath(relative).parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"{label} must not traverse a symlink: {relative}")
    return current


def _artifact_format_error(name: str) -> ValueError:
    return ValueError(f"artifact format is invalid for {name}")


WINDOWS_RESERVED_NAMES = {
    "con", "prn", "aux", "nul",
    *(f"com{index}" for index in range(1, 10)),
    *(f"lpt{index}" for index in range(1, 10)),
}
WINDOWS_INVALID_PATH_CHARS = frozenset('<>:"\\|?*')


def _bundle_path_identity(name: str, *, directory: bool = False) -> str:
    if not name or "\\" in name:
        raise ValueError("artifact bundle path is unsafe")
    raw = name[:-1] if directory and name.endswith("/") else name
    if not raw or (directory and not name.endswith("/")):
        raise ValueError("artifact bundle path is unsafe")
    segments = raw.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        raise ValueError("artifact bundle path contains an aliasing segment")
    canonical: list[str] = []
    for segment in segments:
        if (
            segment.endswith((" ", "."))
            or any(
                character in WINDOWS_INVALID_PATH_CHARS
                or ord(character) < 32
                or unicodedata.category(character).startswith("C")
                for character in segment
            )
            or segment.split(".", 1)[0].casefold() in WINDOWS_RESERVED_NAMES
        ):
            raise ValueError("artifact bundle path is not portable")
        canonical.append(unicodedata.normalize("NFKC", segment).casefold())
    return "/".join(canonical)


def _decoded_artifact(data: bytes, name: str) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise _artifact_format_error(name) from exc


def _json_artifact(data: bytes, name: str) -> object:
    try:
        return loads_json_strict(_decoded_artifact(data, name))
    except (json.JSONDecodeError, ValueError) as exc:
        raise _artifact_format_error(name) from exc


def _zip_names(data: bytes, name: str) -> set[str]:
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            names = {item.filename for item in archive.infolist() if not item.is_dir()}
            if archive.testzip() is not None:
                raise _artifact_format_error(name)
            return names
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise _artifact_format_error(name) from exc


def _validate_artifact_bytes(name: str, data: bytes) -> None:
    suffix = PurePosixPath(name).suffix.lower()
    text: str | None = None

    def decoded() -> str:
        nonlocal text
        if text is None:
            text = _decoded_artifact(data, name)
        return text

    valid = False
    if suffix == ".html":
        lowered = decoded().casefold()
        valid = ("<!doctype html" in lowered or "<html" in lowered) and "<body" in lowered
    elif suffix == ".pdf":
        valid = data.startswith(b"%PDF-") and b"%%EOF" in data[-65536:]
    elif suffix == ".pptx":
        valid = {"[Content_Types].xml", "_rels/.rels", "ppt/presentation.xml"} <= _zip_names(data, name)
    elif suffix == ".docx":
        valid = {"[Content_Types].xml", "_rels/.rels", "word/document.xml"} <= _zip_names(data, name)
    elif suffix in {".odp", ".odt"}:
        try:
            with zipfile.ZipFile(BytesIO(data)) as archive:
                expected = (
                    b"application/vnd.oasis.opendocument.presentation"
                    if suffix == ".odp"
                    else b"application/vnd.oasis.opendocument.text"
                )
                valid = archive.read("mimetype") == expected and "content.xml" in archive.namelist()
        except (KeyError, OSError, zipfile.BadZipFile, RuntimeError):
            valid = False
    elif suffix == ".typ":
        valid = bool(re.search(r"#(?:set|show|let|import|include|align|grid|table|figure|heading|page|text)\b", decoded()))
    elif suffix in {".mp4", ".mov", ".m4a"}:
        valid = len(data) >= 12 and data[4:8] == b"ftyp"
    elif suffix == ".webm":
        valid = data.startswith(b"\x1aE\xdf\xa3")
    elif suffix == ".wav":
        valid = len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WAVE"
    elif suffix == ".flac":
        valid = data.startswith(b"fLaC")
    elif suffix == ".mp3":
        valid = data.startswith(b"ID3") or (len(data) >= 2 and data[0] == 0xFF and data[1] & 0xE0 == 0xE0)
    elif suffix == ".ogg":
        valid = data.startswith(b"OggS")
    elif suffix == ".png":
        valid = data.startswith(b"\x89PNG\r\n\x1a\n")
    elif suffix in {".jpg", ".jpeg"}:
        valid = data.startswith(b"\xff\xd8\xff") and data.rstrip().endswith(b"\xff\xd9")
    elif suffix == ".webp":
        valid = len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WEBP"
    elif suffix in {".tif", ".tiff"}:
        valid = data.startswith((b"II*\x00", b"MM\x00*"))
    elif suffix == ".gif":
        valid = data.startswith((b"GIF87a", b"GIF89a"))
    elif suffix == ".svg":
        valid = bool(re.search(r"<svg(?:\s|>)", decoded(), re.IGNORECASE))
    elif suffix == ".drawio":
        valid = "<mxfile" in decoded() or "<mxGraphModel" in decoded()
    elif suffix == ".excalidraw":
        value = _json_artifact(data, name)
        valid = isinstance(value, dict) and value.get("type") == "excalidraw" and isinstance(value.get("elements"), list)
    elif suffix == ".godot":
        value = decoded()
        valid = "config_version=" in value and bool(re.search(r"^\[[a-z_]+\]", value, re.MULTILINE))
    elif suffix == ".tscn":
        valid = decoded().lstrip().startswith("[gd_scene ")
    elif suffix in {".tres", ".res"}:
        valid = data.startswith(b"RSRC") or decoded().lstrip().startswith("[gd_resource ")
    elif suffix == ".unity":
        value = decoded()
        valid = value.lstrip().startswith("%YAML") and "--- !u!" in value
    elif suffix == ".atlas":
        value = decoded()
        valid = "size:" in value and any(marker in value for marker in ("format:", "filter:", "bounds:", "rotate:"))
    elif suffix == ".blend":
        valid = data.startswith(b"BLENDER")
    elif suffix == ".3dm":
        valid = data.startswith(b"3D Geometry File Format")
    elif suffix == ".glb":
        valid = data.startswith(b"glTF")
    elif suffix == ".gltf":
        value = _json_artifact(data, name)
        asset = value.get("asset") if isinstance(value, dict) else None
        valid = isinstance(asset, dict) and isinstance(asset.get("version"), str)
    elif suffix == ".fbx":
        valid = data.startswith(b"Kaydara FBX Binary") or "FBXHeaderExtension" in decoded()
    elif suffix == ".obj":
        value = decoded()
        valid = bool(re.search(r"^v\s+[-+0-9.]", value, re.MULTILINE)) and bool(
            re.search(r"^(?:f|l)\s+", value, re.MULTILINE)
        )
    if not valid:
        raise _artifact_format_error(name)


def _validate_manifested_bundle(path: Path) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if len(infos) > 10_000:
                raise ValueError("artifact bundle manifest has too many entries")
            file_infos: dict[str, zipfile.ZipInfo] = {}
            entry_identities: dict[str, str] = {}
            for info in infos:
                name = info.filename
                mode = (info.external_attr >> 16) & 0o170000
                if mode == stat.S_IFLNK or info.flag_bits & 0x1:
                    raise ValueError("artifact bundle manifest contains an unsafe entry")
                identity = _bundle_path_identity(name, directory=info.is_dir())
                if identity in entry_identities:
                    raise ValueError("artifact bundle contains an aliasing path")
                entry_identities[identity] = name
                if not info.is_dir():
                    file_infos[name] = info
            manifest_info = file_infos.get("artifact-manifest.json")
            if manifest_info is None or manifest_info.file_size > 1_000_000:
                raise ValueError("artifact bundle manifest is missing or too large")
            try:
                manifest = loads_json_strict(archive.read(manifest_info).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                raise ValueError("artifact bundle manifest is invalid JSON") from exc
            if not isinstance(manifest, dict) or set(manifest) != {"schema_version", "primary", "files"}:
                raise ValueError("artifact bundle manifest fields are missing or unknown")
            if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
                raise ValueError("artifact bundle manifest schema_version must be 1")
            primary = manifest["primary"]
            rows = manifest["files"]
            if not isinstance(primary, str) or not primary or not isinstance(rows, list) or not rows:
                raise ValueError("artifact bundle manifest primary/files are invalid")
            declared: dict[str, str] = {}
            declared_identities: dict[str, str] = {}
            for index, row in enumerate(rows):
                if not isinstance(row, dict) or set(row) != {"path", "sha256"}:
                    raise ValueError(f"artifact bundle manifest files[{index}] fields are invalid")
                name = row["path"]
                digest = row["sha256"]
                if not isinstance(name, str):
                    raise ValueError(f"artifact bundle manifest files[{index}] path is invalid")
                try:
                    identity = _bundle_path_identity(name)
                except ValueError as exc:
                    raise ValueError(f"artifact bundle manifest files[{index}] path is invalid") from exc
                if (
                    identity == _bundle_path_identity("artifact-manifest.json")
                    or name in declared or identity in declared_identities
                ):
                    raise ValueError(f"artifact bundle manifest files[{index}] path is invalid or aliasing")
                if not isinstance(digest, str) or not SHA256.fullmatch(digest):
                    raise ValueError(f"artifact bundle manifest files[{index}] sha256 is invalid")
                declared[name] = digest
                declared_identities[identity] = name
            if primary not in declared:
                raise ValueError("artifact bundle manifest primary is not a declared payload")
            if set(file_infos) != {"artifact-manifest.json", *declared}:
                raise ValueError("artifact bundle manifest does not bind the exact payload set")
            primary_bytes: bytes | None = None
            for name, digest in declared.items():
                with archive.open(file_infos[name]) as source:
                    hasher = hashlib.sha256()
                    chunks: list[bytes] = []
                    size = 0
                    while True:
                        chunk = source.read(1024 * 1024)
                        if not chunk:
                            break
                        size += len(chunk)
                        if size > 2_000_000_000:
                            raise ValueError("artifact bundle manifest payload exceeds size limit")
                        hasher.update(chunk)
                        if name == primary:
                            chunks.append(chunk)
                if hasher.hexdigest() != digest:
                    raise ValueError(f"artifact bundle manifest hash mismatch: {name}")
                if name == primary:
                    primary_bytes = b"".join(chunks)
            if PurePosixPath(primary).suffix.lower() == ".zip":
                raise ValueError("artifact bundle manifest cannot use a nested ZIP as primary")
            assert primary_bytes is not None
            _validate_artifact_bytes(primary, primary_bytes)
    except zipfile.BadZipFile as exc:
        raise ValueError("artifact bundle manifest requires a valid ZIP archive") from exc


def validate_artifact_format(path: Path) -> None:
    """Validate provable container/signature identity, never aesthetic quality."""
    if path.suffix.lower() == ".zip":
        _validate_manifested_bundle(path)
    else:
        _validate_artifact_bytes(path.name, path.read_bytes())


def validate_artifact_lifecycle(
    lifecycle: object,
    evidence_ids: set[str],
    release_evidence: set[str],
) -> None:
    fields = {
        "initial_state", "states", "release_states", "rejected_states",
        "transitions", "rejection_transition",
    }
    if not isinstance(lifecycle, dict) or set(lifecycle) != fields:
        raise ValueError("artifact lifecycle fields are missing or unknown")
    states = lifecycle["states"]
    if not isinstance(states, dict) or not states:
        raise ValueError("artifact lifecycle states must be a non-empty mapping")
    for state_id, state in states.items():
        if not isinstance(state_id, str) or not SLUG.fullmatch(state_id):
            raise ValueError("artifact lifecycle state ids must be slugs")
        if not isinstance(state, dict) or set(state) != {
            "terminal", "user_facing_label", "requires_output_foundations", "requires_output_mechanics",
        }:
            raise ValueError(f"artifact lifecycle state {state_id} fields are invalid")
        if (
            not isinstance(state["terminal"], bool)
            or not isinstance(state["requires_output_foundations"], bool)
            or not isinstance(state["requires_output_mechanics"], bool)
            or not isinstance(state["user_facing_label"], str)
            or not state["user_facing_label"].strip()
        ):
            raise ValueError(f"artifact lifecycle state {state_id} values are invalid")

    initial = lifecycle["initial_state"]
    if not isinstance(initial, str) or initial not in states or states[initial]["terminal"]:
        raise ValueError("artifact lifecycle initial_state must be a nonterminal declared state")
    release_states = lifecycle["release_states"]
    rejected_states = lifecycle["rejected_states"]
    for label, values in (("release_states", release_states), ("rejected_states", rejected_states)):
        if not _unique_strings(values, slugged=True) or any(value not in states or not states[value]["terminal"] for value in values):
            raise ValueError(f"artifact lifecycle {label} must name terminal declared states")
    if set(release_states) & set(rejected_states):
        raise ValueError("artifact lifecycle release and rejected states must be disjoint")
    if states[initial]["requires_output_foundations"] or states[initial]["requires_output_mechanics"]:
        raise ValueError("artifact lifecycle obligation cannot begin at the initial state")
    if any(
        states[state]["requires_output_foundations"] or states[state]["requires_output_mechanics"]
        for state in rejected_states
    ):
        raise ValueError("artifact lifecycle obligation flags must be false on rejected states")
    if any(
        not states[state]["requires_output_foundations"] or not states[state]["requires_output_mechanics"]
        for state in release_states
    ):
        raise ValueError("artifact lifecycle obligation flags must hold on release states")

    graph: dict[str, list[tuple[str, set[str]]]] = {state: [] for state in states}
    edges: set[tuple[str, str]] = set()
    transitions = lifecycle["transitions"]
    if not isinstance(transitions, list) or not transitions:
        raise ValueError("artifact lifecycle transitions must be non-empty")
    for index, transition in enumerate(transitions):
        if not isinstance(transition, dict) or set(transition) != {"from", "to", "requires"}:
            raise ValueError(f"artifact lifecycle transition {index} fields are invalid")
        source, target = transition["from"], transition["to"]
        if (
            not isinstance(source, str)
            or not isinstance(target, str)
            or source not in states
            or target not in states
            or states[source]["terminal"]
        ):
            raise ValueError(f"artifact lifecycle transition {index} references an invalid state")
        edge = (source, target)
        if edge in edges:
            raise ValueError("artifact lifecycle transition edges must be unique")
        edges.add(edge)
        requirements = transition["requires"]
        if not _unique_strings(requirements, slugged=True):
            raise ValueError(f"artifact lifecycle transition {index}.requires must be unique evidence ids")
        unknown = sorted(set(requirements) - evidence_ids)
        if unknown:
            raise ValueError(f"artifact lifecycle transition {index} references unknown evidence: {unknown}")
        graph[source].append((target, set(requirements)))

        if target not in rejected_states:
            source_foundations = states[source]["requires_output_foundations"]
            target_foundations = states[target]["requires_output_foundations"]
            source_mechanics = states[source]["requires_output_mechanics"]
            target_mechanics = states[target]["requires_output_mechanics"]
            if source_foundations and not target_foundations:
                raise ValueError("artifact lifecycle foundation obligation must be monotonic")
            if source_mechanics and not target_mechanics:
                raise ValueError("artifact lifecycle mechanics obligation must be monotonic")
            if target_foundations and not source_foundations and "creative-source" not in requirements:
                raise ValueError("artifact lifecycle foundation obligation must begin with creative-source evidence")
            production_evidence = {"working-artifact", "rendered-artifact", "native-context"}
            if target_mechanics and not source_mechanics and not production_evidence <= set(requirements):
                raise ValueError("artifact lifecycle mechanics obligation must begin with whole-artifact evidence")

    reached_release: set[str] = set()

    def walk(state: str, accumulated: set[str], path: set[str]) -> None:
        if state in path:
            raise ValueError("artifact lifecycle release graph must be acyclic")
        if state in release_states:
            reached_release.add(state)
            missing = sorted(release_evidence - accumulated)
            if missing:
                raise ValueError(f"artifact lifecycle release path omits evidence: {missing}")
            return
        if states[state]["terminal"]:
            return
        for target, requirements in graph[state]:
            walk(target, accumulated | requirements, path | {state})

    walk(initial, set(), set())
    if reached_release != set(release_states):
        raise ValueError("artifact lifecycle release states must be reachable from initial_state")

    rejection = lifecycle["rejection_transition"]
    if not isinstance(rejection, dict) or set(rejection) != {"from_any_nonterminal", "to", "effect"}:
        raise ValueError("artifact lifecycle rejection_transition fields are invalid")
    rejection_target = rejection["to"]
    if (
        rejection["from_any_nonterminal"] is not True
        or not isinstance(rejection_target, str)
        or rejection_target not in rejected_states
    ):
        raise ValueError("artifact lifecycle rejection transition must terminate in a rejected state")
    if not isinstance(rejection["effect"], str) or not rejection["effect"].strip():
        raise ValueError("artifact lifecycle rejection effect is invalid")


def validate_artifact_record(
    record: object,
    registry: object,
    project_root: Path,
    registry_root: Path = ROOT,
) -> None:
    """Validate one project release record against the registry's declared lifecycle."""
    if not isinstance(record, dict) or set(record) != ARTIFACT_RECORD_FIELDS:
        raise ValueError("artifact record fields are missing or unknown")
    if not isinstance(registry, dict):
        raise ValueError("artifact record registry must be an object")
    if type(record["schema_version"]) is not int or record["schema_version"] != 1:
        raise ValueError("artifact record schema_version must be 1")
    if type(record["registry_schema_version"]) is not int or record["registry_schema_version"] != registry.get("schema_version"):
        raise ValueError("artifact record registry_schema_version does not match registry")
    validate_capability_registry(registry, registry_root)
    registry_path = registry_root / "references" / "capability-registry.json"
    canonical_registry_bytes = registry_path.read_bytes()
    canonical_registry = loads_json_strict(canonical_registry_bytes.decode("utf-8"))
    if registry != canonical_registry:
        raise ValueError("artifact record must use the installed registry")
    registry_sha256 = record["registry_sha256"]
    if not isinstance(registry_sha256, str) or not SHA256.fullmatch(registry_sha256):
        raise ValueError("artifact record registry_sha256 must be a lowercase SHA-256 digest")
    if hashlib.sha256(canonical_registry_bytes).hexdigest() != registry_sha256:
        raise ValueError("artifact record registry_sha256 does not match the installed registry")

    _record_slug(record["artifact_id"], "artifact record artifact_id")
    capability_id = _record_slug(record["capability_id"], "artifact record capability_id")
    capabilities = {
        capability["id"]: capability
        for capability in registry.get("capabilities", [])
        if isinstance(capability, dict) and isinstance(capability.get("id"), str)
    }
    if capability_id not in capabilities:
        raise ValueError("artifact record capability_id is not registered")

    producer = record["producer"]
    creative_authority = record["creative_authority"]
    for label, value in (
        ("producer", producer),
        ("creative_authority", creative_authority),
        ("final_audience", record["final_audience"]),
        ("requester_reviewer", record["requester_reviewer"]),
    ):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"artifact record {label} must be non-empty")
    if _normalized_identity(creative_authority) != "mature-design-director":
        raise ValueError("artifact record creative_authority must be mature-design-director")
    if _normalized_identity(producer) == _normalized_identity(creative_authority):
        raise ValueError("artifact record producer must differ from creative_authority")

    lifecycle = registry.get("artifact_lifecycle")
    if not isinstance(lifecycle, dict) or not isinstance(lifecycle.get("states"), dict):
        raise ValueError("artifact record registry has no valid lifecycle")
    states = lifecycle["states"]
    artifact_state = record["artifact_state"]
    if not isinstance(artifact_state, str) or artifact_state not in states:
        raise ValueError("artifact record artifact_state is unknown")

    native_medium = record["native_medium"]
    if not isinstance(native_medium, dict) or set(native_medium) != NATIVE_MEDIUM_FIELDS:
        raise ValueError("artifact record native_medium fields are missing or unknown")
    for field in sorted(NATIVE_MEDIUM_FIELDS):
        value = native_medium[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"artifact record native_medium {field} must be non-empty")
    output_contracts = {
        item["id"]: item
        for item in capabilities[capability_id]["outputs"]
    }
    output_class = _record_slug(native_medium["output_class"], "artifact record native_medium output_class")
    if output_class not in output_contracts:
        raise ValueError("artifact record native_medium output_class is not declared by the capability")
    selected_output = output_contracts[output_class]
    classification = _record_slug(native_medium["classification"], "artifact record native_medium classification")

    primary_artifact = record["primary_artifact"]
    if not isinstance(primary_artifact, dict) or set(primary_artifact) != PRIMARY_ARTIFACT_FIELDS:
        raise ValueError("artifact record primary_artifact fields are missing or unknown")
    primary_path = _record_file(project_root, primary_artifact["ref"], "artifact record primary_artifact ref")
    primary_sha256 = primary_artifact["sha256"]
    if not isinstance(primary_sha256, str) or not SHA256.fullmatch(primary_sha256):
        raise ValueError("artifact record primary_artifact sha256 must be a lowercase SHA-256 digest")
    if hashlib.sha256(primary_path.read_bytes()).hexdigest() != primary_sha256:
        raise ValueError("artifact record primary_artifact sha256 does not match artifact bytes")
    primary_suffix = primary_path.suffix.lower()

    evidence_types = registry.get("evidence_types")
    if not isinstance(evidence_types, dict):
        raise ValueError("artifact record registry has no evidence types")
    evidence = record["evidence"]
    if not isinstance(evidence, dict):
        raise ValueError("artifact record evidence must be an object")
    if not set(evidence) <= set(evidence_types):
        raise ValueError("artifact record contains unknown evidence")

    evidence_hashes: set[str] = set()
    evidence_hashes_by_id: dict[str, set[str]] = {}
    for evidence_id, items in evidence.items():
        if not isinstance(items, list) or not items:
            raise ValueError(f"artifact record evidence {evidence_id} must be a non-empty list")
        item_refs: set[str] = set()
        item_hashes: set[str] = set()
        for index, item in enumerate(items):
            label = f"artifact record evidence {evidence_id}[{index}]"
            if not isinstance(item, dict) or set(item) != EVIDENCE_ITEM_FIELDS:
                raise ValueError(f"{label} fields are missing or unknown")
            path = _record_file(project_root, item["ref"], f"{label} ref")
            sha256 = item["sha256"]
            if not isinstance(sha256, str) or not SHA256.fullmatch(sha256):
                raise ValueError(f"{label} sha256 must be a lowercase SHA-256 digest")
            if hashlib.sha256(path.read_bytes()).hexdigest() != sha256:
                raise ValueError(f"{label} sha256 does not match bound evidence bytes")
            subject_sha256 = item["subject_sha256"]
            if not isinstance(subject_sha256, str) or not SHA256.fullmatch(subject_sha256):
                raise ValueError(f"{label} subject_sha256 must be a lowercase SHA-256 digest")
            if subject_sha256 != primary_sha256:
                raise ValueError(f"{label} subject_sha256 does not match primary artifact")
            if item["ref"] in item_refs or sha256 in item_hashes:
                raise ValueError(f"artifact record evidence {evidence_id} contains a duplicate evidence item")
            item_refs.add(item["ref"])
            item_hashes.add(sha256)
            evidence_hashes.add(sha256)
            if not isinstance(item["description"], str) or not item["description"].strip():
                raise ValueError(f"{label} description must be non-empty")
            reviewer = item["reviewer"]
            if not isinstance(reviewer, str):
                raise ValueError(f"{label} reviewer must be a string")
            if reviewer and (not reviewer.strip() or not _normalized_identity(reviewer)):
                raise ValueError(f"{label} reviewer must be empty or a visible identity")
            benchmarks = item["benchmarks"]
            if not _unique_strings(benchmarks, allow_empty=True):
                raise ValueError(f"{label} benchmarks must be a unique string list")
            if evidence_id in {"proof-selection", "independent-critique"}:
                if not reviewer.strip():
                    raise ValueError(f"{label} reviewer must be non-empty")
                if _normalized_identity(reviewer) == _normalized_identity(str(producer)):
                    raise ValueError(f"{label} reviewer must differ from producer")
            if evidence_id in {"proof-selection", "comparative-quality"} and not benchmarks:
                raise ValueError(f"{label} must name mature benchmarks")
        evidence_hashes_by_id[evidence_id] = item_hashes

    for group in registry["authority"]["distinct_evidence_sets"]:
        for index, left in enumerate(group):
            for right in group[index + 1:]:
                if evidence_hashes_by_id.get(left, set()) & evidence_hashes_by_id.get(right, set()):
                    raise ValueError(f"artifact record distinct evidence bytes are reused by {left} and {right}")

    foundations = record["creative_foundations"]
    mechanics = record["assembly_mechanics"]
    if not isinstance(foundations, list) or not isinstance(mechanics, list):
        raise ValueError("artifact record foundation and mechanics layers must be lists")
    declared_foundations = {
        item["role"]: set(item["sources"])
        for item in capabilities[capability_id]["foundations"]
    }
    declared_mechanics = {
        item["role"]: set(item["candidates"])
        for item in capabilities[capability_id]["delegates"]
    }
    foundation_sources: set[str] = set()
    for index, item in enumerate(foundations):
        label = f"artifact record creative_foundations[{index}]"
        if not isinstance(item, dict) or set(item) != RECORD_FOUNDATION_FIELDS:
            raise ValueError(f"{label} fields are missing or unknown")
        role = _record_slug(item["role"], f"{label} role")
        if role not in declared_foundations:
            raise ValueError(f"{label} role is not declared by the capability")
        source_class = _record_slug(item["source_class"], f"{label} source_class")
        if source_class not in declared_foundations[role]:
            raise ValueError(f"{label} source_class is not declared for its capability role")
        source = item["source"]
        if not isinstance(source, str) or not source.strip():
            raise ValueError(f"{label} source must be non-empty")
        foundation_sources.add(_normalized_identity(source))
        if item["evidence"] != "creative-source" or item["evidence"] not in evidence:
            raise ValueError(f"{label} must bind creative-source evidence")
    mechanics_tools: set[str] = set()
    for index, item in enumerate(mechanics):
        label = f"artifact record assembly_mechanics[{index}]"
        if not isinstance(item, dict) or set(item) != RECORD_MECHANICS_FIELDS:
            raise ValueError(f"{label} fields are missing or unknown")
        role = _record_slug(item["role"], f"{label} role")
        if role not in declared_mechanics:
            raise ValueError(f"{label} role is not declared by the capability")
        candidate = _record_slug(item["candidate"], f"{label} candidate")
        if candidate not in declared_mechanics[role]:
            raise ValueError(f"{label} candidate is not declared for its capability role")
        tool = item["tool"]
        if not isinstance(tool, str) or not tool.strip():
            raise ValueError(f"{label} tool must be non-empty")
        mechanics_tools.add(_normalized_identity(tool))
        mechanics_evidence = _record_slug(item["evidence"], f"{label} evidence")
        if mechanics_evidence not in evidence or mechanics_evidence == "creative-source":
            raise ValueError(f"{label} must bind non-creative mechanics evidence")
    if foundation_sources & mechanics_tools:
        raise ValueError("artifact record creative foundation and assembly mechanics overlap")
    history = record["state_history"]
    if not isinstance(history, list) or not history:
        raise ValueError("artifact record state_history must be non-empty")
    if not isinstance(history[0], dict) or history[0].get("state") != lifecycle.get("initial_state"):
        raise ValueError("artifact record state_history must start at the lifecycle initial_state")
    transitions = {
        (transition["from"], transition["to"]): set(transition["requires"])
        for transition in lifecycle.get("transitions", [])
        if isinstance(transition, dict)
    }
    rejected_states = set(lifecycle.get("rejected_states", []))
    rejection_target = lifecycle["rejection_transition"]["to"]
    attached_evidence: set[str] = set()
    previous_state: str | None = None
    for index, row in enumerate(history):
        label = f"artifact record state_history[{index}]"
        if not isinstance(row, dict) or set(row) != STATE_HISTORY_FIELDS:
            raise ValueError(f"{label} fields are missing or unknown")
        state = row["state"]
        if not isinstance(state, str) or state not in states:
            raise ValueError(f"{label} state is unknown")
        if not _unique_strings(row["evidence"], allow_empty=True):
            raise ValueError(f"{label} evidence must be a unique evidence list")
        row_evidence = set(row["evidence"])
        if not row_evidence <= set(evidence):
            raise ValueError(f"{label} references unbound evidence")
        duplicated = attached_evidence & row_evidence
        if duplicated:
            raise ValueError(f"artifact record evidence appears in more than one lifecycle stage: {sorted(duplicated)}")
        if previous_state is not None:
            if state == rejection_target:
                if states[previous_state]["terminal"]:
                    raise ValueError("artifact record terminal state cannot transition to rejected")
                if index != len(history) - 1:
                    raise ValueError("artifact record rejected state must be terminal")
            else:
                required = transitions.get((previous_state, state))
                if required is None:
                    raise ValueError(f"artifact record illegal lifecycle transition {previous_state} -> {state}")
                missing = required - row_evidence
                if missing:
                    raise ValueError(
                        f"artifact record transition {previous_state} -> {state} misses evidence: {sorted(missing)}"
                    )
        attached_evidence.update(row_evidence)
        previous_state = state
    if previous_state != artifact_state:
        raise ValueError("artifact record artifact_state does not match state_history")
    if attached_evidence != set(evidence):
        raise ValueError("artifact record evidence must be attached to lifecycle history")

    history_states = [row["state"] for row in history]
    if any(states[state]["requires_output_foundations"] for state in history_states):
        missing_foundation_roles = set(selected_output["requires_foundations"]) - {
            item["role"] for item in foundations
        }
        if missing_foundation_roles:
            raise ValueError(
                f"artifact record output_class requires foundation roles: {sorted(missing_foundation_roles)}"
            )
    requires_output_mechanics = any(
        states[state]["requires_output_mechanics"] for state in history_states
    )
    if requires_output_mechanics:
        missing_mechanics_roles = set(selected_output["requires_delegates"]) - {
            item["role"] for item in mechanics
        }
        if missing_mechanics_roles:
            raise ValueError(
                f"artifact record output_class requires mechanics roles: {sorted(missing_mechanics_roles)}"
            )
        if primary_suffix not in selected_output["artifact_suffixes"]:
            raise ValueError("artifact record primary_artifact suffix is not allowed by output_class")
        validate_artifact_format(primary_path)

    delegations = record["delegations"]
    if not isinstance(delegations, list):
        raise ValueError("artifact record delegations must be a list")
    delegation_ids: set[str] = set()
    for index, item in enumerate(delegations):
        label = f"artifact record delegation {index}"
        if not isinstance(item, dict) or set(item) != RECORD_DELEGATION_FIELDS:
            raise ValueError(f"{label} fields are missing or unknown")
        if item["status"] != "completed":
            raise ValueError(f"{label} must be completed before acceptance")
        task_id = _record_slug(item["task_id"], f"{label} task_id")
        if task_id in delegation_ids:
            raise ValueError("artifact record delegation task_id values must be unique")
        delegation_ids.add(task_id)
        artifact_path = _record_file(project_root, item["artifact_ref"], f"{label} artifact_ref")
        artifact_sha256 = item["artifact_sha256"]
        if not isinstance(artifact_sha256, str) or not SHA256.fullmatch(artifact_sha256):
            raise ValueError(f"{label} artifact_sha256 must be a lowercase SHA-256 digest")
        if hashlib.sha256(artifact_path.read_bytes()).hexdigest() != artifact_sha256:
            raise ValueError(f"{label} artifact_sha256 does not match artifact bytes")
        if artifact_sha256 not in evidence_hashes:
            raise ValueError(f"{label} artifact_sha256 is not bound by evidence")
        if item["accepted_by"] != creative_authority:
            raise ValueError(f"{label} accepted_by must be the creative_authority")
        acceptance_evidence = _record_slug(item["acceptance_evidence"], f"{label} acceptance_evidence")
        if acceptance_evidence not in evidence:
            raise ValueError(f"{label} acceptance_evidence is unbound")
        if artifact_sha256 not in evidence_hashes_by_id[acceptance_evidence]:
            raise ValueError(f"{label} acceptance_evidence does not bind artifact_sha256")

    release_states = set(lifecycle.get("release_states", []))
    rejection_reason = record["rejection_reason"]
    if not isinstance(rejection_reason, str):
        raise ValueError("artifact record rejection_reason must be a string")
    if rejection_reason and not rejection_reason.strip():
        raise ValueError("artifact record rejection_reason must be empty or non-whitespace")
    if artifact_state in release_states:
        if classification not in selected_output["allowed_classifications"]:
            raise ValueError("artifact record native_medium classification is not allowed by output_class")
        required_release = set(registry["authority"]["release_evidence"]) | set(capabilities[capability_id]["evidence"])
        missing = required_release - attached_evidence
        if missing:
            raise ValueError(f"artifact record delivered state misses evidence: {sorted(missing)}")
        if not foundations or not mechanics:
            raise ValueError("artifact record delivered state requires creative foundations and assembly mechanics")
        if rejection_reason.strip():
            raise ValueError("artifact record delivered state cannot include rejection_reason")
    elif artifact_state in rejected_states:
        if not rejection_reason.strip():
            raise ValueError("artifact record rejected state requires rejection_reason")
    elif rejection_reason.strip():
        raise ValueError("artifact record non-rejected state cannot include rejection_reason")


def validate_capability_registry(data: object, root: Path = ROOT) -> set[str]:
    if not isinstance(data, dict) or set(data) != REGISTRY_FIELDS:
        raise ValueError("capability registry fields are missing or unknown")
    if type(data["schema_version"]) is not int or data["schema_version"] != 4 or data["skill"] != "mature-design-director":
        raise ValueError("capability registry identity/schema is invalid")
    authority = data["authority"]
    if not isinstance(authority, dict) or set(authority) != {
        "owns", "delegates", "composition_rule", "release_evidence", "distinct_evidence_sets",
    }:
        raise ValueError("capability registry authority is invalid")
    if not _unique_strings(authority["owns"], slugged=True) or not _unique_strings(authority["delegates"], slugged=True):
        raise ValueError("authority owns/delegates must be unique slug lists")
    if not isinstance(authority["composition_rule"], str) or not authority["composition_rule"].strip():
        raise ValueError("authority composition_rule is invalid")
    if not _unique_strings(authority["release_evidence"], slugged=True):
        raise ValueError("authority release_evidence must be a non-empty unique slug list")
    distinct_sets = authority["distinct_evidence_sets"]
    if not isinstance(distinct_sets, list) or not distinct_sets:
        raise ValueError("authority distinct_evidence_sets must be non-empty")
    distinct_members: set[str] = set()
    for index, group in enumerate(distinct_sets):
        if not _unique_strings(group, slugged=True) or len(group) < 2:
            raise ValueError(f"authority distinct_evidence_sets[{index}] must contain unique evidence ids")
        overlap = distinct_members & set(group)
        if overlap:
            raise ValueError(f"authority distinct_evidence_sets overlap: {sorted(overlap)}")
        distinct_members.update(group)
    layer_contract = data["layer_contract"]
    if not isinstance(layer_contract, dict) or set(layer_contract) != {"creative_foundation", "assembly_mechanics", "separation_rule"}:
        raise ValueError("layer_contract fields are invalid")
    if not all(isinstance(value, str) and value.strip() for value in layer_contract.values()):
        raise ValueError("layer_contract values must be non-empty strings")

    flow = data["flow"]
    if not isinstance(flow, list) or not flow:
        raise ValueError("capability registry flow must be non-empty")
    flow_ids = set()
    for index, stage in enumerate(flow):
        if not isinstance(stage, dict) or set(stage) != {"id", "purpose", "completion"}:
            raise ValueError(f"flow stage {index} fields are invalid")
        if not isinstance(stage["id"], str) or not SLUG.fullmatch(stage["id"]) or stage["id"] in flow_ids:
            raise ValueError(f"flow stage {index}.id must be a unique slug")
        if not all(isinstance(stage[key], str) and stage[key].strip() for key in ("purpose", "completion")):
            raise ValueError(f"flow stage {index} text is invalid")
        flow_ids.add(stage["id"])

    evidence = data["evidence_types"]
    if not isinstance(evidence, dict) or not evidence:
        raise ValueError("evidence_types must be a non-empty mapping")
    for evidence_id, description in evidence.items():
        if not isinstance(evidence_id, str) or not SLUG.fullmatch(evidence_id):
            raise ValueError("evidence type ids must be slugs")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"evidence type {evidence_id} description is invalid")
    release_evidence = set(authority["release_evidence"])
    unknown_release_evidence = sorted(release_evidence - set(evidence))
    if unknown_release_evidence:
        raise ValueError(f"authority references unknown release evidence: {unknown_release_evidence}")
    unknown_distinct_evidence = sorted(distinct_members - set(evidence))
    if unknown_distinct_evidence:
        raise ValueError(f"authority references unknown distinct evidence: {unknown_distinct_evidence}")
    validate_artifact_lifecycle(data["artifact_lifecycle"], set(evidence), release_evidence)

    capabilities = data["capabilities"]
    if not isinstance(capabilities, list) or not capabilities:
        raise ValueError("capabilities must be a non-empty list")
    capability_ids, contracts, linked = set(), set(), set()
    for index, capability in enumerate(capabilities):
        label = f"capability {index}"
        if not isinstance(capability, dict) or set(capability) != CAPABILITY_FIELDS:
            raise ValueError(f"{label} fields are missing or unknown")
        capability_id = capability["id"]
        if not isinstance(capability_id, str) or not SLUG.fullmatch(capability_id) or capability_id in capability_ids:
            raise ValueError(f"{label}.id must be a unique slug")
        capability_ids.add(capability_id)
        contract = _file(root, capability["contract"], f"{label}.contract")
        if contract in contracts:
            raise ValueError(f"{label}.contract is duplicated")
        contracts.add(contract)
        linked.add(contract)
        for key in ("accepts", "evidence"):
            if not _unique_strings(capability[key], slugged=True):
                raise ValueError(f"{label}.{key} must be a non-empty unique slug list")
        unknown_evidence = sorted(set(capability["evidence"]) - set(evidence))
        if unknown_evidence:
            raise ValueError(f"{label} references unknown evidence: {unknown_evidence}")
        foundations = capability["foundations"]
        if not isinstance(foundations, list) or not foundations:
            raise ValueError(f"{label}.foundations must be a non-empty list")
        foundation_roles, creative_sources = set(), set()
        for offset, foundation in enumerate(foundations):
            if not isinstance(foundation, dict) or set(foundation) != {"role", "sources"}:
                raise ValueError(f"{label}.foundations[{offset}] fields are invalid")
            role = foundation["role"]
            if not isinstance(role, str) or not SLUG.fullmatch(role) or role in foundation_roles:
                raise ValueError(f"{label}.foundations[{offset}].role must be a unique slug")
            if not _unique_strings(foundation["sources"], slugged=True):
                raise ValueError(f"{label}.foundations[{offset}].sources must be unique slugs")
            overlap = creative_sources & set(foundation["sources"])
            if overlap:
                raise ValueError(f"{label}.foundations duplicate creative sources: {sorted(overlap)}")
            foundation_roles.add(role)
            creative_sources.update(foundation["sources"])
        delegates = capability["delegates"]
        if not isinstance(delegates, list):
            raise ValueError(f"{label}.delegates must be a list")
        roles, mechanics = set(), set()
        for offset, delegation in enumerate(delegates):
            if not isinstance(delegation, dict) or set(delegation) != {"role", "candidates"}:
                raise ValueError(f"{label}.delegates[{offset}] fields are invalid")
            role = delegation["role"]
            if not isinstance(role, str) or not SLUG.fullmatch(role) or role in roles:
                raise ValueError(f"{label}.delegates[{offset}].role must be a unique slug")
            if not _unique_strings(delegation["candidates"], slugged=True):
                raise ValueError(f"{label}.delegates[{offset}].candidates must be unique slugs")
            roles.add(role)
            mechanics.update(delegation["candidates"])
        overlap = sorted(creative_sources & mechanics)
        if overlap:
            raise ValueError(f"{label} mixes creative foundations with mechanics: {overlap}")
        outputs = capability["outputs"]
        if not isinstance(outputs, list) or not outputs:
            raise ValueError(f"{label}.outputs must be a non-empty list")
        output_ids: set[str] = set()
        for offset, output in enumerate(outputs):
            output_label = f"{label}.outputs[{offset}]"
            if not isinstance(output, dict) or set(output) != OUTPUT_CONTRACT_FIELDS:
                raise ValueError(f"{output_label} fields are invalid")
            output_id = output["id"]
            if not isinstance(output_id, str) or not SLUG.fullmatch(output_id) or output_id in output_ids:
                raise ValueError(f"{output_label}.id must be a unique slug")
            output_ids.add(output_id)
            if not _unique_strings(output["requires_foundations"], slugged=True):
                raise ValueError(f"{output_label}.requires_foundations must be unique role slugs")
            if not _unique_strings(output["requires_delegates"], slugged=True):
                raise ValueError(f"{output_label}.requires_delegates must be unique role slugs")
            if not _unique_strings(output["allowed_classifications"], slugged=True):
                raise ValueError(f"{output_label}.allowed_classifications must be unique slugs")
            if not _unique_strings(output["artifact_suffixes"]):
                raise ValueError(f"{output_label}.artifact_suffixes must be unique strings")
            if any(not re.fullmatch(r"\.[a-z0-9]+", suffix) for suffix in output["artifact_suffixes"]):
                raise ValueError(f"{output_label}.artifact_suffixes must be lowercase file suffixes")
            unknown_foundations = sorted(set(output["requires_foundations"]) - foundation_roles)
            if unknown_foundations:
                raise ValueError(f"{output_label} references unknown foundation roles: {unknown_foundations}")
            unknown_delegates = sorted(set(output["requires_delegates"]) - roles)
            if unknown_delegates:
                raise ValueError(f"{output_label} references unknown delegate roles: {unknown_delegates}")

    ecosystem = data["ecosystem"]
    if not isinstance(ecosystem, dict) or not ecosystem:
        raise ValueError("ecosystem must be a non-empty path mapping")
    for key, value in ecosystem.items():
        if not isinstance(key, str) or not SLUG.fullmatch(key.replace("_", "-")):
            raise ValueError("ecosystem keys must be semantic slugs")
        linked.add(_file(root, value, f"ecosystem.{key}"))
    resources = data["resources"]
    if not _unique_strings(resources):
        raise ValueError("resources must be a non-empty unique path list")
    for index, value in enumerate(resources):
        linked.add(_file(root, value, f"resources[{index}]"))
    learning = data["learning"]
    if not isinstance(learning, dict) or set(learning) != {
        "contract", "project_record", "default_target", "shared_case_policy",
    }:
        raise ValueError("learning contract fields are invalid")
    linked.add(_file(root, learning["contract"], "learning.contract"))
    record = learning["project_record"]
    if not isinstance(record, str) or not record.endswith("/") or Path(record).is_absolute() or ".." in Path(record).parts:
        raise ValueError("learning.project_record must be a safe relative directory")
    for key in ("default_target", "shared_case_policy"):
        if not isinstance(learning[key], str) or not SLUG.fullmatch(learning[key]):
            raise ValueError(f"learning.{key} must be a slug")
    return linked


def validate_creative_skill_sources(data: object) -> None:
    if not isinstance(data, dict) or set(data) != {
        "schema_version", "verified_at", "method", "sources", "reviewed_not_absorbed"
    }:
        raise ValueError("creative skill registry top-level fields are invalid")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("creative skill registry schema_version must be 1")
    try:
        verified_at = dt.date.fromisoformat(data["verified_at"])
    except (TypeError, ValueError) as exc:
        raise ValueError("creative skill registry.verified_at must be an ISO date") from exc
    if verified_at > dt.datetime.now(dt.timezone.utc).date():
        raise ValueError("creative skill registry.verified_at cannot be in the future")
    if not isinstance(data["method"], dict) or not data["method"]:
        raise ValueError("creative skill registry.method must be a non-empty object")
    sources = data["sources"]
    if not isinstance(sources, list) or not sources:
        raise ValueError("creative skill registry.sources must be a non-empty list")
    expected = {
        "repository", "url", "maintainer_class", "stars_at_verification", "pushed_at",
        "repository_license", "license_status", "selected_skills", "absorbed_behaviors",
        "placement", "rejected_assumptions",
    }
    repositories: set[str] = set()
    skill_identities: set[tuple[str, str]] = set()
    for index, source in enumerate(sources):
        label = f"creative skill source {index}"
        if not isinstance(source, dict) or set(source) != expected:
            raise ValueError(f"{label} fields are invalid")
        repository = source["repository"]
        if not _repository_segments("github", repository):
            raise ValueError(f"{label}.repository must be owner/repo")
        identity = repository.casefold()
        if identity in repositories:
            raise ValueError(f"creative skill registry duplicates repository: {repository}")
        repositories.add(identity)
        expected_url = f"https://github.com/{repository}"
        if not isinstance(source["url"], str) or source["url"].casefold() != expected_url.casefold():
            raise ValueError(f"{label}.url must match repository")
        if not isinstance(source["maintainer_class"], str) or not source["maintainer_class"].strip():
            raise ValueError(f"{label}.maintainer_class must be non-empty")
        if type(source["stars_at_verification"]) is not int or source["stars_at_verification"] < 0:
            raise ValueError(f"{label}.stars_at_verification must be a non-negative integer")
        if not isinstance(source["pushed_at"], str) or not source["pushed_at"].endswith("Z"):
            raise ValueError(f"{label}.pushed_at must be a UTC timestamp")
        if source["repository_license"] is not None and (
            not isinstance(source["repository_license"], str) or not source["repository_license"].strip()
        ):
            raise ValueError(f"{label}.repository_license must be null or non-empty")
        if not isinstance(source["license_status"], str) or not source["license_status"].strip():
            raise ValueError(f"{label}.license_status must be non-empty")
        for field in ("selected_skills", "absorbed_behaviors", "placement", "rejected_assumptions"):
            values = source[field]
            if not isinstance(values, list) or any(not isinstance(item, str) or not item.strip() for item in values):
                raise ValueError(f"{label}.{field} must be a list of non-empty strings")
            if len(values) != len(set(values)):
                raise ValueError(f"{label}.{field} contains duplicates")
        if not source["selected_skills"] or not source["absorbed_behaviors"] or not source["placement"]:
            raise ValueError(f"{label} must select skills, absorb behavior, and name placement")
        for path in source["selected_skills"]:
            pure = PurePosixPath(path)
            if pure.is_absolute() or ".." in pure.parts or pure.name != "SKILL.md":
                raise ValueError(f"{label}.selected_skills has invalid path: {path}")
            skill_identity = (identity, path.casefold())
            if skill_identity in skill_identities:
                raise ValueError(f"creative skill registry duplicates skill path: {repository}/{path}")
            skill_identities.add(skill_identity)
    reviewed = data["reviewed_not_absorbed"]
    if not isinstance(reviewed, list):
        raise ValueError("creative skill registry.reviewed_not_absorbed must be a list")
    for index, item in enumerate(reviewed):
        if not isinstance(item, dict) or set(item) != {"repository", "reason"}:
            raise ValueError(f"reviewed_not_absorbed {index} fields are invalid")
        if not _repository_segments("github", item["repository"]):
            raise ValueError(f"reviewed_not_absorbed {index}.repository must be owner/repo")
        if item["repository"].casefold() in repositories:
            raise ValueError(f"reviewed repository is also absorbed: {item['repository']}")
        if not isinstance(item["reason"], str) or not item["reason"].strip():
            raise ValueError(f"reviewed_not_absorbed {index}.reason must be non-empty")


def load_spdx_ids(path: Path) -> set[str]:
    data = load_json_strict(path)
    fields = {
        "schema_version", "spdx_license_list_version", "source_url", "source_sha256",
        "license_ids_sha256", "retrieved_at", "policy", "license_ids",
    }
    if not isinstance(data, dict) or set(data) != fields or data["schema_version"] != 1:
        raise ValueError("SPDX policy fields/schema are invalid")
    version = data["spdx_license_list_version"]
    if not isinstance(version, str) or not version:
        raise ValueError("SPDX policy version is invalid")
    source = urlparse(data["source_url"] if isinstance(data["source_url"], str) else "")
    if source.scheme != "https" or not source.netloc or f"/v{version}/" not in source.path:
        raise ValueError("SPDX source_url must be HTTPS and pinned to its declared version")
    if not isinstance(data["source_sha256"], str) or not SHA256.fullmatch(data["source_sha256"]):
        raise ValueError("SPDX source_sha256 is invalid")
    try:
        retrieved = dt.date.fromisoformat(data["retrieved_at"])
    except (TypeError, ValueError) as exc:
        raise ValueError("SPDX retrieved_at must be ISO YYYY-MM-DD") from exc
    if retrieved > dt.datetime.now(dt.timezone.utc).date():
        raise ValueError("SPDX retrieved_at cannot be in the future")
    ids = data["license_ids"]
    if not _unique_strings(ids) or ids != sorted(ids):
        raise ValueError("SPDX license_ids must be sorted unique strings")
    if any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.+-]*", item) for item in ids):
        raise ValueError("SPDX license_ids must be single identifier tokens, not expressions")
    digest = hashlib.sha256(("\n".join(ids) + "\n").encode()).hexdigest()
    if data["license_ids_sha256"] != digest:
        raise ValueError("SPDX license_ids_sha256 differs from the declared set")
    forbidden = {"NOASSERTION"} | {item for item in ids if item.startswith(("LicenseRef-", "DocumentRef-"))}
    if forbidden & set(ids):
        raise ValueError("SPDX policy contains forbidden non-license identifiers")
    if not isinstance(data["policy"], str) or not data["policy"].strip():
        raise ValueError("SPDX policy.policy must be a non-empty statement")
    return set(ids)


def _repository_segments(provider: str, repository: object) -> list[str]:
    if not isinstance(repository, str):
        return []
    segments = repository.split("/")
    required = 2 if provider == "github" else 2
    if len(segments) < required or (provider == "github" and len(segments) != 2):
        return []
    if any(segment in {".", ".."} or not REPOSITORY_SEGMENT.fullmatch(segment) for segment in segments):
        return []
    return segments


def validate_catalog(rows, allowed_spdx: set[str] | None = None, spdx_path: Path | None = None) -> None:
    if not isinstance(rows, list) or not rows:
        raise ValueError("catalog must be a non-empty JSON list")
    if allowed_spdx is None:
        allowed_spdx = load_spdx_ids(spdx_path or ROOT / "maintenance" / "spdx-license-ids.json")
    names, repositories = set(), set()
    today = dt.datetime.now(dt.timezone.utc).date()
    for index, row in enumerate(rows):
        label = f"catalog row {index}"
        if not isinstance(row, dict):
            raise ValueError(f"{label} must be an object")
        missing = sorted((CATALOG_FIELDS - CATALOG_OPTIONAL_FIELDS) - set(row))
        unknown = sorted(set(row) - CATALOG_FIELDS)
        if missing or unknown:
            raise ValueError(f"{label} fields missing={missing} unknown={unknown}")
        for key in ("name", "license_hint", "best_for", "risk"):
            if not isinstance(row[key], str) or not row[key].strip():
                raise ValueError(f"{label}.{key} must be a non-empty string")
        for key in ("layer", "layer_family"):
            if not isinstance(row[key], str) or not SLUG.fullmatch(row[key]):
                raise ValueError(f"{label}.{key} must be a slug")
        if not _unique_strings(row["tags"], slugged=True):
            raise ValueError(f"{label}.tags must be unique non-empty slugs")
        provider = row.get("repository_provider", "github")
        if not isinstance(provider, str) or provider not in REPOSITORY_PROVIDERS:
            raise ValueError(f"{label}.repository_provider is unsupported")
        if not _repository_segments(provider, row["repository"]):
            raise ValueError(f"{label}.repository shape is invalid for {provider}")
        identity = (provider, row["repository"].casefold())
        if row["name"] in names or identity in repositories:
            raise ValueError(f"{label} duplicates name or provider/repository identity")
        names.add(row["name"])
        repositories.add(identity)
        for key in ("official_url", "license_source_url"):
            parsed = urlparse(row[key] if isinstance(row[key], str) else "")
            if parsed.scheme != "https" or not parsed.netloc:
                raise ValueError(f"{label}.{key} must be an absolute HTTPS URL")
        accepted = row["accepted_spdx"]
        if not isinstance(accepted, list) or not all(isinstance(item, str) for item in accepted):
            raise ValueError(f"catalog row {index}.accepted_spdx must contain valid SPDX ids")
        if len(accepted) != len(set(accepted)) or not all(
            item in allowed_spdx for item in accepted
        ):
            raise ValueError(f"{label}.accepted_spdx must contain unique governed SPDX IDs")
        if not isinstance(row["manual_license_review"], bool):
            raise ValueError(f"{label}.manual_license_review must be boolean")
        if not accepted and not row["manual_license_review"]:
            raise ValueError(f"{label} needs accepted_spdx or manual_license_review=true")
        for key in ("last_verified", "license_verified_at"):
            try:
                verified = dt.date.fromisoformat(row[key])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{label}.{key} must be ISO YYYY-MM-DD") from exc
            if verified > today:
                raise ValueError(f"{label}.{key} cannot be in the future")


def _license_status(catalog_row: dict, live_license: str) -> str:
    if live_license == "NOASSERTION" or catalog_row["manual_license_review"]:
        return "MANUAL_REVIEW"
    return "MATCH" if live_license in catalog_row["accepted_spdx"] else "MISMATCH"


def validate_audit_baseline(data: object, catalog: list[dict], root: Path = ROOT) -> None:
    if not isinstance(data, dict) or set(data) != {"audit_metadata", "rows", "failures"}:
        raise ValueError("audit baseline fields are missing or unknown")
    metadata, rows, failures = data["audit_metadata"], data["rows"], data["failures"]
    metadata_fields = {
        "schema_version", "audited_at", "catalog_sha256", "auditor_sha256",
        "catalog_count", "selected_count", "max_age_days", "status_counts", "failure_count",
    }
    if not isinstance(metadata, dict) or set(metadata) != metadata_fields or metadata["schema_version"] != 1:
        raise ValueError("audit baseline metadata is invalid")
    try:
        audited_at = dt.datetime.fromisoformat(metadata["audited_at"])
    except (TypeError, ValueError) as exc:
        raise ValueError("audit baseline audited_at must be ISO datetime") from exc
    if audited_at.tzinfo is None or audited_at > dt.datetime.now(dt.timezone.utc):
        raise ValueError("audit baseline audited_at must be timezone-aware and not future")
    catalog_path = root / "references" / "ecosystem-catalog.json"
    auditor_path = root / "maintenance" / "audit_ecosystem.py"
    if metadata["catalog_sha256"] != hashlib.sha256(catalog_path.read_bytes()).hexdigest():
        raise ValueError("audit baseline catalog hash differs from current catalog")
    if metadata["auditor_sha256"] != hashlib.sha256(auditor_path.read_bytes()).hexdigest():
        raise ValueError("audit baseline auditor hash differs from current script")
    if not isinstance(rows, list) or not isinstance(failures, list) or failures:
        raise ValueError("audit baseline must contain rows and zero operational failures")
    if metadata["failure_count"] != 0 or metadata["catalog_count"] != len(catalog) or metadata["selected_count"] != len(rows):
        raise ValueError("audit baseline counts differ from current catalog/results")
    catalog_by_identity = {
        (row.get("repository_provider", "github"), row["repository"].casefold()): row for row in catalog
    }
    row_fields = {
        "name", "layer", "layer_family", "repository", "repository_provider",
        "catalog_license", "license_source_url", "license_verified_at", "live_license",
        "license_status", "code_updated_at", "age_days", "archived", "status",
    }
    identities, status_counts = set(), {}
    max_age = metadata["max_age_days"]
    if not isinstance(max_age, int) or isinstance(max_age, bool) or max_age <= 0:
        raise ValueError("audit baseline max_age_days is invalid")
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != row_fields:
            raise ValueError(f"audit baseline row {index} fields are missing or unknown")
        identity = (row["repository_provider"], row["repository"].casefold()) if all(
            isinstance(row[key], str) for key in ("repository_provider", "repository")
        ) else None
        if identity not in catalog_by_identity or identity in identities:
            raise ValueError("audit baseline repository identities differ from current catalog")
        identities.add(identity)
        source = catalog_by_identity[identity]
        expected = {
            "name": source["name"], "layer": source["layer"],
            "layer_family": source["layer_family"], "catalog_license": source["license_hint"],
            "license_source_url": source["license_source_url"],
            "license_verified_at": source["license_verified_at"],
        }
        if any(row[key] != value for key, value in expected.items()):
            raise ValueError(f"audit baseline row {index} catalog fields differ")
        if not isinstance(row["live_license"], str) or not row["live_license"]:
            raise ValueError(f"audit baseline row {index} live_license is invalid")
        license_status = _license_status(source, row["live_license"])
        if row["license_status"] != license_status:
            raise ValueError(f"audit baseline row {index} license status is inconsistent")
        try:
            updated = dt.datetime.fromisoformat(row["code_updated_at"].replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc:
            raise ValueError(f"audit baseline row {index} code_updated_at is invalid") from exc
        age = (audited_at - updated).days
        if not isinstance(row["age_days"], int) or isinstance(row["age_days"], bool) or row["age_days"] != age:
            raise ValueError(f"audit baseline row {index} age is inconsistent")
        archived = row["archived"]
        if archived is not None and not isinstance(archived, bool):
            raise ValueError(f"audit baseline row {index} archived is invalid")
        status = (
            "ARCHIVED" if archived is True else
            "STALE_REVIEW" if age > max_age else
            "REPOSITORY_REVIEW" if not isinstance(archived, bool) else
            "LICENSE_REVIEW" if license_status != "MATCH" else "OK"
        )
        if row["status"] != status:
            raise ValueError(f"audit baseline row {index} status is inconsistent")
        status_counts[status] = status_counts.get(status, 0) + 1
    if identities != set(catalog_by_identity):
        raise ValueError("audit baseline repository identities differ from current catalog")
    if metadata["status_counts"] != dict(sorted(status_counts.items())):
        raise ValueError("audit baseline status counts differ from rows")


def validate_internal_links(root: Path = ROOT) -> None:
    markdown_link = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    local_code_path = re.compile(r"`((?:references|templates|scripts|maintenance|tests)/[^`\s]+)`")
    skill_root_path = re.compile(
        r"(?<![A-Za-z0-9_./-])(<skill-root>/(?:references|templates|scripts|maintenance|tests)/[A-Za-z0-9_./-]+)"
    )
    canonical = root.resolve()
    for source in root.rglob("*.md"):
        text = source.read_text(encoding="utf-8")
        targets = [match.group(1).split()[0] for match in markdown_link.finditer(text)]
        targets.extend(match.group(1) for match in local_code_path.finditer(text))
        targets.extend(match.group(1) for match in skill_root_path.finditer(text))
        for target in targets:
            if target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            target = target.removeprefix("<skill-root>/")
            base = root if target.split("/", 1)[0] in {"references", "templates", "scripts", "maintenance", "tests"} else source.parent
            resolved = (base / target).resolve()
            try:
                resolved.relative_to(canonical)
            except ValueError as exc:
                raise ValueError(f"{source.relative_to(root)} links outside skill: {target}") from exc
            if not resolved.exists():
                raise ValueError(f"{source.relative_to(root)} has broken local link: {target}")


def validate_portable_bundle_manifest(root: Path, skill_text: str) -> None:
    declared = {
        match.group(1).rstrip(".,;:") for match in PORTABLE_SUPPORT_REF.finditer(skill_text)
    }
    expected = {
        str(path.relative_to(root))
        for directory in PORTABLE_SUPPORT_DIRS
        for path in (root / directory).rglob("*")
        if path.is_file()
        and not path.is_symlink()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
        and not path.name.startswith(".")
    }
    missing = sorted(expected - declared)
    if missing:
        raise ValueError("portable bundle manifest omits support files: " + ", ".join(missing))


def validate_root(root: Path) -> int:
    skill = root / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    if len(text) > 100_000:
        raise ValueError("SKILL.md exceeds 100,000 characters")
    validate_frontmatter(parse_frontmatter(text))
    if "`references/capability-registry.json`" not in text:
        raise ValueError("SKILL.md must link the capability registry")
    registry = load_json_strict(root / "references" / "capability-registry.json")
    linked = validate_capability_registry(registry, root)
    ecosystem = registry["ecosystem"]
    catalog_path = root / ecosystem["production_tools"]
    spdx_path = root / "maintenance" / "spdx-license-ids.json"
    audit_path = root / "maintenance" / "ecosystem-audit-baseline.json"
    creative_skills_path = root / ecosystem["creative_skills"]
    validate_creative_skill_sources(load_json_strict(creative_skills_path))
    catalog = load_json_strict(catalog_path)
    validate_catalog(catalog, allowed_spdx=load_spdx_ids(spdx_path), spdx_path=spdx_path)
    validate_audit_baseline(load_json_strict(audit_path), catalog, root)
    validate_portable_bundle_manifest(root, text)
    if any(path.is_symlink() for path in root.rglob("*")):
        raise ValueError("portable skill tree must not contain symlinks")
    nested = sorted(path.relative_to(root) for path in root.rglob("SKILL.md") if path != skill)
    if nested:
        raise ValueError(f"nested skills are forbidden: {nested}")
    validate_internal_links(root)
    return 2 + len(linked)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT, help="Skill root to validate")
    parser.add_argument("--artifact-record", type=Path, help="Project artifact release record to validate")
    parser.add_argument("--project-root", type=Path, help="Project root containing artifact evidence")
    args = parser.parse_args()
    try:
        skill_root = args.root.resolve()
        checked = validate_root(skill_root)
        if (args.artifact_record is None) != (args.project_root is None):
            raise ValueError("--artifact-record and --project-root must be provided together")
        if args.artifact_record is not None and args.project_root is not None:
            registry = load_json_strict(skill_root / "references" / "capability-registry.json")
            record = load_json_strict(args.artifact_record.resolve())
            validate_artifact_record(record, registry, args.project_root.resolve(), skill_root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"validation failed: {exc}") from exc
    print(f"Validated mature-design-director: {checked} contract-linked files")
    if args.artifact_record is not None:
        print(f"Validated artifact release record: {args.artifact_record}")


if __name__ == "__main__":
    main()