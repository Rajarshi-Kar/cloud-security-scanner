import json
import os

from app.core.config import settings
from app.models.scan import Scan
from app.models.vulnerability import Vulnerability


def generate_json_report(scan: Scan, vulnerabilities: list[Vulnerability], dest_path: str) -> None:
    payload = {
        "scan_id": str(scan.id),
        "target": scan.target,
        "scan_type": scan.scan_type.value,
        "status": scan.status.value,
        "security_score": scan.security_score,
        "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
        "vulnerabilities": [
            {
                "id": str(v.id),
                "source": v.source.value,
                "severity": v.severity.value,
                "title": v.title,
                "description": v.description,
                "cve_id": v.cve_id,
                "cve_url": f"{settings.CVE_LOOKUP_URL}{v.cve_id}" if v.cve_id else None,
                "package_name": v.package_name,
                "file_path": v.file_path,
            }
            for v in vulnerabilities
        ],
    }
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
