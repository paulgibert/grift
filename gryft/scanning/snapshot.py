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
    distro: str
    image_sz: int

    def cves_as_pandas(self, include_image=False) -> pd.DataFrame:
        if len(self.cves) == 0:
            return pd.DataFrame(columns=["id", "severity", "fix_state",
                                         "component.name", "component.version", "component.type_"])
        df = pd.DataFrame(map(asdict, self.cves))
        component_df = df["component"].apply(pd.Series)
        component_df.columns = ["component." + col for col in component_df.columns]
        df = df.drop("component", axis=1).join(component_df)

        if include_image:
            image_dict = vars(self.image)
            keys = list(image_dict.keys())
            values = list(image_dict.values())
            df[keys] = values
        return df
    
    def components_as_pandas(self, include_image=False) -> pd.DataFrame:
        if len(self.components) == 0:
            return pd.DataFrame(columns=["name", "version", "type_"])
        df = pd.DataFrame(map(asdict, self.components))
        if include_image:
            image_dict = vars(self.image)
            keys = list(image_dict.keys())
            values = list(image_dict.values())
            df[keys] = values
        return df
    
    def size_as_pandas(self, include_image=False) -> pd.DataFrame:
        df = pd.DataFrame({"image_sz": self.image_sz}, index=[0])
        if include_image:
            image_dict = vars(self.image)
            keys = list(image_dict.keys())
            values = list(image_dict.values())
            df[keys] = values
        return df
