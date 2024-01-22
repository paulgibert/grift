# Standard lib
from typing import Dict, List
import json
from dataclasses import dataclass
from datetime import datetime, timezone

# 3rd party
import sh   # Depends on grpye and syft
from sh import ErrorReturnCode_1

# Local
from gryft.image import Image
from gryft.types import CVE, Component
from gryft.snapshot import ImageSnapshot


@dataclass
class GrypeReport:
    cves: Dict[str, List[CVE]]

    @classmethod
    def from_json(cls, data: Dict):
        try:
            counts = {k: [] for k in ["critical", "high", "medium",
                                      "low", "negligible", "unknown"]}
            matches = data["matches"]

            cve_list = [CVE.from_match(m) for m in matches]
            for c in cve_list:
                if c.severity not in counts.keys():
                    raise RuntimeError(f"Grype reported an unrecognized vulnerability severity {c.severity}")
                counts[c.severity].append(c)
            
            return cls(cves=counts)
        
        except KeyError as e:
            raise RuntimeError(f"Missing fields in grype report: {str(e)}")
        except ValueError as e:
            raise RuntimeError(str(e))


def _scan_grype(image: Image) -> Dict:
    """
    Scans an image with grype.
    """
    try:
        json_str = sh.grype(image.scan_str(), output="json")
        return json.loads(json_str)
    except ErrorReturnCode_1 as e:
        raise ValueError(f"Image not found ({e.full_cmd} FAILED): " + e.stderr.decode("utf-8"))
    except json.decoder.JSONDecodeError:
        raise RuntimeError(f"Failed to parse JSON from grype scan of {image}:\n{json_str}")


def scan_grype(image: Image) -> GrypeReport:
    data = _scan_grype(image)
    return GrypeReport.from_json(data)


@dataclass
class SyftReport:
    components: List[Component]
    image_sz: int

    @classmethod
    def from_json(cls, data: Dict):
        try:
            artifacts = data["artifacts"]
            components = [Component.from_artifact(a) for a in artifacts]
            image_sz = data["source"]["target"]["imageSize"]
            return cls(components=components,
                       image_sz=image_sz)

        except KeyError as e:
            raise RuntimeError(f"Missing fields in syft report: {str(e)}")
        except ValueError as e:
            raise RuntimeError(str(e))


def _scan_syft(image: Image) -> Dict:
    """
    Scans an image with syft.
    """
    try:
        json_str = sh.syft(image.scan_str(), output="syft-json")
        return json.loads(json_str)
    except ErrorReturnCode_1 as e:
        raise ValueError(f"Image not found ({e.full_cmd} FAILED): " + e.stderr.decode("utf-8"))
    except json.decoder.JSONDecodeError:
        raise RuntimeError(f"Failed to parse JSON from syft scan of {image.scan_str()}")


def scan_syft(image: Image) -> SyftReport:
    data = _scan_syft(image)
    return SyftReport.from_json(data)


class ImageScanner:
    def scan(self, image: Image) -> ImageSnapshot:
        scanned_at = datetime.now(timezone.utc)
        grype_report = scan_grype(image)
        syft_report = scan_syft(image)
        return ImageSnapshot(
            image=image,
            scanned_at=scanned_at,
            cves=grype_report.cves,
            components=syft_report.components,
            image_sz=syft_report.image_sz
        )
