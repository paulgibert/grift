# Standrad lib
from typing import Dict, List, Tuple
import json
from datetime import datetime, timezone

# 3rd party
import sh
import pandas as pd
import multiprocess as mp
from tqdm import tqdm

# Local
from gryft.scanning.image import Image
from gryft.scanning.report import GrypeReport, SyftReport
from gryft.scanning.snapshot import ImageSnapshot


def _scan_grype(image: Image) -> Dict:
    """
    Scans an image with grype.
    """
    try:
        json_str = sh.grype(image.identifier(), output="json")
        return json.loads(json_str)
    except sh.ErrorReturnCode_1 as e:
        raise ValueError(f"Image not found ({e.full_cmd} FAILED): " + e.stderr.decode("utf-8"))
    except json.decoder.JSONDecodeError:
        raise RuntimeError(f"Failed to parse JSON from grype scan of {image}:\n{json_str}")


def scan_grype(image: Image) -> GrypeReport:
    data = _scan_grype(image)
    return GrypeReport.from_json(data)


def _scan_syft(image: Image) -> Dict:
    """
    Scans an image with syft.
    """
    try:
        json_str = sh.syft(image.identifier(), output="syft-json")
        return json.loads(json_str)
    except sh.ErrorReturnCode_1 as e:
        raise ValueError(f"Image not found ({e.full_cmd} FAILED): " + e.stderr.decode("utf-8"))
    except json.decoder.JSONDecodeError:
        raise RuntimeError(f"Failed to parse JSON from syft scan of {image}")
    

def scan_syft(image: Image) -> SyftReport:
    data = _scan_syft(image)
    return SyftReport.from_json(data)


class ImageScanner:
    def _scan_image(self, image: Image) -> ImageSnapshot:
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
    
    def _scan_seq(self, images: List[Image]) -> List[ImageSnapshot]:
        snapshots = []
        for image in tqdm(images, desc="Scanning Images"):
            snapshots.append(self._scan_image(image))
        return snapshots

    def _scan_pool(self, images: List[Image], nprocs: int=4) -> List[ImageSnapshot]:
        p = min(nprocs, mp.cpu_count())
        with mp.Pool(p) as pool:
            snapshots = list(tqdm(pool.imap_unordered(self._scan_image, images),
                    desc=f"Scanning images",
                    total=len(images)))
            return snapshots

    def scan(self, source: Image | List[Image],
             nprocs: int=1) -> Image | List[Image]:
        if nprocs < 1:
            raise ValueError("`nprocs` must be >= 1")
        
        if isinstance(source, Image):
            images = [source]
        else:
            images = source
        
        if nprocs == 1:
            snapshots = self._scan_seq(images)
        else:
            snapshots = self._scan_pool(images, nprocs)
        
        if isinstance(source, Image):
            return snapshots[0]
        return snapshots
    
    def scan_pandas(self, df: pd.DataFrame, nprocs: int=4
                    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        images = [Image(**kwargs.to_dict()) for _, kwargs in df.iterrows()]
        snapshots = self.scan(images, nprocs)
        
        cve_df = pd.DataFrame()
        component_df = pd.DataFrame()
        size_df = pd.DataFrame()

        for snap in snapshots:
            cve_df = pd.concat([cve_df, snap.cves_as_pandas(include_image=True)],
                    axis=0)
            component_df = pd.concat([component_df, snap.components_as_pandas(include_image=True)],
                    axis=0)
            size_df = pd.concat([size_df, snap.size_as_pandas(include_image=True)],
                    axis=0)
        
        return cve_df, component_df, size_df