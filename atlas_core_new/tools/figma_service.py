"""
Figma Integration Service — Design Intelligence for Atlas Core

Connects to the Figma REST API to pull design files, components, styles,
and rendered images into the Atlas ecosystem.

Authentication: Uses FIGMA_API_KEY environment variable (Personal Access Token)
API Base: https://api.figma.com/v1
"""

import os
import requests
from typing import Optional

FIGMA_API_BASE = "https://api.figma.com/v1"


def _get_headers() -> dict:
    token = os.environ.get("FIGMA_API_KEY", "")
    return {"X-FIGMA-TOKEN": token}


def _has_token() -> bool:
    return bool(os.environ.get("FIGMA_API_KEY", "").strip())


def get_connection_status() -> dict:
    if not _has_token():
        return {"connected": False, "reason": "No Figma API key configured"}
    try:
        r = requests.get(f"{FIGMA_API_BASE}/me", headers=_get_headers(), timeout=10)
        if r.status_code == 200:
            user = r.json()
            return {
                "connected": True,
                "user": {
                    "id": user.get("id"),
                    "handle": user.get("handle"),
                    "email": user.get("email"),
                    "img_url": user.get("img_url"),
                },
            }
        elif r.status_code == 403:
            return {"connected": False, "reason": "API key is invalid or expired"}
        else:
            return {"connected": False, "reason": f"Figma API returned status {r.status_code}"}
    except requests.exceptions.Timeout:
        return {"connected": False, "reason": "Connection timed out"}
    except Exception as e:
        return {"connected": False, "reason": str(e)}


