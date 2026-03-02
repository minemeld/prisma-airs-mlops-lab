#!/usr/bin/env python3
"""
AIRS Model Security SDK - Local Test Harness

Tests all SDK operations locally without the full CI/CD pipeline.
Exercises: list_scans, get_scan, scan (local + GCS), both security groups.

Usage:
    # Load creds and run all tests
    python scripts/test_airs_sdk.py --all

    # Individual operations
    python scripts/test_airs_sdk.py --list-scans
    python scripts/test_airs_sdk.py --get-scan <UUID>
    python scripts/test_airs_sdk.py --scan-local <path> --group warn
    python scripts/test_airs_sdk.py --scan-gcs <gs://path> --group block
    python scripts/test_airs_sdk.py --scan-local <path> --group <UUID>

Creds: reads .env.superuser automatically.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from uuid import UUID
from datetime import datetime, timedelta

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Load creds from .env.superuser (project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env.superuser")

from model_security_client.api import ModelSecurityAPIClient

console = Console()

# ─────────────────────────────────────────────────────────────────────
# Security Group Registry
# Maps friendly names to UUIDs. Source type MUST match scan source.
# Replace placeholder UUIDs with YOUR tenant's values from
# SCM → AI Model Security → Security Groups (see Module 4.2).
# ─────────────────────────────────────────────────────────────────────
SECURITY_GROUPS = {
    # Custom groups (create these in SCM or use defaults)
    "warn": {
        "uuid": UUID("00000000-0000-0000-0000-000000000004"),
        "name": "GCS - Staging Area (warn-only)",
        "source": "GCS",
    },
    "block": {
        "uuid": UUID("00000000-0000-0000-0000-000000000005"),
        "name": "GCS - MLOps Lab Build (blocking-all)",
        "source": "GCS",
    },
    # Default groups (auto-created by SCM)
    "local": {
        "uuid": UUID("00000000-0000-0000-0000-000000000001"),
        "name": "Default LOCAL",
        "source": "LOCAL",
    },
    "gcs-default": {
        "uuid": UUID("00000000-0000-0000-0000-000000000002"),
        "name": "Default GCS",
        "source": "GCS",
    },
    "hf": {
        "uuid": UUID("00000000-0000-0000-0000-000000000003"),
        "name": "Default HUGGING_FACE",
        "source": "HUGGING_FACE",
    },
}

API_URL = os.environ.get(
    "MODEL_SECURITY_API_ENDPOINT",
    "https://api.sase.paloaltonetworks.com/aims",
)


def resolve_group(name_or_uuid: str) -> dict:
    """Resolve a group name or UUID string to a group dict."""
    if name_or_uuid in SECURITY_GROUPS:
        return SECURITY_GROUPS[name_or_uuid]
    try:
        uid = UUID(name_or_uuid)
        return {"uuid": uid, "name": f"Custom ({name_or_uuid})", "source": "?"}
    except ValueError:
        console.print(f"[red]Unknown group: {name_or_uuid}[/red]")
        console.print(f"Available: {', '.join(SECURITY_GROUPS.keys())}")
        sys.exit(1)


def get_client() -> ModelSecurityAPIClient:
    """Create an authenticated SDK client."""
    client_id = os.environ.get("AIRS_MS_CLIENT_ID")
    client_secret = os.environ.get("AIRS_MS_CLIENT_SECRET")
    tsg_id = os.environ.get("TSG_ID")

    if not client_id or not client_secret:
        console.print("[red]Missing AIRS_MS_CLIENT_ID / AIRS_MS_CLIENT_SECRET[/red]")
        console.print("Ensure .env.superuser is present and has credentials.")
        sys.exit(1)

    console.print(f"[dim]API:    {API_URL}[/dim]")
    console.print(f"[dim]Client: {client_id[:30]}...[/dim]")
    console.print(f"[dim]TSG:    {tsg_id}[/dim]")
    console.print()

    return ModelSecurityAPIClient(base_url=API_URL, timeout=30.0)


def dump_response(resp, label: str = "Response"):
    """Pretty-print a scan response object."""
    if hasattr(resp, "model_dump"):
        data = resp.model_dump()
    else:
        data = dict(resp) if resp else {}

    # Serialize for display (handles UUIDs, datetimes, enums)
    text = json.dumps(data, indent=2, default=str)
    console.print(Panel(text, title=label, border_style="blue", expand=False))
    return data


def print_scan_row(scan, table: Table):
    """Add a scan to a Rich table."""
    if hasattr(scan, "model_dump"):
        d = scan.model_dump()
    else:
        d = dict(scan)

    outcome = str(d.get("eval_outcome", "?")).split(".")[-1]
    style = "green" if outcome == "ALLOWED" else "red" if outcome == "BLOCKED" else "yellow"
    summary = d.get("eval_summary") or {}
    passed = summary.get("rules_passed", "?")
    failed = summary.get("rules_failed", "?")
    total = summary.get("total_rules", "?")
    formats = ", ".join(d.get("model_formats", []) or [])
    created = str(d.get("created_at", ""))[:19]
    sg_name = d.get("security_group_name", "?")
    source = str(d.get("source_type", "?")).split(".")[-1]

    table.add_row(
        str(d.get("uuid", "?"))[:12] + "...",
        f"[{style}]{outcome}[/{style}]",
        f"{passed}/{total} pass, {failed}/{total} fail",
        source,
        sg_name,
        formats[:40],
        created,
    )


# ─────────────────────────────────────────────────────────────────────
# Operations
# ─────────────────────────────────────────────────────────────────────

def op_list_scans(client, limit=10, source_types=None, eval_outcomes=None):
    """List recent scans with optional filters."""
    console.rule("[bold]LIST SCANS[/bold]")

    kwargs = {"limit": limit}
    if source_types:
        from airs_schemas.constants import SourceType
        kwargs["source_types"] = [SourceType(s) for s in source_types]
    if eval_outcomes:
        from airs_schemas.constants import EvalOutcome
        kwargs["eval_outcomes"] = [EvalOutcome(o) for o in eval_outcomes]

    result = client.list_scans(**kwargs)

    scans = result.scans if hasattr(result, "scans") else result.get("scans", [])

    table = Table(title=f"Recent Scans (limit={limit})", box=box.ROUNDED)
    table.add_column("Scan ID", style="cyan")
    table.add_column("Verdict")
    table.add_column("Rules")
    table.add_column("Source")
    table.add_column("Security Group")
    table.add_column("Formats")
    table.add_column("Created")

    for scan in scans:
        print_scan_row(scan, table)

    console.print(table)

    if hasattr(result, "pagination"):
        p = result.pagination
        total = p.total_items if hasattr(p, "total_items") else "?"
        console.print(f"[dim]Total scans: {total}[/dim]")

    return scans


def op_get_scan(client, scan_uuid: str):
    """Retrieve a specific scan by UUID."""
    console.rule("[bold]GET SCAN[/bold]")
    console.print(f"Fetching scan: [cyan]{scan_uuid}[/cyan]")

    result = client.get_scan(scan_id=UUID(scan_uuid))
    data = dump_response(result, f"Scan {scan_uuid[:12]}...")

    # Highlight key fields
    outcome = str(data.get("eval_outcome", "?")).split(".")[-1]
    style = "green" if outcome == "ALLOWED" else "red"
    console.print(f"\nVerdict: [{style}]{outcome}[/{style}]")
    console.print(f"Security Group: {data.get('security_group_name')}")
    console.print(f"Formats: {data.get('model_formats')}")

    return data


def op_scan_local(client, model_path: str, group_key: str):
    """Scan a local model directory."""
    group = resolve_group(group_key)

    if group["source"] != "LOCAL" and group["source"] != "?":
        console.print(f"[yellow]Warning: Group '{group['name']}' is {group['source']} source, "
                       f"but scanning a LOCAL path. This may fail![/yellow]")
        console.print(f"[yellow]Use --group local for local scans.[/yellow]")

    console.rule("[bold]SCAN LOCAL MODEL[/bold]")
    console.print(f"Path:  [cyan]{model_path}[/cyan]")
    console.print(f"Group: [cyan]{group['name']}[/cyan] ({group['uuid']})")

    abs_path = Path(model_path).resolve()
    if not abs_path.exists():
        console.print(f"[red]Path not found: {abs_path}[/red]")
        sys.exit(1)

    # List files to scan
    files = list(abs_path.rglob("*"))
    model_files = [f for f in files if f.is_file()]
    console.print(f"Files: {len(model_files)} files in directory")
    for f in model_files[:10]:
        console.print(f"  [dim]{f.relative_to(abs_path)}[/dim]")
    if len(model_files) > 10:
        console.print(f"  [dim]... and {len(model_files) - 10} more[/dim]")

    console.print()
    with console.status("[green]Scanning model...[/green]"):
        result = client.scan(
            security_group_uuid=group["uuid"],
            model_path=str(abs_path),
            poll_timeout_secs=600,
        )

    data = dump_response(result, "Scan Result")

    outcome = str(data.get("eval_outcome", "?")).split(".")[-1]
    style = "green" if outcome == "ALLOWED" else "red"
    console.print(f"\nVerdict: [{style}]{outcome}[/{style}]")

    return data


def op_scan_gcs(client, gcs_uri: str, group_key: str):
    """Scan a model in GCS (AIRS service pulls it directly)."""
    group = resolve_group(group_key)

    if group["source"] not in ("GCS", "?"):
        console.print(f"[yellow]Warning: Group '{group['name']}' is {group['source']} source, "
                       f"but scanning a GCS path. This may fail![/yellow]")

    console.rule("[bold]SCAN GCS MODEL[/bold]")
    console.print(f"URI:   [cyan]{gcs_uri}[/cyan]")
    console.print(f"Group: [cyan]{group['name']}[/cyan] ({group['uuid']})")
    console.print()
    console.print("[dim]Note: The AIRS service pulls the model from GCS directly.[/dim]")
    console.print("[dim]The service needs access to your GCS bucket.[/dim]")

    console.print()
    with console.status("[green]Scanning model via GCS...[/green]"):
        result = client.scan(
            security_group_uuid=group["uuid"],
            model_uri=gcs_uri,
            poll_timeout_secs=600,
        )

    data = dump_response(result, "Scan Result")

    outcome = str(data.get("eval_outcome", "?")).split(".")[-1]
    style = "green" if outcome == "ALLOWED" else "red"
    console.print(f"\nVerdict: [{style}]{outcome}[/{style}]")

    return data


def op_scan_hf(client, hf_repo: str, group_key: str = "hf"):
    """Scan a HuggingFace model."""
    group = resolve_group(group_key)

    console.rule("[bold]SCAN HUGGINGFACE MODEL[/bold]")
    console.print(f"Repo:  [cyan]{hf_repo}[/cyan]")
    console.print(f"Group: [cyan]{group['name']}[/cyan] ({group['uuid']})")

    console.print()
    with console.status("[green]Scanning HuggingFace model...[/green]"):
        result = client.scan(
            security_group_uuid=group["uuid"],
            model_uri=hf_repo,
            poll_timeout_secs=600,
        )

    data = dump_response(result, "Scan Result")

    outcome = str(data.get("eval_outcome", "?")).split(".")[-1]
    style = "green" if outcome == "ALLOWED" else "red"
    console.print(f"\nVerdict: [{style}]{outcome}[/{style}]")

    return data


def op_run_all(client):
    """Run a comprehensive test suite."""
    console.rule("[bold cyan]AIRS SDK TEST SUITE[/bold cyan]", style="cyan")
    console.print()

    # Print security group registry
    table = Table(title="Security Group Registry", box=box.ROUNDED)
    table.add_column("Key", style="cyan")
    table.add_column("Name")
    table.add_column("Source")
    table.add_column("UUID")
    for key, g in SECURITY_GROUPS.items():
        table.add_row(key, g["name"], g["source"], str(g["uuid"]))
    console.print(table)
    console.print()

    # Test 1: List scans (verifies credentials)
    console.print("[bold]Test 1: List recent scans (credential check)[/bold]")
    try:
        scans = op_list_scans(client, limit=5)
        console.print("[green]PASS - Credentials work, API reachable[/green]\n")
    except Exception as e:
        console.print(f"[red]FAIL - {e}[/red]\n")
        return

    # Test 2: Get scan by UUID (if we have scans)
    if scans:
        first_scan = scans[0]
        scan_uuid = str(first_scan.uuid if hasattr(first_scan, "uuid") else first_scan.get("uuid"))
        console.print(f"[bold]Test 2: Get scan by UUID ({scan_uuid[:12]}...)[/bold]")
        try:
            op_get_scan(client, scan_uuid)
            console.print("[green]PASS - get_scan works[/green]\n")
        except Exception as e:
            console.print(f"[red]FAIL - {e}[/red]\n")

    # Test 3: List with filters
    console.print("[bold]Test 3: List scans filtered by BLOCKED verdict[/bold]")
    try:
        blocked = op_list_scans(client, limit=5, eval_outcomes=["BLOCKED"])
        console.print("[green]PASS - Filtered list works[/green]\n")
    except Exception as e:
        console.print(f"[red]FAIL - {e}[/red]\n")

    # Test 4: GCS scan with warn-only group
    console.print("[bold]Test 4: GCS scan (warn-only group)[/bold]")
    console.print("[yellow]Scanning gs://jlimon-airs-lab/approved-models/cloud-security-advisor/ with warn group[/yellow]")
    try:
        op_scan_gcs(client, "gs://jlimon-airs-lab/approved-models/cloud-security-advisor/", "warn")
        console.print("[green]PASS - GCS warn scan works[/green]\n")
    except Exception as e:
        console.print(f"[red]FAIL - {e}[/red]\n")
        console.print("[dim]This may fail if AIRS service doesn't have GCS access.[/dim]\n")

    # Test 5: GCS scan with blocking group
    console.print("[bold]Test 5: GCS scan (blocking-all group)[/bold]")
    console.print("[yellow]Scanning same model with blocking group[/yellow]")
    try:
        op_scan_gcs(client, "gs://jlimon-airs-lab/approved-models/cloud-security-advisor/", "block")
        console.print("[green]PASS - GCS block scan works[/green]\n")
    except Exception as e:
        console.print(f"[red]FAIL - {e}[/red]\n")

    console.rule("[bold cyan]TEST SUITE COMPLETE[/bold cyan]", style="cyan")


def parse_args():
    parser = argparse.ArgumentParser(
        description="AIRS Model Security SDK - Local Test Harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Security Group Keys:
  warn         GCS - Staging Area (all rules warn-only)
  block        GCS - MLOps Lab Build (all rules blocking)
  local        Default LOCAL
  gcs-default  Default GCS
  hf           Default HUGGING_FACE
  <UUID>       Any UUID directly

Examples:
  python scripts/test_airs_sdk.py --all
  python scripts/test_airs_sdk.py --list-scans --limit 20
  python scripts/test_airs_sdk.py --list-scans --eval-outcomes BLOCKED
  python scripts/test_airs_sdk.py --get-scan 9faaf8b5-a594-49ce-bc7c-dbab90a94a52
  python scripts/test_airs_sdk.py --scan-local ./model-download --group local
  python scripts/test_airs_sdk.py --scan-gcs gs://jlimon-airs-lab/approved-models/cloud-security-advisor/ --group warn
  python scripts/test_airs_sdk.py --scan-gcs gs://jlimon-airs-lab/approved-models/cloud-security-advisor/ --group block
  python scripts/test_airs_sdk.py --scan-hf https://huggingface.co/Qwen/Qwen2.5-3B-Instruct
        """,
    )

    parser.add_argument("--all", action="store_true", help="Run full test suite")

    # List scans
    parser.add_argument("--list-scans", action="store_true", help="List recent scans")
    parser.add_argument("--limit", type=int, default=10, help="Max scans to list")
    parser.add_argument("--source-types", nargs="*", help="Filter: LOCAL, GCS, HUGGING_FACE, etc.")
    parser.add_argument("--eval-outcomes", nargs="*", help="Filter: ALLOWED, BLOCKED, PENDING, ERROR")

    # Get scan
    parser.add_argument("--get-scan", type=str, help="Get scan by UUID")

    # Scan operations
    parser.add_argument("--scan-local", type=str, help="Scan a local model directory")
    parser.add_argument("--scan-gcs", type=str, help="Scan a GCS model URI (gs://...)")
    parser.add_argument("--scan-hf", type=str, help="Scan a HuggingFace model URI")
    parser.add_argument("--group", type=str, default="local",
                        help="Security group key or UUID (warn, block, local, gcs-default, hf)")

    # Output
    parser.add_argument("--output-json", type=str, help="Save result JSON to file")

    return parser.parse_args()


