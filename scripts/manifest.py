#!/usr/bin/env python3
"""Model manifest helper for pipeline provenance tracking.

Creates and updates manifest.json files that travel with model artifacts
through the three-gate pipeline, accumulating provenance data.

Usage:
    # Create initial manifest (Gate 1)
    python scripts/manifest.py create \
        --model-name cloud-security-advisor \
        --base-model Qwen/Qwen2.5-3B-Instruct \
        --base-model-source huggingface_public \
        --dataset ethanolivertroy/nist-cybersecurity-training \
        --run-id 20260205-143022 \
        --output manifest.json

    # Add a scan result
    python scripts/manifest.py add-scan \
        --manifest manifest.json \
        --gate gate1 \
        --scan-uuid abc-123 \
        --verdict ALLOWED \
        --security-group "00000000-0000-0000-0000-000000000001" \
        --target "Qwen/Qwen2.5-3B-Instruct"

    # Add training info
    python scripts/manifest.py add-training \
        --manifest manifest.json \
        --vertex-job-id 1234567890 \
        --machine-type a2-highgpu-1g \
        --max-steps 5000 \
        --adapter-path gs://jlimon-airs-lab/raw-models/cloud-security-advisor/20260205

    # Add deployment record
    python scripts/manifest.py add-deployment \
        --manifest manifest.json \
        --vertex-endpoint-id your-endpoint-id \
        --cloud-run-revision cloud-security-advisor-00042 \
        --strategy full

    # Verify manifest has required scans
    python scripts/manifest.py verify \
        --manifest manifest.json \
        --require-scan gate2 \
        --require-verdict ALLOWED,BLOCKED
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


SCHEMA_VERSION = "1.0"


def cmd_create(args):
    """Create a new manifest."""
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "model_name": args.model_name,
        "model_version": args.model_version or "",
        "lineage": {
            "base_model": args.base_model,
            "base_model_source": args.base_model_source or "",
            "dataset": args.dataset or "",
            "training_run_id": args.run_id or "",
            "adapter_path": "",
            "merged_model_path": "",
        },
        "training": {},
        "scans": {},
        "deployments": [],
        "metadata": {
            "created_by": os.getenv("GITHUB_WORKFLOW", "manual"),
            "created_at": now_iso(),
            "last_updated_by": os.getenv("GITHUB_WORKFLOW", "manual"),
            "last_updated_at": now_iso(),
            "github_repository": os.getenv("GITHUB_REPOSITORY", ""),
        },
    }
    output = args.output or "manifest.json"
    write_manifest(manifest, output)
    print(f"Created manifest: {output}")


def cmd_add_scan(args):
    """Add a scan result to the manifest."""
    manifest = read_manifest(args.manifest)
    manifest["scans"][args.gate] = {
        "scan_uuid": args.scan_uuid,
        "verdict": args.verdict,
        "security_group": args.security_group or "",
        "target": args.target or "",
        "target_type": args.target_type or "",
        "timestamp": now_iso(),
        "workflow_run_id": os.getenv("GITHUB_RUN_ID", ""),
        "commit_sha": os.getenv("GITHUB_SHA", ""),
    }
    if args.warn_only:
        manifest["scans"][args.gate]["verdict_action"] = "warn"
    touch_metadata(manifest)
    write_manifest(manifest, args.manifest)
    print(f"Added {args.gate} scan: {args.verdict} (uuid={args.scan_uuid})")


def cmd_add_training(args):
    """Add or update training info in the manifest."""
    manifest = read_manifest(args.manifest)
    training = manifest.get("training", {})
    if args.vertex_job_id:
        training["vertex_job_id"] = args.vertex_job_id
    if args.machine_type:
        training["machine_type"] = args.machine_type
    if args.max_steps:
        training["max_steps"] = int(args.max_steps)
    if args.adapter_path:
        training["adapter_path"] = args.adapter_path
        manifest["lineage"]["adapter_path"] = args.adapter_path
    manifest["training"] = training
    touch_metadata(manifest)
    write_manifest(manifest, args.manifest)
    print(f"Updated training info")


def cmd_add_deployment(args):
    """Add a deployment record to the manifest."""
    manifest = read_manifest(args.manifest)
    deployment = {
        "vertex_endpoint_id": args.vertex_endpoint_id or "",
        "cloud_run_revision": args.cloud_run_revision or "",
        "strategy": args.strategy or "full",
        "timestamp": now_iso(),
        "workflow_run_id": os.getenv("GITHUB_RUN_ID", ""),
        "commit_sha": os.getenv("GITHUB_SHA", ""),
    }
    manifest.setdefault("deployments", []).append(deployment)
    touch_metadata(manifest)
    write_manifest(manifest, args.manifest)
    print(f"Added deployment record")


def cmd_set_version(args):
    """Set the model version in the manifest."""
    manifest = read_manifest(args.manifest)
    manifest["model_version"] = args.version
    if args.merged_model_path:
        manifest["lineage"]["merged_model_path"] = args.merged_model_path
    touch_metadata(manifest)
    write_manifest(manifest, args.manifest)
    print(f"Set version: {args.version}")


def cmd_verify(args):
    """Verify manifest has required scans and fields."""
    manifest = read_manifest(args.manifest)
    errors = []

    # Check required scans
    if args.require_scan:
        for gate in args.require_scan:
            if gate not in manifest.get("scans", {}):
                errors.append(f"Missing required scan: {gate}")
            elif args.require_verdict:
                actual = manifest["scans"][gate].get("verdict", "")
                allowed = [v.strip().upper() for v in args.require_verdict]
                if actual.upper() not in allowed:
                    errors.append(
                        f"Scan {gate} verdict '{actual}' not in allowed: {allowed}"
                    )

    # Check required fields
    if args.require_field:
        for field_path in args.require_field:
            value = get_nested(manifest, field_path)
            if not value:
                errors.append(f"Missing required field: {field_path}")

    if errors:
        print("Manifest verification FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("Manifest verification PASSED")
        # Print summary
        scans = manifest.get("scans", {})
        for gate, scan in scans.items():
            verdict = scan.get("verdict", "?")
            scan_uuid = scan.get("scan_uuid", scan.get("scan_id", "?"))
            print(f"  {gate}: {verdict} (uuid={scan_uuid})")


def cmd_show(args):
    """Display manifest contents."""
    manifest = read_manifest(args.manifest)
    print(json.dumps(manifest, indent=2))


# --- Helpers ---


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def touch_metadata(manifest):
    meta = manifest.setdefault("metadata", {})
    meta["last_updated_by"] = os.getenv("GITHUB_WORKFLOW", "manual")
    meta["last_updated_at"] = now_iso()


def read_manifest(path):
    with open(path) as f:
        return json.load(f)


def write_manifest(manifest, path):
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def get_nested(d, path):
    """Get a value from a nested dict using dot-separated path."""
    keys = path.split(".")
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k)
        else:
            return None
    return d


# --- CLI ---


def main():
    parser = argparse.ArgumentParser(
        description="Model manifest helper for pipeline provenance tracking"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # create
    p = sub.add_parser("create", help="Create a new manifest")
    p.add_argument("--model-name", required=True)
    p.add_argument("--base-model", required=True)
    p.add_argument("--base-model-source", default="")
    p.add_argument("--dataset", default="")
    p.add_argument("--run-id", default="")
    p.add_argument("--model-version", default="")
    p.add_argument("--output", default="manifest.json")

    # add-scan
    p = sub.add_parser("add-scan", help="Add a scan result")
    p.add_argument("--manifest", required=True)
    p.add_argument("--gate", required=True, choices=["gate1", "gate2", "gate3"])
    p.add_argument("--scan-uuid", required=True)
    p.add_argument("--verdict", required=True)
    p.add_argument("--security-group", default="")
    p.add_argument("--target", default="")
    p.add_argument("--target-type", default="")
    p.add_argument("--warn-only", action="store_true")

    # add-training
    p = sub.add_parser("add-training", help="Add training info")
    p.add_argument("--manifest", required=True)
    p.add_argument("--vertex-job-id", default="")
    p.add_argument("--machine-type", default="")
    p.add_argument("--max-steps", default="")
    p.add_argument("--adapter-path", default="")

    # add-deployment
    p = sub.add_parser("add-deployment", help="Add deployment record")
    p.add_argument("--manifest", required=True)
    p.add_argument("--vertex-endpoint-id", default="")
    p.add_argument("--cloud-run-revision", default="")
    p.add_argument("--strategy", default="full")

    # set-version
    p = sub.add_parser("set-version", help="Set model version")
    p.add_argument("--manifest", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--merged-model-path", default="")

    # verify
    p = sub.add_parser("verify", help="Verify manifest")
    p.add_argument("--manifest", required=True)
    p.add_argument("--require-scan", nargs="+", help="Required scan gates")
    p.add_argument(
        "--require-verdict",
        nargs="+",
        help="Acceptable verdicts (e.g., ALLOWED BLOCKED)",
    )
    p.add_argument("--require-field", nargs="+", help="Required dot-path fields")

    # show
    p = sub.add_parser("show", help="Display manifest")
    p.add_argument("--manifest", required=True)

    args = parser.parse_args()

    commands = {
        "create": cmd_create,
        "add-scan": cmd_add_scan,
        "add-training": cmd_add_training,
        "add-deployment": cmd_add_deployment,
        "set-version": cmd_set_version,
        "verify": cmd_verify,
        "show": cmd_show,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