def get_file(file_key: str, depth: Optional[int] = 2) -> dict:
    if not _has_token():
        return {"error": "No Figma API key configured"}
    try:
        params = {}
        if depth is not None:
            params["depth"] = depth
        r = requests.get(
            f"{FIGMA_API_BASE}/files/{file_key}",
            headers=_get_headers(),
            params=params,
            timeout=30,
        )
        if r.status_code == 200:
            data = r.json()
            return {
                "name": data.get("name"),
                "lastModified": data.get("lastModified"),
                "version": data.get("version"),
                "role": data.get("role"),
                "thumbnailUrl": data.get("thumbnailUrl"),
                "pages": _extract_pages(data.get("document", {})),
                "components": _summarize_components(data.get("components", {})),
                "styles": _summarize_styles(data.get("styles", {})),
            }
        elif r.status_code == 404:
            return {"error": "File not found — check the file key"}
        elif r.status_code == 403:
            return {"error": "Access denied — check your API key permissions"}
        else:
            return {"error": f"Figma API error: {r.status_code}"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out — file may be very large"}
    except Exception as e:
        return {"error": str(e)}


def get_file_images(file_key: str, node_ids: list, fmt: str = "png", scale: float = 2) -> dict:
    if not _has_token():
        return {"error": "No Figma API key configured"}
    if not node_ids:
        return {"error": "No node IDs provided"}
    try:
        r = requests.get(
            f"{FIGMA_API_BASE}/images/{file_key}",
            headers=_get_headers(),
            params={
                "ids": ",".join(node_ids),
                "format": fmt,
                "scale": scale,
            },
            timeout=30,
        )
        if r.status_code == 200:
            data = r.json()
            return {
                "images": data.get("images", {}),
                "err": data.get("err"),
            }
        else:
            return {"error": f"Figma API error: {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def get_file_components(file_key: str) -> dict:
    if not _has_token():
        return {"error": "No Figma API key configured"}
    try:
        r = requests.get(
            f"{FIGMA_API_BASE}/files/{file_key}/components",
            headers=_get_headers(),
            timeout=20,
        )
        if r.status_code == 200:
            data = r.json()
            meta = data.get("meta", {})
            components = meta.get("components", [])
            return {
                "count": len(components),
                "components": [
                    {
                        "key": c.get("key"),
                        "name": c.get("name"),
                        "description": c.get("description"),
                        "node_id": c.get("node_id"),
                        "thumbnail_url": c.get("thumbnail_url"),
                        "containing_frame": c.get("containing_frame", {}).get("name"),
                    }
                    for c in components
                ],
            }
        else:
            return {"error": f"Figma API error: {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def get_file_styles(file_key: str) -> dict:
    if not _has_token():
        return {"error": "No Figma API key configured"}
    try:
        r = requests.get(
            f"{FIGMA_API_BASE}/files/{file_key}/styles",
            headers=_get_headers(),
            timeout=20,
        )
        if r.status_code == 200:
            data = r.json()
            meta = data.get("meta", {})
            styles = meta.get("styles", [])
            return {
                "count": len(styles),
                "styles": [
                    {
                        "key": s.get("key"),
                        "name": s.get("name"),
                        "description": s.get("description"),
                        "style_type": s.get("style_type"),
                        "node_id": s.get("node_id"),
                        "thumbnail_url": s.get("thumbnail_url"),
                    }
                    for s in styles
                ],
            }
        else:
            return {"error": f"Figma API error: {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def extract_colors_from_file(file_key: str) -> dict:
    if not _has_token():
        return {"error": "No Figma API key configured"}
    try:
        r = requests.get(
            f"{FIGMA_API_BASE}/files/{file_key}",
            headers=_get_headers(),
            params={"depth": 1},
            timeout=30,
        )
        if r.status_code != 200:
            return {"error": f"Figma API error: {r.status_code}"}

        data = r.json()
        styles = data.get("styles", {})
        color_styles = {
            k: v for k, v in styles.items()
            if v.get("styleType") == "FILL"
        }

        r2 = requests.get(
            f"{FIGMA_API_BASE}/files/{file_key}/styles",
            headers=_get_headers(),
            timeout=20,
        )
        fill_styles = []
        if r2.status_code == 200:
            meta = r2.json().get("meta", {})
            for s in meta.get("styles", []):
                if s.get("style_type") == "FILL":
                    fill_styles.append({
                        "name": s.get("name"),
                        "description": s.get("description"),
                        "node_id": s.get("node_id"),
                    })

        return {
            "file_name": data.get("name"),
            "color_style_count": len(color_styles),
            "fill_styles": fill_styles,
        }
    except Exception as e:
        return {"error": str(e)}


def get_node_details(file_key: str, node_ids: list) -> dict:
    if not _has_token():
        return {"error": "No Figma API key configured"}
    try:
        r = requests.get(
            f"{FIGMA_API_BASE}/files/{file_key}/nodes",
            headers=_get_headers(),
            params={"ids": ",".join(node_ids)},
            timeout=30,
        )
        if r.status_code == 200:
            data = r.json()
            nodes = data.get("nodes", {})
            result = {}
            for node_id, node_data in nodes.items():
                doc = node_data.get("document", {})
                result[node_id] = {
                    "name": doc.get("name"),
                    "type": doc.get("type"),
                    "children_count": len(doc.get("children", [])),
                    "absoluteBoundingBox": doc.get("absoluteBoundingBox"),
                }
            return {"nodes": result}
        else:
            return {"error": f"Figma API error: {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def parse_figma_url(url: str) -> dict:
    import re
    patterns = [
        r"figma\.com/(?:file|design)/([a-zA-Z0-9]+)",
        r"figma\.com/proto/([a-zA-Z0-9]+)",
        r"figma\.com/board/([a-zA-Z0-9]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            file_key = match.group(1)
            node_id = None
            node_match = re.search(r"node-id=([0-9]+-[0-9]+)", url)
            if node_match:
                node_id = node_match.group(1).replace("-", ":")
            return {"file_key": file_key, "node_id": node_id}
    return {"error": "Could not parse Figma URL — make sure it's a valid Figma file link"}


def _extract_pages(document: dict) -> list:
    pages = []
    for child in document.get("children", []):
        if child.get("type") == "CANVAS":
            pages.append({
                "id": child.get("id"),
                "name": child.get("name"),
                "children_count": len(child.get("children", [])),
                "backgroundColor": child.get("backgroundColor"),
            })
    return pages


def _summarize_components(components: dict) -> list:
    result = []
    for node_id, comp in components.items():
        result.append({
            "node_id": node_id,
            "name": comp.get("name"),
            "description": comp.get("description"),
        })
    return result[:50]


def _summarize_styles(styles: dict) -> list:
    result = []
    for node_id, style in styles.items():
        result.append({
            "node_id": node_id,
            "name": style.get("name"),
            "type": style.get("styleType"),
            "description": style.get("description"),
        })
    return result[:50]