def main():
    args = parse_args()
    client = get_client()
    result = None

    try:
        # Auto-select security group based on scan type if user didn't override
        group = args.group
        if group == "local":  # default value - auto-detect from scan type
            if args.scan_gcs:
                group = "gcs-default"
            elif args.scan_hf:
                group = "hf"

        if args.all:
            op_run_all(client)
        elif args.list_scans:
            op_list_scans(client, limit=args.limit,
                          source_types=args.source_types,
                          eval_outcomes=args.eval_outcomes)
        elif args.get_scan:
            result = op_get_scan(client, args.get_scan)
        elif args.scan_local:
            result = op_scan_local(client, args.scan_local, group)
        elif args.scan_gcs:
            result = op_scan_gcs(client, args.scan_gcs, group)
        elif args.scan_hf:
            result = op_scan_hf(client, args.scan_hf, group)
        else:
            console.print("[yellow]No operation specified. Use --help for usage.[/yellow]")
            console.print()
            # Show quick info
            console.print("[bold]Available security groups:[/bold]")
            for key, g in SECURITY_GROUPS.items():
                console.print(f"  [cyan]{key:12s}[/cyan] {g['name']} ({g['source']})")
            console.print()
            console.print("[bold]Quick start:[/bold]")
            console.print("  python scripts/test_airs_sdk.py --list-scans")
            console.print("  python scripts/test_airs_sdk.py --all")
    finally:
        client.close()

    if result and args.output_json:
        with open(args.output_json, "w") as f:
            json.dump(result, f, indent=2, default=str)
        console.print(f"\n[dim]Saved to: {args.output_json}[/dim]")


if __name__ == "__main__":
    main()
