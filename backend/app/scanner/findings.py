from dataclasses import dataclass

from app.models.vulnerability import Severity, VulnerabilitySource


@dataclass
class Finding:
    source: VulnerabilitySource
    severity: Severity
    title: str
    description: str | None = None
    cve_id: str | None = None
    package_name: str | None = None
    file_path: str | None = None
