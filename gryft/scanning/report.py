# Standard lib
from typing import Dict, List
import json
from dataclasses import dataclass
from datetime import datetime, timezone

# 3rd party
import sh   # Depends on grpye and syft
from sh import ErrorReturnCode_1

# Local
from gryft.scanning.image import Image
from gryft.scanning.types import CVE, Component
from gryft.scanning.snapshot import ImageSnapshot


@dataclass
class GrypeReport:
    cves: Dict[str, List[CVE]]

    @classmethod
    def from_json(cls, data: Dict):
        try:
            matches = data["matches"]
            cves = [CVE.from_match(m) for m in matches]
            return cls(cves=cves)

        except KeyError as e:
            raise RuntimeError(f"Missing fields in grype report: {str(e)}")
        except ValueError as e:
            raise RuntimeError(str(e))


@dataclass
class SyftReport:
    components: List[Component]
    image_sz: int

    @classmethod
    def from_json(cls, data: Dict):
        if "artifacts" not in data.keys():
            raise RuntimeError("Syft report is missing the `artifacts` field")
        artifacts = data["artifacts"]
        components = [Component.from_artifact(a) for a in artifacts]
        
        try:
            image_sz = data["source"]["metadata"]["imageSize"]
        except KeyError as e:
            raise Exception(f"Syft report is missing field: {str(e)}")
        
        return cls(components=components,
                    image_sz=image_sz)
