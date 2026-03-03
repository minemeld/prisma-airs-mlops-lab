#!/usr/bin/env python3
"""
Compare two AIRS scan results side-by-side.

Fetches scan results by UUID and displays differences.
Useful for comparing BLOCKED vs ALLOWED scans, or scans with different
security groups.

Usage:
    python scripts/compare_scan_results.py <scan_uuid_1> <scan_uuid_2>
    python scripts/compare_scan_results.py <uuid_1> <uuid_2> --output-json comparison.json

Requires:
    - AIRS SDK credentials in .env.superuser or environment variables
    - model-security-client package installed
"""

import os
import sys
import json
import argparse
from pathlib import Path
from uuid import UUID

from dotenv import load_dotenv

# Load credentials
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env.superuser")
load_dotenv(PROJECT_ROOT / ".env")

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

try:
    from model_security_client.api import ModelSecurityAPIClient
    AIRS_AVAILABLE = True
except ImportError:
    AIRS_AVAILABLE = False

console = Console() if HAS_RICH else None


def _print(msg: str):
    """Print helper that works with or without rich."""
    if console:
        console.print(msg)
    else:
        import re
        print(re.sub(r"\[/?[^\]]+\]", "", msg))


def fetch_scan(client, scan_uuid: str) -> dict:
    """Fetch a scan result by UUID, return as dict."""
    try:
        uuid_obj = UUID(scan_uuid)
    except ValueError:
        _print(f"[bold red]Invalid UUID:[/bold red] {scan_uuid}")
        sys.exit(1)

    try:
        response = client.get_scan(uuid_obj)
        if hasattr(response, "model_dump"):
            return response.model_dump()
        return dict(response) if response else {}
    except Exception as e:
        _print(f"[bold red]Failed to fetch scan {scan_uuid}:[/bold red] {e}")
        return {}


def extract_fields(scan: dict) -> dict:
    """Extract key comparison fields from a scan result."""
    # Parse verdict
    raw_verdict = scan.get("eval_outcome", "UNKNOWN")
    verdict = str(raw_verdict).split(".")[-1].upper()

    # Parse eval summary
    summary = scan.get("eval_summary", {}) or {}
    total_rules = summary.get("total_rules", 0)
    rules_passed = summary.get("rules_passed", 0)
    rules_failed = summary.get("rules_failed", 0)

    # Parse scan metadata
    scan_uuid = scan.get("uuid", scan.get("scan_id", "N/A"))
    model_path = scan.get("model_path", scan.get("model_uri", "N/A"))
    source_type = scan.get("source_type", "N/A")
    security_group = scan.get("security_group_uuid", "N/A")
    created_at = scan.get("created_at", scan.get("timestamp", "N/A"))
    status = scan.get("status", "N/A")

    return {
        "uuid": str(scan_uuid),
        "verdict": verdict,
        "total_rules": total_rules,
        "rules_passed": rules_passed,
        "rules_failed": rules_failed,
        "model_path": str(model_path),
        "source_type": str(source_type),
        "security_group": str(security_group),
        "created_at": str(created_at),
        "status": str(status),
    }


def verdict_color(verdict: str) -> str:
    """Return rich color tag for verdict."""
    colors = {
        "ALLOWED": "green",
        "BLOCKED": "red",
        "PENDING": "yellow",
        "ERROR": "red",
    }
    return colors.get(verdict, "white")


