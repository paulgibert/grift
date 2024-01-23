# Standard lib
from typing import Dict, Tuple
from dataclasses import dataclass

# 3rd party
import matplotlib
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd


@dataclass
class PMCStyle:
    colors: Dict[str, str]
    marker_sz: int=20
    line_width: int=1
    title_padding: int=10
    legend_font_sz: int=8
    xtick_font_sz: int=8
    ylabel_font_sz: int=6


def pmc_plot(df: pd.DataFrame, title: str, style: PMCStyle) -> Tuple[Figure, Axes]:
    """
    | application | publisher 1 | publisher 2 | ... | publisher N |
    """
    
    cols = list(df.columns)
    cols.remove("application")
    
    fig, ax = plt.subplots()
    fig.tight_layout()
    plt.subplots_adjust(left=0.15, top=0.90)

    sns.despine(ax=ax)
    matplotlib.rcParams["font.family"] = "serif"
    
    y = np.arange(0, df.shape[0])
    for col in cols:
        x = df[col].to_numpy()
        color = style.colors[col]
        ax.scatter(x, y, color=color, s=style.marker_sz,
                   label=col)
        ave = np.mean(x)
        ax.vlines(ave, 0, len(y), color=color,
                  linewidth=style.line_width,
                  linestyle="--",
                  zorder=-1)
        ax.annotate(str(int(ave)),xy=(ave+2,len(y)-0.5), fontsize=style.xtick_font_sz)
        

    ax.set_title(title, pad=style.title_padding)
    ax.legend(loc='upper right', ncols=1,
              fontsize=style.legend_font_sz)
    
    # Set min x axis value to 0
    ax.margins(x=0)

    ax.tick_params(axis='x', which='both', labelsize=style.xtick_font_sz)

    ax.set_yticks(y, df["application"].to_numpy(),
                  fontsize=style.ylabel_font_sz)
    

    return fig, ax
