# Standard lib
from typing import Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime

# 3rd party
import pandas as pd

# Local
from gryft.scanning.types import CVE, Component
from gryft.scanning.image import Image


@dataclass
class ImageSnapshot:
    image: Image
    scanned_at: datetime
    cves: List[CVE]
    components: List[Component]
    image_sz: int

    def cves_as_pandas(self, include_image=False) -> pd.DataFrame:
        df = pd.DataFrame([vars(c) for c in self.cves])
        if include_image:
            image_dict = asdict(self.image)
            keys = list(image_dict.keys())
            values = list(image_dict.values())
            df[keys] = values
        return df
    
    def components_as_pandas(self, include_image=False) -> pd.DataFrame:
        df = pd.DataFrame([vars(c) for c in self.components])
        if include_image:
            image_dict = asdict(self.image)
            keys = list(image_dict.keys())
            values = list(image_dict.values())
            df[keys] = values
        return df
