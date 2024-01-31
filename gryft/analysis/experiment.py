# Standard lib
from typing import List, Dict, Tuple
from dataclasses import dataclass
import multiprocess as mp
from functools import reduce

# 3rd Party
import pandas as pd
from tqdm import tqdm

# Local
from gryft.scanning import ImageScanner
from gryft.scanning.image import Image


# def _snapshot_to_row(snapshot: ImageSnapshot):
#     row = pd.Series()
#     row["total_cves"] = snapshot.count_cves()
#     row["severe_cves"] = snapshot.count_cves(severity=["high", "critical"])
#     row["components"] = len(snapshot.components)
#     row["image_sz"] = snapshot.image_sz / 1000000
#     return row


def _process_row(row: pd.Series) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    kwargs = row.to_dict()
    
    for c in ["application", "publisher"]:
        kwargs.pop(c)
    
    image = Image(**kwargs)

    try:
        snapshot = ImageScanner().scan(image)
        
        cves_df = snapshot.cves_as_pandas()
        components_df = snapshot.components_as_pandas()
        size_df = pd.DataFrame({"image_sz": [snapshot.image_sz]})

        attrs = ["registry", "repository", "tag", "digest"]
        
        for df in [cves_df, components_df, size_df]:
            df["publisher"] = row["publisher"]
            df["application"] = row["application"]
            for a in attrs:
                df[a] = getattr(image, a)
            
        return cves_df, components_df, size_df
    
    except ValueError as e:
        print(str(e))


def _collect_snapshots_i(i: int,
                       results: List[Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]
                       ) -> pd.DataFrame:
    dfs = [df[i] for df in results]
    return pd.concat(dfs, axis=0, ignore_index=True)


@dataclass
class ExperimentResults:
    cve_df: pd.DataFrame
    component_df: pd.DataFrame
    size_df: pd.DataFrame


class Experiment:
    # def __init__(self, work_dir: str):
    #     if not os.path.exists(work_dir):
    #         raise FileNotFoundError("`work_dir` does not exist")
    #     self.work_dir = work_dir
    #     self.snapshots = None
    
    # def _persist_snapshots(self):
    #     snaps_dir = os.path.join(self.work_dir, "snapshots")
    #     if os.path.exists(snaps_dir):
    #         shutil.rmtree(snaps_dir)
    #     os.mkdir(snaps_dir)

    #     for publisher, df in self.snapshots.items():
    #         file_path = os.path.join(snaps_dir, f"{publisher}.csv")
    #         df.to_csv(file_path, index=False)
    
    # def _load_snapshots(self) -> Dict[str, pd.DataFrame]:
    #     snaps_dir = os.path.join(self.work_dir, "snapshots")
    #     if not os.path.exists(snaps_dir):
    #         raise FileNotFoundError("No snapshots found in the work directory")
        
    #     self.snapshots = {}

    #     for file_path in glob.glob(os.path.join(snaps_dir, "*.csv")):
    #         publisher = os.path.basename(file_path)[:-4]
    #         df = pd.read_csv(file_path)
    #         self.snapshots[publisher] = df
    
    def run(self, images: pd.DataFrame) -> pd.DataFrame:
        """
        | application | publisher | registry | repository | tag | digest |
        """
        snapshots = {}
        
        rows = [row for _, row in images.iterrows()]
        
        pool = mp.Pool(mp.cpu_count())
        snapshots = list(tqdm(pool.imap_unordered(_process_row, rows),
                            desc=f"Scanning images",
                            total=len(rows)))
        pool.close()
        pool.join()

        cve_df = _collect_snapshots_i(0, snapshots)
        component_df = _collect_snapshots_i(1, snapshots)
        size_df = _collect_snapshots_i(2, snapshots)

        return ExperimentResults(cve_df=cve_df,
                                 component_df=component_df,
                                 size_df=size_df)
    
    # TODO: Remove
    # def _create_pmc_table(self, col: str) -> pd.DataFrame:
    #     out_dfs = []
    #     for publisher, df in self.snapshots.items():
    #         mapper = {col: publisher}
    #         out = df[["application", col]].rename(mapper, axis=1)
    #         out_dfs.append(out)
        
    #     return reduce(lambda left, right: pd.merge(left, right,
    #             on='application', how='inner'), out_dfs)

    # def generate_figures(self, colors: Dict[str, str], options: Dict[str, PMCOptions]=None):
    #     if self.snapshots is None:
    #         self._load_snapshots()
        
    #     figs_dir = os.path.join(self.work_dir, "figures")
    #     if os.path.exists(figs_dir):
    #         shutil.rmtree(figs_dir)
    #     os.mkdir(figs_dir)
        
    #     default_options = PMCOptions(colors)

    #     cols = ["total_cves", "severe_cves", "components", "image_sz"]
    #     titles = ["Total CVEs", "Severe CVEs", "Number of Components", "Image Size (MB)"]

    #     for col, title in zip(cols, titles):
    #         opt = None
    #         if options and (col in options.keys()):
    #             opt = options[col]

    #         tab = self._create_pmc_table(col)
    #         fig, _ = pmc_plot(tab, colors=colors, title=title, options=opt)

    #         fname = col.replace("_", "-") + ".png"
    #         file_path = os.path.join(figs_dir, fname)
    #         fig.savefig(file_path, dpi=200)
