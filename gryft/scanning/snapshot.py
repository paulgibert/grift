# Standard lib
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

# Local
from gryft.scanning.types import CVE, Component
from gryft.scanning.image import Image


SEVERITIES = ["critical", "high", "medium", "low", "negligible", "unknown"]


def _validate_severity(severity: str):
    if severity not in SEVERITIES:
        raise TypeError(f"Unrecognized value for `severity`. Must be one of {CVE.severities}")

@dataclass
class ImageSnapshot:
    image: Image
    scanned_at: datetime
    cves: Dict[str, List[CVE]]
    components: List[Component]
    image_sz: int

    def count_cves(self, severity: str | List[str]=None, fix_state: str=None):
        if severity is None:
            severity = SEVERITIES

        if isinstance(severity, str):
            severity = [severity]
        
        for s in severity:
            _validate_severity(s)
        
        count = 0
        for sev, cves in self.cves.items():
            if sev in severity:
                count += len(cves)
        return count