def display_comparison(fields_a: dict, fields_b: dict):
    """Display side-by-side comparison of two scan results."""
    if not HAS_RICH:
        # Fallback: plain text
        print("\n" + "=" * 70)
        print("  AIRS Scan Comparison")
        print("=" * 70)
        for key in fields_a:
            val_a = fields_a[key]
            val_b = fields_b[key]
            marker = " <-- DIFFERENT" if val_a != val_b else ""
            print(f"  {key:20s} | {str(val_a):25s} | {str(val_b):25s}{marker}")
        return

    # Rich table comparison
    table = Table(
        title="AIRS Scan Comparison",
        box=box.DOUBLE_EDGE,
        show_lines=True,
    )
    table.add_column("Field", style="bold", min_width=18)
    table.add_column(f"Scan A", min_width=30)
    table.add_column(f"Scan B", min_width=30)
    table.add_column("Match?", justify="center", min_width=8)

    display_order = [
        ("uuid", "Scan UUID"),
        ("verdict", "Verdict"),
        ("total_rules", "Total Rules"),
        ("rules_passed", "Rules Passed"),
        ("rules_failed", "Rules Failed"),
        ("model_path", "Model Path"),
        ("source_type", "Source Type"),
        ("security_group", "Security Group"),
        ("created_at", "Created At"),
        ("status", "Status"),
    ]

    for key, label in display_order:
        val_a = str(fields_a.get(key, "N/A"))
        val_b = str(fields_b.get(key, "N/A"))
        match = val_a == val_b

        # Apply verdict coloring
        if key == "verdict":
            color_a = verdict_color(val_a)
            color_b = verdict_color(val_b)
            val_a_display = f"[bold {color_a}]{val_a}[/bold {color_a}]"
            val_b_display = f"[bold {color_b}]{val_b}[/bold {color_b}]"
        elif key == "rules_failed":
            val_a_display = f"[red]{val_a}[/red]" if int(fields_a.get(key, 0)) > 0 else f"[green]{val_a}[/green]"
            val_b_display = f"[red]{val_b}[/red]" if int(fields_b.get(key, 0)) > 0 else f"[green]{val_b}[/green]"
        elif key == "rules_passed":
            val_a_display = f"[green]{val_a}[/green]"
            val_b_display = f"[green]{val_b}[/green]"
        else:
            val_a_display = val_a
            val_b_display = val_b

        match_display = "[green]YES[/green]" if match else "[red]NO[/red]"

        table.add_row(label, val_a_display, val_b_display, match_display)

    console.print()
    console.print(table)

    # Summary panel
    verdict_a = fields_a.get("verdict", "UNKNOWN")
    verdict_b = fields_b.get("verdict", "UNKNOWN")

    if verdict_a == verdict_b:
        summary_text = f"Both scans returned [bold]{verdict_a}[/bold] -- same verdict."
    else:
        summary_text = (
            f"Scan A: [bold {verdict_color(verdict_a)}]{verdict_a}[/bold {verdict_color(verdict_a)}]  |  "
            f"Scan B: [bold {verdict_color(verdict_b)}]{verdict_b}[/bold {verdict_color(verdict_b)}]\n\n"
            "Different verdicts. This could indicate:\n"
            "  - Different security group configurations (warn vs block)\n"
            "  - Different models scanned (clean vs malicious)\n"
            "  - Policy changes between scans"
        )

    console.print()
    console.print(Panel(summary_text, title="Summary", border_style="cyan"))


def main():
    parser = argparse.ArgumentParser(
        description="Compare two AIRS scan results side-by-side",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/compare_scan_results.py abc123-... def456-...
  python scripts/compare_scan_results.py abc123 def456 --output-json comparison.json

The script fetches both scans from the AIRS API and displays a formatted
comparison table highlighting differences in verdicts, rule counts, and
security group configurations.
        """,
    )

    parser.add_argument("scan_uuid_1", help="UUID of the first scan")
    parser.add_argument("scan_uuid_2", help="UUID of the second scan")
    parser.add_argument("--output-json", type=Path, help="Save comparison as JSON")

    args = parser.parse_args()

    # Verify AIRS SDK
    if not AIRS_AVAILABLE:
        _print("[bold red]model-security-client package not installed![/bold red]")
        _print("  Install with: pip install model-security-client")
        sys.exit(1)

    # Verify credentials
    if not os.getenv("MODEL_SECURITY_CLIENT_ID") or not os.getenv("MODEL_SECURITY_CLIENT_SECRET"):
        _print("[bold red]Missing AIRS credentials.[/bold red]")
        _print("  Set MODEL_SECURITY_CLIENT_ID and MODEL_SECURITY_CLIENT_SECRET")
        _print("  Or create .env.superuser in project root")
        sys.exit(1)

    # Initialize client
    api_url = os.environ.get(
        "MODEL_SECURITY_API_ENDPOINT",
        "https://api.sase.paloaltonetworks.com/aims",
    )
    client = ModelSecurityAPIClient(base_url=api_url, timeout=30.0)

    _print(f"\n[bold]Fetching scan results...[/bold]")
    _print(f"  Scan A: {args.scan_uuid_1}")
    _print(f"  Scan B: {args.scan_uuid_2}")

    # Fetch both scans
    scan_a = fetch_scan(client, args.scan_uuid_1)
    scan_b = fetch_scan(client, args.scan_uuid_2)

    client.close()

    if not scan_a:
        _print(f"[bold red]Scan A not found:[/bold red] {args.scan_uuid_1}")
        sys.exit(1)
    if not scan_b:
        _print(f"[bold red]Scan B not found:[/bold red] {args.scan_uuid_2}")
        sys.exit(1)

    # Extract and compare
    fields_a = extract_fields(scan_a)
    fields_b = extract_fields(scan_b)

    display_comparison(fields_a, fields_b)

    # Save JSON if requested
    if args.output_json:
        comparison = {
            "scan_a": {"uuid": args.scan_uuid_1, "fields": fields_a, "raw": scan_a},
            "scan_b": {"uuid": args.scan_uuid_2, "fields": fields_b, "raw": scan_b},
            "differences": {
                k: {"a": fields_a[k], "b": fields_b[k]}
                for k in fields_a
                if fields_a[k] != fields_b[k]
            },
        }
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_json, "w") as f:
            json.dump(comparison, f, indent=2, default=str)
        _print(f"\n[dim]Comparison saved to: {args.output_json}[/dim]")


if __name__ == "__main__":
    main()
