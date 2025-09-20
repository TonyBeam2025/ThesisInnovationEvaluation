#!/usr/bin/env python
"""Tool to authenticate with CNKI and run a manual search focusing on pre-date filters."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from thesis_inno_eval.cnki_client_pool import CNKIClient, get_token, normalize_cnki_pt_upper
from thesis_inno_eval.config_manager import get_config_manager


def _resolve_uniplatform() -> Optional[str]:
    try:
        config_mgr = get_config_manager()
        endpoints = config_mgr.get_cnki_api_endpoints()
        candidate = endpoints.get("uniplatform")
        if candidate:
            return candidate
    except Exception:
        pass
    return os.environ.get("CNKI_UNIPLATFORM")


def _load_credentials() -> tuple[str, str]:
    client_id = os.environ.get("CNKI_CLIENT_ID")
    client_secret = os.environ.get("CNKI_CLIENT_SECRET")
    if not client_id or not client_secret:
        missing = []
        if not client_id:
            missing.append("CNKI_CLIENT_ID")
        if not client_secret:
            missing.append("CNKI_CLIENT_SECRET")
        raise RuntimeError(f"Missing CNKI credentials: {', '.join(missing)}")
    return client_id, client_secret


def _pretty_print(result: dict, limit: int) -> None:
    collections = result.get("searchResultsCollections", {})
    total = collections.get("total")
    items = collections.get("items", [])
    print(f"Total matches: {total}")
    for idx, item in enumerate(items[:limit], start=1):
        title = item.get("Title") or item.get("metadata", {}).get("TI")
        year = item.get("PublicationYear")
        pt_value = None
        for meta in item.get("metadata", []):
            if meta.get("name") == "PT":
                pt_value = meta.get("value")
                break
        print(f"[{idx}] {title} ({year}), PT={pt_value}")
    if len(items) > limit:
        print(f"... {len(items) - limit} more items not shown ...")




def _build_example_query_payload(expression: str, lang: str, pt_upper: str, size: int = 50) -> dict:
    product = 'WWJD,WWPD' if lang == 'English' else 'CJFD,CDFD,CMFD,CPFD,CCND,IPFD,CAPJ'
    return {
        'resource': 'CROSSDB',
        'product': product,
        'extend': 1,
        'start': 1,
        'size': size,
        'sort': 'PT',
        'sequence': 'DESC',
        'select': 'TI,AB,KY,DB,LY,YE,PT',
        'q': {
            'logic': 'AND',
            'items': [
                {
                    'logic': 'AND',
                    'operator': '',
                    'uf': 'EXPERT',
                    'uv': expression
                },
                {
                    'logic': 'AND',
                    'operator': 'LE',
                    'uf': 'PT',
                    'uv': pt_upper
                }
            ],
            'childItems': []
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a direct CNKI search with a boolean expression and publication-time filter."
    )
    parser.add_argument(
        "--expression",
        default="TI='ecology' and KY='Ecological Civilization'",
        help="Boolean expression for the EXPERT field (default targets ecology/ecological civilization).",
    )
    parser.add_argument(
        "--lang",
        default="Chinese",
        choices=["Chinese", "English"],
        help="CNKI search language channel (affects corpus and product selection).",
    )
    parser.add_argument(
        "--pt-upper",
        default="20150627",
        help="Upper bound for publication date (PT) in YYYYMMDD format.",
    )
    parser.add_argument(
        "--show",
        type=int,
        default=5,
        help="Number of records to display from the response (default 5).",
    )
    parser.add_argument(
        "--output",
        default="cnki_manual_search_result.json",
        help="Path to store the raw JSON response (default cnki_manual_search_result.json).",
    )
    args = parser.parse_args()

    uniplatform = _resolve_uniplatform()
    if not uniplatform:
        raise RuntimeError("Unable to resolve CNKI uniplatform identifier from config or environment.")

    client_id, client_secret = _load_credentials()
    token_payload = get_token(client_id, client_secret)
    access_token = token_payload.get("access_token") if token_payload else None
    if not access_token:
        raise RuntimeError("Failed to obtain CNKI access token.")

    client = CNKIClient(uniplatform, access_token)
    pt_upper = normalize_cnki_pt_upper(args.pt_upper)
    if not pt_upper:
        raise ValueError("Provided PT upper bound is not a valid date.")

    print(f"Executing CNKI search with PT<= {pt_upper} using expression: {args.expression}")
    example_payload = _build_example_query_payload(args.expression, args.lang, pt_upper)
    print('Request payload preview:')
    print(json.dumps(example_payload, ensure_ascii=False, indent=2))
    result = client.call_cnki_api_raw_http(args.expression, lang=args.lang, pt_upper=pt_upper)

    if not result:
        print("No data returned from CNKI API.")
        return

    _pretty_print(result, args.show)
    output_path = Path(args.output).resolve()
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    print(f"Full response written to {output_path}")


if __name__ == "__main__":
    main()
