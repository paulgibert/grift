# gryft

A fast, bulk image scanner built on grype and syft.

# Example

```
from gryft.scanning.image import Image
from gryft.scanning.scanner import ImageScanner

images = [
  Image("cgr.dev", "chainguard/python", "latest"),
  Image("cgr.dev", "chainguard/redis", "latest"),
  Image("cgr.dev", "chainguard/nginx", "latest"),
  ...
]

scanner = ImageScanner()
snapshots = scanner.scan(images)

print(snapshots[0].cves_as_pandas())

  id	                severity	fix_state
0	CVE-2024-0853	      medium	  fixed
1	GHSA-wr4c-gwg7-p734	unknown	  fixed
2	GHSA-mq8w-c2j9-rqxc	unknown	  fixed
3	GHSA-9xr6-qf7m-2jv5	unknown	  fixed
4	GHSA-97xx-95pm-5qv6	unknown	  fixed
...
```
