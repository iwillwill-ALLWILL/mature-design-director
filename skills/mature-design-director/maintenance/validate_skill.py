#!/usr/bin/env python3
"""Validate the portable mature-design-director contracts without cataloguing capabilities in code."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
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
    "schema_version", "skill", "authority", "flow", "evidence_types", "capabilities",
    "ecosystem", "resources", "learning",
}
CAPABILITY_FIELDS = {"id", "contract", "accepts", "outputs", "delegates", "evidence"}
PORTABLE_SUPPORT_DIRS = ("references", "templates", "scripts")
PORTABLE_SUPPORT_REF = re.compile(
    r"`((?:references|templates|scripts)/[^`\s]+)`"
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
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and len(value) == len(set(value))
        and all(isinstance(item, str) and item and (not slugged or SLUG.fullmatch(item)) for item in value)
    )


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


def validate_capability_registry(data: object, root: Path = ROOT) -> set[str]:
    if not isinstance(data, dict) or set(data) != REGISTRY_FIELDS:
        raise ValueError("capability registry fields are missing or unknown")
    if data["schema_version"] != 3 or data["skill"] != "mature-design-director":
        raise ValueError("capability registry identity/schema is invalid")
    authority = data["authority"]
    if not isinstance(authority, dict) or set(authority) != {"owns", "delegates", "composition_rule"}:
        raise ValueError("capability registry authority is invalid")
    if not _unique_strings(authority["owns"], slugged=True) or not _unique_strings(authority["delegates"], slugged=True):
        raise ValueError("authority owns/delegates must be unique slug lists")
    if not isinstance(authority["composition_rule"], str) or not authority["composition_rule"]:
        raise ValueError("authority composition_rule is invalid")

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
        for key in ("accepts", "outputs", "evidence"):
            if not _unique_strings(capability[key], slugged=True):
                raise ValueError(f"{label}.{key} must be a non-empty unique slug list")
        unknown_evidence = sorted(set(capability["evidence"]) - set(evidence))
        if unknown_evidence:
            raise ValueError(f"{label} references unknown evidence: {unknown_evidence}")
        delegates = capability["delegates"]
        if not isinstance(delegates, list):
            raise ValueError(f"{label}.delegates must be a list")
        roles = set()
        for offset, delegation in enumerate(delegates):
            if not isinstance(delegation, dict) or set(delegation) != {"role", "candidates"}:
                raise ValueError(f"{label}.delegates[{offset}] fields are invalid")
            role = delegation["role"]
            if not isinstance(role, str) or not SLUG.fullmatch(role) or role in roles:
                raise ValueError(f"{label}.delegates[{offset}].role must be a unique slug")
            if not _unique_strings(delegation["candidates"], slugged=True):
                raise ValueError(f"{label}.delegates[{offset}].candidates must be unique slugs")
            roles.add(role)

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
    if data["schema_version"] != 1:
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
        if source["url"].casefold() != expected_url.casefold():
            raise ValueError(f"{label}.url must match repository")
        if not isinstance(source["maintainer_class"], str) or not source["maintainer_class"].strip():
            raise ValueError(f"{label}.maintainer_class must be non-empty")
        if not isinstance(source["stars_at_verification"], int) or source["stars_at_verification"] < 0:
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
    data = json.loads(path.read_text(encoding="utf-8"))
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
        if not isinstance(accepted, list) or len(accepted) != len(set(accepted)) or not all(
            isinstance(item, str) and item in allowed_spdx for item in accepted
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
    local_code_path = re.compile(r"`((?:references|templates|scripts|tests)/[^`\s]+)`")
    skill_root_path = re.compile(
        r"(?<![A-Za-z0-9_./-])(<skill-root>/(?:references|templates|scripts|tests)/[A-Za-z0-9_./-]+)"
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
            base = root if target.split("/", 1)[0] in {"references", "templates", "scripts", "tests"} else source.parent
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
    registry = json.loads((root / "references" / "capability-registry.json").read_text(encoding="utf-8"))
    linked = validate_capability_registry(registry, root)
    ecosystem = registry["ecosystem"]
    catalog_path = root / ecosystem["production_tools"]
    spdx_path = root / "maintenance" / "spdx-license-ids.json"
    audit_path = root / "maintenance" / "ecosystem-audit-baseline.json"
    creative_skills_path = root / ecosystem["creative_skills"]
    validate_creative_skill_sources(json.loads(creative_skills_path.read_text(encoding="utf-8")))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    validate_catalog(catalog, allowed_spdx=load_spdx_ids(spdx_path), spdx_path=spdx_path)
    validate_audit_baseline(json.loads(audit_path.read_text(encoding="utf-8")), catalog, root)
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
    args = parser.parse_args()
    try:
        checked = validate_root(args.root.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"validation failed: {exc}") from exc
    print(f"Validated mature-design-director: {checked} contract-linked files")


if __name__ == "__main__":
    main()