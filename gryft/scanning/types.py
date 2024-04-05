# Standard lib
from typing import Dict
from dataclasses import dataclass


@dataclass(frozen=True)
class CVE:
    """
    A `dataclass` representing a CVE.

    id (str): The CVE id (CVE-2024-1234).
    severity (str): The severity of the CVE (critical, high, medium, low, negligible, or unknown)
    fix_state (str): The state of the CVE's fix.
    """
    id: str
    severity: str
    fix_state: str
    
    @classmethod
    def from_match(cls, match: Dict):
        """
        Creates an instance of `CVE` from a grype match. The published date
        is fetched from the NVD.

        Args:
            match (Dict): The grype match.
        """
        try:
            id = match["vulnerability"]["id"]
            severity = match["vulnerability"]["severity"].lower()
            fix_state = match["vulnerability"]["fix"]["state"].lower()
            return cls(id=id, severity=severity, fix_state=fix_state)
        except KeyError as e:
            raise ValueError(f"Missing field in grype match: {str(e)}")


@dataclass(frozen=True)
class Component:
    """
    A class representing an image component.

    name (str): The component name.
    type_ (str): The component type reported by syft.
    """
    name: str
    type_: str

    @classmethod
    def from_artifact(cls, artifact: Dict):
        """
        Creates an instance of `Component` from a syft artifact.

        Args:
            artifact (Dict): The syft artifact.
        """
        try:
            name = artifact["name"]
            type_ = artifact["type"].lower()
            return cls(name=name, type_=type_)
        except KeyError as e:
            raise ValueError(f"Missing field in syft artifact: {str(e)}")