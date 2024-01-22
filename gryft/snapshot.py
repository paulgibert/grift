# Standard lib
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

# Local
from gryft.types import CVE, Component
from gryft.image import Image


def _validate_severity(severity: str):
    if severity not in CVE.severities:
        raise TypeError(f"Unrecognized value for `severity`. Must be one of {CVE.severities}")

@dataclass
class ImageSnapshot:
    image: Image
    scanned_on: datetime
    cves: Dict[str, List[CVE]]
    components: List[Component]
    image_sz: int

    def count_cves(self, severity: str | List[str], fix_state: str=None):
        if isinstance(severity, str):
            severity = [severity]
        for s in severity:
            _validate_severity(s)
        
        count = 0
        for c in self.cves:
            if c.severity in severity:
                if (fix_state is None) or (c.fix_state == fix_state):
                    count += 1
        return count
