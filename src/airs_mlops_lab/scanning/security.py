"""AIRS Model Security scanning using Prisma AIRS SDK.

This module provides a clean Python interface for scanning ML models
using the Palo Alto Networks AI Model Security service.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID

from model_security_client.api import ModelSecurityAPIClient


class Verdict(Enum):
    """Scan verdict indicating overall security status.

    Maps directly to the AIRS SDK EvalOutcome values.
    Only ALLOWED and BLOCKED are terminal scan outcomes.
    """

    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"


class SourceType(Enum):
    """Model source types supported by AIRS."""

    HUGGING_FACE = "HUGGING_FACE"
    LOCAL = "LOCAL"
    GCS = "GCS"
    S3 = "S3"
    AZURE = "AZURE"


# Default security group UUIDs by source type.
# Replace with YOUR tenant's UUIDs from SCM → AI Model Security → Security Groups.
# See Module 4.2 for how to find your UUIDs.
DEFAULT_SECURITY_GROUPS: dict[SourceType, UUID] = {
    SourceType.HUGGING_FACE: UUID("00000000-0000-0000-0000-000000000003"),
    SourceType.LOCAL: UUID("00000000-0000-0000-0000-000000000001"),
    SourceType.GCS: UUID("00000000-0000-0000-0000-000000000002"),
    SourceType.S3: UUID("00000000-0000-0000-0000-000000000006"),
    SourceType.AZURE: UUID("00000000-0000-0000-0000-000000000007"),
}


@dataclass
class Finding:
    """A single security finding from a scan."""

    rule: str
    message: str
    severity: str
    blocking: bool = False


@dataclass
class ScanResult:
    """Result of an AIRS model security scan."""

    verdict: Verdict
    findings: list[Finding] = field(default_factory=list)
    scan_uuid: str | None = None
    model_name: str | None = None
    raw_response: dict[str, Any] | None = None

    @property
    def is_safe(self) -> bool:
        """Returns True if model passed all blocking checks."""
        return self.verdict == Verdict.ALLOWED

    @property
    def blocking_findings(self) -> list[Finding]:
        """Returns only findings that block deployment."""
        return [f for f in self.findings if f.blocking]


def init_scanner(
    base_url: str | None = None,
    timeout: float = 30.0,
) -> ModelSecurityAPIClient:
    """Initialize the AIRS Model Security client.

    Authentication is handled via environment variables:
    - MODEL_SECURITY_CLIENT_ID
    - MODEL_SECURITY_CLIENT_SECRET
    - TSG_ID

    Args:
        base_url: API endpoint. Defaults to MODEL_SECURITY_API_ENDPOINT env var
                  or https://api.sase.paloaltonetworks.com/aims
        timeout: Request timeout in seconds.

    Returns:
        Initialized ModelSecurityAPIClient instance.
    """
    if base_url is None:
        base_url = os.environ.get(
            "MODEL_SECURITY_API_ENDPOINT",
            "https://api.sase.paloaltonetworks.com/aims",
        )

    return ModelSecurityAPIClient(base_url=base_url, timeout=timeout)


def scan_model(
    model_path: str | None = None,
    model_uri: str | None = None,
    security_group: UUID | None = None,
    source_type: SourceType | None = None,
    client: ModelSecurityAPIClient | None = None,
    poll_timeout_secs: int = 600,
) -> ScanResult:
    """Scan a model for security issues using AIRS Model Security.

    Either model_path (local file) or model_uri (HF/cloud) must be provided.

    Args:
        model_path: Path to local model file or directory.
        model_uri: URI for remote model (e.g., "hf://org/model" or HF model ID).
        security_group: UUID of security group to use. If not provided,
                        uses default for the detected source type.
        source_type: Explicit source type. Auto-detected if not provided.
        client: Existing client instance. Created if not provided.
        poll_timeout_secs: Maximum time to wait for scan completion.

    Returns:
        ScanResult with verdict, findings, and raw response.

    Raises:
        ValueError: If neither model_path nor model_uri is provided.
    """
    if model_path is None and model_uri is None:
        raise ValueError("Either model_path or model_uri must be provided")

    # Auto-detect source type
    if source_type is None:
        if model_path is not None:
            source_type = SourceType.LOCAL
        elif model_uri is not None:
            if model_uri.startswith("gs://"):
                source_type = SourceType.GCS
            elif model_uri.startswith("s3://"):
                source_type = SourceType.S3
            elif model_uri.startswith("az://") or model_uri.startswith("azure://"):
                source_type = SourceType.AZURE
            else:
                # Assume HuggingFace for anything else
                source_type = SourceType.HUGGING_FACE

    # Get security group
    if security_group is None:
        security_group = DEFAULT_SECURITY_GROUPS.get(source_type)
        if security_group is None:
            raise ValueError(f"No default security group for source type: {source_type}")

    # Initialize client if needed
    close_client = False
    if client is None:
        client = init_scanner()
        close_client = True

    try:
        # Execute scan
        response = client.scan(
            security_group_uuid=security_group,
            model_path=model_path,
            model_uri=model_uri,
            poll_timeout_secs=poll_timeout_secs,
        )

        # Parse response into ScanResult
        return _parse_scan_response(response)

    finally:
        if close_client:
            client.close()


def _parse_scan_response(response: Any) -> ScanResult:
    """Parse SDK response into ScanResult."""
    if response is None:
        return ScanResult(
            verdict=Verdict.BLOCKED,
            findings=[Finding(
                rule="scan_failed",
                message="Scan returned no response",
                severity="HIGH",
                blocking=True,
            )],
        )

    # Extract data from response
    raw_dict = response.model_dump() if hasattr(response, "model_dump") else dict(response)

    # Map eval_outcome to Verdict
    # AIRS SDK returns: ALLOWED or BLOCKED for eval_outcome
    eval_outcome = raw_dict.get("eval_outcome", "")
    # Handle SDK enum objects (e.g., EvalOutcome.ALLOWED -> "ALLOWED")
    eval_outcome = str(eval_outcome).split(".")[-1].upper()
    if eval_outcome == "ALLOWED":
        verdict = Verdict.ALLOWED
    else:  # BLOCKED, ERROR, empty, or unknown
        verdict = Verdict.BLOCKED

    # Extract findings from violations or eval_summary
    findings = []
    violations = raw_dict.get("violations", [])
    for v in violations:
        findings.append(Finding(
            rule=v.get("rule_name", "unknown"),
            message=v.get("message", ""),
            severity=v.get("severity", "UNKNOWN"),
            blocking=v.get("blocking", False),
        ))

    # If no detailed violations but we have eval_summary, create summary finding
    if not findings and raw_dict.get("eval_summary"):
        summary = raw_dict["eval_summary"]
        failed_count = summary.get("rules_failed", 0)
        if failed_count > 0:
            findings.append(Finding(
                rule="eval_summary",
                message=f"{failed_count} rule(s) failed out of {summary.get('total_rules', 0)}",
                severity="HIGH" if verdict == Verdict.BLOCKED else "MEDIUM",
                blocking=(verdict == Verdict.BLOCKED),
            ))

    # Extract model info
    model_uri = raw_dict.get("model_uri", "")
    model_name = model_uri.split("/")[-1] if model_uri else None

    return ScanResult(
        verdict=verdict,
        findings=findings,
        scan_uuid=str(raw_dict.get("uuid", "")),
        model_name=model_name,
        raw_response=raw_dict,
    )
