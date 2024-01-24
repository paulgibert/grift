# Standard lib
from typing import Dict, Tuple, List
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
class PMCOptions:
    marker_sz: int=20
    line_width: int=1
    title_padding: int=10
    legend_font_sz: int=8
    xtick_font_sz: int=10
    ylabel_font_sz: int=8
    xlims: List=None


def _get_x_ranges(df: pd.DataFrame, threshold: float=0.15, max_breaks: int=1) -> List[Tuple]:
    """
    TODO: Support max_breaks >= 1
    """
    x = sorted(pd.concat([df[col] for col in df.drop(["application"], axis=1)]).tolist())
    x_max = np.max(x)
    
    diff = np.diff(x)
    i = np.argmax(np.diff(x))

    pad = x_max // 100

    if max_breaks == 0:
        return [(0, x_max + pad)]
    
    if max_breaks > 1:
        raise NotImplementedError("Values for `max_breaks` > 1 are not supported")

    if diff[i] > x_max * threshold:
        return [(0, x[i] + pad), (x[i+1] - pad, x_max + pad)]
    
    return [(0, x_max + pad)]


def pmc_plot(df: pd.DataFrame, colors: Dict[str, str], title: str, options: PMCOptions=None) -> Tuple[Figure, Axes]:
    """
    | application | publisher 1 | publisher 2 | ... | publisher N |
    TODO: This is pretty messy. Need to clean the code up.
    """
    matplotlib.rcParams["font.family"] = "serif"

    if options is None:
        options = PMCOptions()
    
    if options.xlims is None:
        options.xlims = _get_x_ranges(df, max_breaks=0)

    cols = list(df.columns)
    cols.remove("application")

    n_axes = len(options.xlims)
    fig, axes = plt.subplots(1, n_axes, sharey=True)

    if n_axes == 1:
        axes = [axes] # Wrap axes to ensure it is iterable

    fig.tight_layout()
    plt.subplots_adjust(left=0.15, top=0.90, wspace=0.05)

    y = np.arange(0, df.shape[0])

    for i, xlim, ax in zip(range(n_axes), options.xlims, axes):
        sns.despine(ax=ax)

        for col in cols:
            x = df[col].to_numpy()
            color = colors[col]
            if i == 0:
                ax.scatter(x, y, color=color, s=options.marker_sz,
                    label=col)
                ave = np.mean(x)
                ax.vlines(ave, 0, len(y), color=color,
                        linewidth=options.line_width,
                        linestyle="--",
                        zorder=-1)
                ax.text(ave, ax.get_ylim()[1], str(np.round(ave, decimals=1)),
                        ha='center', va='bottom', color=color,
                        fontsize=options.xtick_font_sz)
            else:
                ax.scatter(x, y, color=color, s=options.marker_sz)
        
        ax.set_xlim(xlim)
        ax.tick_params(axis='x', which='both', labelsize=options.xtick_font_sz)
        
        if i == 0:
            ax.spines.right.set_visible(False)
            ax.set_yticks(y, df["application"], fontsize=options.ylabel_font_sz)
        else:
            ax.spines.left.set_visible(False)
            ax.yaxis.set_visible(False)

            # Plot slanted line markers at each break
            kwargs = dict(marker=[(-0.5, -1), (0.5, 1)], markersize=options.xtick_font_sz,
                          linestyle="none", color='k', mec='k', mew=1, clip_on=False)
            ax.plot(0, 0, transform=ax.transAxes, **kwargs)
            axes[i-1].plot(1, 0, transform=axes[i-1].transAxes, **kwargs)


    fig.suptitle(title)
    fig.legend(loc='upper right', ncols=1,
              fontsize=options.legend_font_sz)
    
    # Set min x axis value to 0
    
    
    return fig, ax