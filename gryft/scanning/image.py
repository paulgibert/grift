class Image:
    def __init__(self, registry: str, repository: str,
                 tag: str='latest', digest: str=None, **kwargs):
        self.registry = registry
        self.repository = repository
        self.tag = tag
        self.digest = digest
        
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_identifier(cls, identifier: str):
        registry = identifier.split("/")[0]
        repository = "/".join(identifier.split("/")[1:]).split(":")[0]
        tag = identifier.split(":")[1]
        if "@" in tag:
            tag = tag.split("@")[0]
        if "@" in identifier:
            digest = identifier.split("@")[1]
        else:
            digest = None
        return cls(registry, repository, tag, digest=digest)

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
        output = self.repository + ':' + self.tag
        if self.registry is not None:
            output = self.regigistry + '/' + output
        if self.digest:
            output += f"@{self.digest}"
        return output
    
    def __repr__(self) -> str:
        return self.identifier()
