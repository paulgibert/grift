# Standard lib
from dataclasses import dataclass


@dataclass
class Image:
    """
    A `dataclass` representing an image.

    registry (str): The image registry (cgr.dev, docker.io).
    repository (str): The image repository (chainguard/nginx, ubi7/ubi-minimal).
    tag (str, Optional): The image tag.
    digest (str, Optional): The image digest
    """
    registry: str
    repository: str
    tag: str="latest"
    digest: str=None

    def __init__(self, registry: str, repository: str,
                 tag: str, digest: str=None, **kwargs):
        self.registry = registry
        self.repository = repository
        self.tag = tag
        self.digest = digest

        for k, v in kwargs.items():
            setattr(self, k, v)

    def identifier(self) -> str:
        """
        Returns the identifier of the image.
        Takes the form <registry><repository/path>[:tag][@<sha_digest>].

        Examples:
            docker.io/alpine:latest
            cgr.dev/chainguard/wolfi-base:latest@sha256:9a5330218c81bdeb5d63702...

        Returns:
            String representation of the image.
        """
        output = f"{self.registry}/{self.repository}:{self.tag}"
        if self.digest:
            output += f"@{self.digest}"
        return output
    
    def __repr__(self) -> str:
        return self.identifier()