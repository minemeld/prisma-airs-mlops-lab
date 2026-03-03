#!/usr/bin/env python3
"""
AIRS Model Scanner CLI

Wraps the Prisma AIRS SDK to scan local or remote models.
Designed for use in CI/CD pipelines to block deployment of unsafe models.

Security groups are auto-detected from model path source type (LOCAL/GCS/HF),
or can be overridden with --security-group (UUID or shorthand key).
"""

import os
import sys
import json
import argparse
from pathlib import Path
from uuid import UUID
from dotenv import load_dotenv
from rich.console import Console

# Try importing AIRS SDK
try:
    from model_security_client.api import ModelSecurityAPIClient
    AIRS_AVAILABLE = True
except ImportError:
    AIRS_AVAILABLE = False

console = Console()

# Security groups from your SCM tenant.
# Replace these with YOUR tenant's UUIDs from SCM → AI Model Security → Security Groups.
# Or pass UUIDs directly via --security-group flag (no code changes needed).
# See Module 4.2 for how to find your UUIDs.
SECURITY_GROUPS = {
    "local":       (UUID("a7ae2286-5a2d-4dc6-9e98-7055916725cc"), "LOCAL"),
    "gcs-default": (UUID("c472b2b9-5823-47cd-bda1-8a83f3b536b6"), "GCS"),
    "hf":          (UUID("0ef6dadc-70ff-4fab-b4e5-854046bb7a56"), "HUGGING_FACE"),
    "warn":        (UUID("c472b2b9-5823-47cd-bda1-8a83f3b536b6"), "GCS"),
    "block":       (UUID("c472b2b9-5823-47cd-bda1-8a83f3b536b6"), "GCS"),
}

# Default group per source type (used when --security-group is not specified)
DEFAULT_GROUPS = {
    "LOCAL":        SECURITY_GROUPS["local"][0],
    "GCS":          SECURITY_GROUPS["gcs-default"][0],
    "HUGGING_FACE": SECURITY_GROUPS["hf"][0],
}


def parse_args():
    parser = argparse.ArgumentParser(description="Scan AI models with Prisma AIRS")
    parser.add_argument("--model-path", required=True, help="Path to model (local dir, gs:// URI, or HuggingFace URL)")
    parser.add_argument(
        "--security-group",
        default=None,
        help="Security group UUID or shorthand key (local, gcs-default, hf, warn, block). "
             "Auto-detected from model path if not specified.",
    )
    parser.add_argument("--warn-only", action="store_true", help="Treat BLOCKED verdict as warning (exit 0)")
    parser.add_argument("--output-json", help="Path to save JSON report")
    return parser.parse_args()


def check_airs_credentials():
    """Verify AIRS Model Security credentials are set."""
    has_sa = os.getenv("MODEL_SECURITY_CLIENT_ID") and os.getenv("MODEL_SECURITY_CLIENT_SECRET")
    has_tsg = os.getenv("TSG_ID")

    if not has_sa:
        console.print("[bold red]Missing Credentials:[/bold red] Set MODEL_SECURITY_CLIENT_ID and MODEL_SECURITY_CLIENT_SECRET.")
        return False

    if not has_tsg:
        console.print("[bold yellow]TSG_ID not set. May be required for authentication.[/bold yellow]")

    return True


def detect_source_type(model_path):
    """Detect source type from model path string."""
    if model_path.startswith("gs://"):
        return "GCS"
    elif model_path.startswith("s3://"):
        return "S3"
    elif model_path.startswith("https://huggingface.co"):
        return "HUGGING_FACE"
    else:
        return "LOCAL"


def resolve_security_group(group_arg, source_type):
    """Resolve security group from CLI arg or auto-detect from source type.

    Returns (UUID, source_type_of_group).
    """
    if group_arg is None:
        # Auto-detect: use default group for this source type
        group_uuid = DEFAULT_GROUPS.get(source_type)
        if group_uuid is None:
            console.print(f"[bold red]No default security group for source type: {source_type}[/bold red]")
            sys.exit(1)
        # Catch placeholder UUIDs — students need to configure their own
        if str(group_uuid).startswith("00000000"):
            console.print(f"[bold yellow]⚠ Security group UUID is a placeholder![/bold yellow]")
            console.print(f"  The SECURITY_GROUPS dict in scan_model.py has not been configured.")
            console.print(f"  Two options:")
            console.print(f"    1. Pass your UUID directly:  --security-group <your-uuid>")
            console.print(f"    2. Edit SECURITY_GROUPS in airs/scan_model.py with your tenant's UUIDs")
            console.print(f"  Find your UUIDs in SCM → AI Model Security → Security Groups (Module 4.2)")
            sys.exit(1)
        console.print(f"  Security Group: [cyan]Default {source_type}[/cyan] (auto-detected)")
        return group_uuid

    # Try as shorthand key first
    if group_arg in SECURITY_GROUPS:
        group_uuid, group_source = SECURITY_GROUPS[group_arg]
        if str(group_uuid).startswith("00000000"):
            console.print(f"[bold yellow]⚠ '{group_arg}' maps to a placeholder UUID![/bold yellow]")
            console.print(f"  Pass your real UUID directly:  --security-group <your-uuid>")
            console.print(f"  Or edit SECURITY_GROUPS in airs/scan_model.py with your tenant's UUIDs")
            sys.exit(1)
        console.print(f"  Security Group: [cyan]{group_arg}[/cyan] ({group_uuid})")
        if group_source != source_type:
            console.print(
                f"[bold yellow]Warning: Group source type ({group_source}) does not match "
                f"model source type ({source_type}). This may cause a ValidationError.[/bold yellow]"
            )
        return group_uuid

    # Try as raw UUID
    try:
        group_uuid = UUID(group_arg)
        console.print(f"  Security Group: [cyan]{group_uuid}[/cyan] (custom UUID)")
        return group_uuid
    except ValueError:
        console.print(f"[bold red]Invalid security group: '{group_arg}'[/bold red]")
        console.print(f"  Use a UUID or shorthand key: {', '.join(SECURITY_GROUPS.keys())}")
        sys.exit(1)


