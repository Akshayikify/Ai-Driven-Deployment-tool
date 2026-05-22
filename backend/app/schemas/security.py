from __future__ import annotations

from typing import Dict, List, Literal
from pydantic import BaseModel, Field


class SecurityFinding(BaseModel):
    """
    Represents a single secret or sensitive value detected in the repository.
    The actual secret value is NEVER stored — only a redacted snippet.
    """
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    rule_id: str = Field(..., description="Machine-readable rule identifier, e.g. 'AWS_ACCESS_KEY_ID'")
    description: str = Field(..., description="Human-readable description of what was found")
    file_path: str = Field(..., description="Relative path to the file containing the finding")
    line_number: int = Field(..., description="1-indexed line number where the secret appears")
    redacted_snippet: str = Field(..., description="Context snippet with the secret value masked")
    recommendation: str = Field(..., description="Actionable remediation advice")


class SecurityReport(BaseModel):
    """
    Aggregated result of a full security scan on a workspace.
    This is attached to the task findings dict and returned to the frontend.
    """
    scanned_files: int = Field(0, description="Total number of source files scanned")
    scan_duration_ms: int = Field(0, description="How long the scan took in milliseconds")
    findings: List[SecurityFinding] = Field(default_factory=list)
    severity_counts: Dict[str, int] = Field(
        default_factory=lambda: {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    )
    is_clean: bool = Field(True, description="True only when zero findings exist")
    blocked: bool = Field(False, description="True when CRITICAL findings are present — deployment must be halted")
    summary: str = Field("", description="Human-readable one-liner summary for the UI")
