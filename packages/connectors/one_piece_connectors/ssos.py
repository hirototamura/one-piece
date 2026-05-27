"""Minimal SSOS / ROS2 reverse-ingestion connector."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

TOPIC_PATTERN = re.compile(
    r"create_(?P<kind>publisher|subscription)\s*(?:<[^>]+>)?\s*\(\s*[^,]+,\s*[\"'](?P<topic>[^\"']+)[\"']"
)


def infer_discipline(name: str) -> str:
    lowered = name.lower()
    if "thermal" in lowered or "eclss" in lowered or "coolant" in lowered:
        return "thermal"
    if "power" in lowered or "battery" in lowered:
        return "electrical"
    if "comm" in lowered:
        return "communications"
    if "guidance" in lowered or "gnc" in lowered:
        return "gnc"
    return "software"


def _package_name(package_xml: Path) -> str:
    root = ET.fromstring(package_xml.read_text(encoding="utf-8"))
    name = root.findtext("name")
    if not name:
        raise ValueError(f"Package name not found in {package_xml}")
    return name.strip()


def ingest_ssos_repo(repo_path: Path) -> dict[str, Any]:
    package_files = sorted(repo_path.rglob("package.xml"))
    packages: list[dict[str, Any]] = []
    topics: dict[str, dict[str, list[str]]] = {}

    for package_xml in package_files:
        package_name = _package_name(package_xml)
        package_dir = package_xml.parent
        element_id = f"el-{package_name.replace('_', '-')}"
        packages.append(
            {
                "id": element_id,
                "name": package_name,
                "kind": "subsystem",
                "discipline": infer_discipline(package_name),
            }
        )

        for source in package_dir.rglob("*"):
            if source.suffix not in {".py", ".cpp", ".cc", ".hpp", ".h"}:
                continue
            try:
                text = source.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for match in TOPIC_PATTERN.finditer(text):
                topic = match.group("topic")
                kind = "publishers" if match.group("kind") == "publisher" else "subscribers"
                topics.setdefault(topic, {"publishers": [], "subscribers": []})
                if element_id not in topics[topic][kind]:
                    topics[topic][kind].append(element_id)

    icds: list[dict[str, Any]] = []
    interface_parameters: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for index, (topic, mapping) in enumerate(sorted(topics.items()), start=1):
        providers = mapping["publishers"] or mapping["subscribers"][:1]
        consumers = mapping["subscribers"] or mapping["publishers"][:1]
        provider = providers[0] if providers else packages[0]["id"]
        consumer = consumers[0] if consumers else packages[0]["id"]
        icd_id = f"icd-ssos-{index}"
        icds.append(
            {
                "id": icd_id,
                "key": f"ICD-SSOS-{index:03d}",
                "title": f"ROS2 topic {topic}",
                "state": "baseline",
                "providerElementId": provider,
                "consumerElementId": consumer,
                "scope": f"Auto-ingested from ROS2 topic graph: {topic}",
                "disciplines": ["software"],
            }
        )
        interface_parameters.append(
            {
                "id": f"ifp-ssos-{index}",
                "icdId": icd_id,
                "name": topic.split("/")[-1] or topic,
                "direction": "bidirectional",
                "dataType": "ros2_topic",
            }
        )
        traces.append(
            {
                "id": f"tr-ssos-{index}",
                "relation": "documents",
                "sourceId": icd_id,
                "targetId": provider,
            }
        )

    return {
        "requirements": [],
        "elements": packages,
        "traces": traces,
        "interfaceControlDocuments": icds,
        "interfaceParameters": interface_parameters,
        "designParameters": [],
        "designConstraints": [],
        "cadModels": [],
        "designArtifacts": [
            {
                "id": "art-ssos-source",
                "key": "SRC-SSOS",
                "name": "SSOS source repository",
                "kind": "source_repo",
                "sourcePath": str(repo_path),
                "revision": "workspace",
                "discipline": "software",
            }
        ],
        "cellCodeBindings": [],
    }
