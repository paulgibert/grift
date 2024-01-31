# Standard lib
from typing import Dict, List
from dataclasses import dataclass
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

    def cves_as_pandas(self) -> pd.DataFrame:
        return pd.DataFrame([vars(c) for c in self.cves])
    
    def components_as_pandas(self) -> pd.DataFrame:
        return pd.DataFrame([vars(c) for c in self.components])