def scan_model(model_path, security_group_uuid):
    """Execute the scan using AIRS SDK."""
    if not AIRS_AVAILABLE:
        console.print("[bold red]model-security-client package not installed![/bold red]")
        sys.exit(1)

    source_type = detect_source_type(model_path)

    console.print(f"\n[bold blue]Starting AIRS Scan[/bold blue]")
    console.print(f"  Model: [cyan]{model_path}[/cyan]")
    console.print(f"  Source Type: [cyan]{source_type}[/cyan]")

    try:
        # Determine local_path vs model_uri based on source type
        if source_type == "LOCAL":
            abs_path = Path(model_path).resolve()
            if not abs_path.exists():
                console.print(f"[bold red]Model path not found:[/bold red] {abs_path}")
                sys.exit(1)
            local_path = str(abs_path)
            model_uri = None
        else:
            local_path = None
            model_uri = model_path

        # Initialize client
        base_url = os.environ.get(
            "MODEL_SECURITY_API_ENDPOINT",
            "https://api.sase.paloaltonetworks.com/aims"
        )
        client = ModelSecurityAPIClient(base_url=base_url, timeout=60.0)

        # Trigger Scan
        with console.status("[bold green]Scanning model artifacts...[/bold green]"):
            response = client.scan(
                security_group_uuid=security_group_uuid,
                model_path=local_path,
                model_uri=model_uri,
                poll_timeout_secs=600,
            )

        client.close()

        # Convert response to dict
        if hasattr(response, "model_dump"):
            return response.model_dump()
        return dict(response) if response else {}

    except Exception as e:
        console.print(f"[bold red]Scan Failed:[/bold red] {str(e)}")
        sys.exit(1)


def main():
    load_dotenv()
    args = parse_args()

    if not check_airs_credentials():
        sys.exit(1)

    # Detect source type and resolve security group
    source_type = detect_source_type(args.model_path)
    security_group_uuid = resolve_security_group(args.security_group, source_type)

    # Run scan
    results = scan_model(args.model_path, security_group_uuid)

    # Save Report
    if args.output_json:
        with open(args.output_json, "w") as f:
            json.dump(results, f, indent=2, default=str)
        console.print(f"\n[dim]Report saved to: {args.output_json}[/dim]")

    # Parse verdict — SDK returns enum objects (e.g., EvalOutcome.BLOCKED)
    raw_verdict = results.get("eval_outcome", "UNKNOWN")
    verdict = str(raw_verdict).split(".")[-1].upper()

    scan_uuid = results.get("uuid", "N/A")
    console.print(f"\n[bold]Scan UUID: {scan_uuid}[/bold]")
    console.print(f"[bold]Scan Verdict: {verdict}[/bold]")

    # Display aggregate rule summary
    eval_summary = results.get("eval_summary")
    if eval_summary and isinstance(eval_summary, dict):
        total = eval_summary.get("total_rules", 0)
        passed = eval_summary.get("rules_passed", 0)
        failed = eval_summary.get("rules_failed", 0)
        if total > 0:
            console.print(f"[bold]Rule Summary:[/bold] {passed}/{total} passed, {failed}/{total} failed")

    # Verdict handling — only ALLOWED, BLOCKED, ERROR, PENDING exist in the SDK
    if verdict == "ERROR":
        console.print("\n[bold red]Pipeline Blocked: Scan error[/bold red]")
        sys.exit(1)
    elif verdict == "BLOCKED":
        if args.warn_only:
            console.print(f"\n[bold yellow]Model BLOCKED by policy rules (--warn-only: treating as warning)[/bold yellow]")
            console.print(f"  Review security group configuration if unexpected.")
            console.print("\n[bold green]Scan Complete (warn-only mode)[/bold green]")
            sys.exit(0)
        else:
            console.print(f"\n[bold red]Pipeline Blocked: Model BLOCKED by policy rules[/bold red]")
            console.print(f"  A blocking rule triggered. Use --warn-only to override.")
            sys.exit(1)
    elif verdict == "ALLOWED":
        console.print("\n[bold green]Scan Complete[/bold green]")
        sys.exit(0)
    else:
        # PENDING or unexpected value — treat as error
        console.print(f"\n[bold red]Unexpected verdict: {verdict}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
