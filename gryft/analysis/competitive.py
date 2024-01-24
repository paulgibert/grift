# Standard lib
from typing import List, Dict
import os
import multiprocessing as mp
import shutil
import glob
from functools import reduce

# 3rd Party
import pandas as pd
from tqdm import tqdm

# Local
from gryft.scanning import ImageScanner
from gryft.scanning.image import Image
from gryft.scanning.snapshot import ImageSnapshot
from gryft.analysis.plot import pmc_plot, PMCOptions


def _snapshot_to_row(snapshot: ImageSnapshot):
    row = pd.Series()
    row["total_cves"] = snapshot.count_cves()
    row["severe_cves"] = snapshot.count_cves(severity=["high", "critical"])
    row["components"] = len(snapshot.components)
    row["image_sz"] = snapshot.image_sz / 1000000
    return row


def _process_row(row: pd.Series):
    kwargs = row.to_dict()
    kwargs.pop("application")
    
    image = Image(**kwargs)

    try:
        snapshot = ImageScanner().scan(image)
        
        new_row = _snapshot_to_row(snapshot)
        new_row = pd.concat([row, new_row])
        new_row = pd.DataFrame(new_row.to_dict(), index=[0])
        return new_row
    
    except ValueError as e:
        print(str(e))


class CompetitiveAnalysis:
    def __init__(self, work_dir: str):
        if not os.path.exists(work_dir):
            raise FileNotFoundError("`work_dir` does not exist")
        self.work_dir = work_dir
        self.snapshots = None
    
    def _persist_snapshots(self):
        snaps_dir = os.path.join(self.work_dir, "snapshots")
        if os.path.exists(snaps_dir):
            shutil.rmtree(snaps_dir)
        os.mkdir(snaps_dir)

        for publisher, df in self.snapshots.items():
            file_path = os.path.join(snaps_dir, f"{publisher}.csv")
            df.to_csv(file_path, index=False)
    
    def _load_snapshots(self) -> Dict[str, pd.DataFrame]:
        snaps_dir = os.path.join(self.work_dir, "snapshots")
        if not os.path.exists(snaps_dir):
            raise FileNotFoundError("No snapshots found in the work directory")
        
        self.snapshots = {}

        for file_path in glob.glob(os.path.join(snaps_dir, "*.csv")):
            publisher = os.path.basename(file_path)[:-4]
            df = pd.read_csv(file_path)
            self.snapshots[publisher] = df
    
    def run(self, images: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        | application | publisher | registry | repository | tag | digest |
        """
        snapshots = {}
        
        for publisher, df in images.items():
            rows = [row for _, row in df.iterrows()]
            
            pool = mp.Pool(mp.cpu_count())
            result = list(tqdm(pool.imap_unordered(_process_row, rows),
                                desc=f"Scanning {publisher}",
                                total=len(rows)))
            pool.close()
            pool.join()
            df_out = pd.concat(result, axis=0, ignore_index=True)
            snapshots[publisher] = df_out

        self.snapshots = snapshots
        self._persist_snapshots()
    
    def _create_pmc_table(self, col: str) -> pd.DataFrame:
        out_dfs = []
        for publisher, df in self.snapshots.items():
            mapper = {col: publisher}
            out = df[["application", col]].rename(mapper, axis=1)
            out_dfs.append(out)
        
        return reduce(lambda left, right: pd.merge(left, right,
                on='application', how='inner'), out_dfs)

    def generate_figures(self, colors: Dict[str, str], options: Dict[str, PMCOptions]=None):
        if self.snapshots is None:
            self._load_snapshots()
        
        figs_dir = os.path.join(self.work_dir, "figures")
        if os.path.exists(figs_dir):
            shutil.rmtree(figs_dir)
        os.mkdir(figs_dir)
        
        default_options = PMCOptions(colors)

        cols = ["total_cves", "severe_cves", "components", "image_sz"]
        titles = ["Total CVEs", "Severe CVEs", "Number of Components", "Image Size (MB)"]

        for col, title in zip(cols, titles):
            opt = None
            if options and (col in options.keys()):
                opt = options[col]

            tab = self._create_pmc_table(col)
            fig, _ = pmc_plot(tab, colors=colors, title=title, options=opt)

            fname = col.replace("_", "-") + ".png"
            file_path = os.path.join(figs_dir, fname)
            fig.savefig(file_path)
