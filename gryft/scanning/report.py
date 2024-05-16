# Standard lib
from typing import Dict, List
from dataclasses import dataclass

# 3rd party
import sh   # Depends on grpye and syft
from sh import ErrorReturnCode_1

# Local
from gryft.scanning.types import CVE, Component


@dataclass
class GrypeReport:
    cves: List[CVE]

    @classmethod
    def from_json(cls, data: Dict):
        matches = data.get("matches", None)
        cves = []
        if matches is not None:
            try:
                cves = [CVE.from_match(m) for m in matches]
            except KeyError as e:
                raise RuntimeError(f"Missing fields in grype report: {str(e)}")
            except ValueError as e:
                raise RuntimeError(str(e))
        return cls(cves=cves)


@dataclass
class SyftReport:
    components: List[Component]
    distro: str
    image_sz: int

    @classmethod
    def from_json(cls, data: Dict):
        if "artifacts" not in data.keys():
            raise RuntimeError("Syft report is missing the `artifacts` field")
        artifacts = data["artifacts"]
        components = [Component.from_artifact(a) for a in artifacts]
        
        try:
            distro = data["distro"]["id"]
        except KeyError:
            distro = "unknown"

        try:
            image_sz = data["source"]["metadata"]["imageSize"]
        except KeyError as e:
            raise Exception(f"Syft report is missing field: {str(e)}")
        
        return cls(components=components,
                   distro=distro,
                   image_sz=image_sz)
