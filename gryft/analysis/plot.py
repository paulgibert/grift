# Standard lib
from typing import Dict, Tuple, List
from dataclasses import dataclass

# 3rd party
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd


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


def _get_xmax(df: pd.DataFrame) -> float:
    x = sorted(pd.concat([df[col] for col in df.drop(["application"], axis=1)]).tolist())
    return np.max(x)


def _get_width_ratios(xmax: float, brk: Tuple[int, int]) -> Tuple[float, float]:
    # series = [0, brk[0], brk[1], xmax]
    # diff = np.diff(series) / xmax
    # return diff[0], diff[1] + diff[2]
    r0 = brk[0]
    s0 = r0 / xmax
    r1 = xmax - brk[1]
    s1 = r1 * s0 / r0
    print(s0, s1)
    return s0, 1 - s0


class PMCPlot:
    def __init__(self, apps: List[str],
                 figsize: Tuple[int, int]=None,
                 marker_sz: float=20, line_width: float=1,
                 x_font_sz: int=10,
                 y_font_sz: int=8,
                 legend_font_sz: int=10):
        self._fig, self._ax = plt.subplots(figsize=figsize)
        self.apps = apps
        self._N = len(apps)

        # Figure configs
        self.marker_sz = marker_sz
        self.line_width = line_width
        self.x_font_sz = x_font_sz
        self.y_font_sz = y_font_sz
        self.legend_font_sz = legend_font_sz

        # Figure adjustments
        matplotlib.rcParams["font.family"] = "serif"
        sns.despine(ax=self._ax)
        
        # Axis adjustments
        self._ax.margins(x=0)
        self._ax.set_ylim((-0.5, self._N-0.5))
        self._ax.tick_params(axis='x', which='both', labelsize=self.x_font_sz)
        self._ax.set_yticks(np.arange(self._N), self.apps,
                            fontsize=self.y_font_sz)

    def plot(self, data: np.ndarray, label: str=None, color: str=None) -> float:
        if len(data) != len(self.apps):
            raise ValueError(f"`data` and `apps` length must be the same. {len(data)} != {len(self._N)}")
        
        y = np.arange(self._N)   
    
        self._ax.scatter(data, y, color=color, s=self.marker_sz,
                         label=label)
        
        ave = np.mean(data)
        self._ax.vlines(ave, 0, self._N, color=color,
                        linewidth=self.line_width,
                        linestyle="--",
                        zorder=-1)
        
        ylim = self._ax.get_ylim()[1]
        text = str(np.round(ave, decimals=1))
        self._ax.text(ave, ylim, text, ha='center',
                      va='bottom', color=color,
                      fontsize=self.x_font_sz*0.8)
        
        self._fig.tight_layout()

        return ave

    def set_title(self, label: str, pad: int=20):
        self._ax.set_title(label, pad=pad)
        self._fig.tight_layout()
    
    def set_xlabel(self, label: str):
        self._ax.set_xlabel(label)
        self._fig.tight_layout()

    def set_ylabel(self, label: str):
        self._ax.set_ylabel(label)
        self._fig.tight_layout()

    def legend(self, loc: str="upper right",
               ncols: int=1):
        self._fig.legend(loc=loc, ncols=ncols,
                         fontsize=self.legend_font_sz,
                         bbox_to_anchor=(1, 0.9),
                         bbox_transform=plt.gcf().transFigure)
        self._fig.tight_layout()

    
# def pmc_plot(df: pd.DataFrame, colors: Dict[str, str], title: str, options: PMCOptions=None) -> Tuple[Figure, Axes]:
#     """
#     | application | publisher 1 | publisher 2 | ... | publisher N |
#     TODO: This is pretty messy. Need to clean the code up.
#     """
#     matplotlib.rcParams["font.family"] = "serif"

#     if options is None:
#         options = PMCOptions()

#     cols = list(df.columns)
#     cols.remove("application")

#     xmax = _get_xmax(df)
#     width_ratios = _get_width_ratios(xmax, options.xaxis_break)
#     fig, axes = plt.subplots(1, 2, sharey=True, width_ratios=width_ratios)
#     fig.tight_layout()

#     plt.subplots_adjust(left=0.20, top=0.90, wspace=0.05)

#     y = np.arange(0, df.shape[0])
#     # sns.despine(ax=ax)    

#     for col in cols:
#         x = df[col].to_numpy()
#         ave = np.mean(x)
#         color = colors[col]
    
#         axes[0].scatter(x, y, color=color, s=options.marker_sz,
#                         label=col)
#         axes[1].scatter(x, y, color=color, s=options.marker_sz)
        
#         ave = np.mean(x)
#         axes[0].vlines(ave, 0, len(y), color=color,
#                        linewidth=options.line_width,
#                        linestyle="--",
#                        zorder=-1)
        
#         axes[0].text(ave, axes[0].get_ylim()[1], str(np.round(ave, decimals=1)),
#                      ha='center', va='bottom', color=color,
#                      fontsize=options.xtick_font_sz)
    
#     # x axis
#     axes[0].tick_params(axis='x', which='both', labelsize=options.xtick_font_sz)
#     axes[1].tick_params(axis='x', which='both', labelsize=options.xtick_font_sz)
    
#     # limit x axis
#     axes[0].set_xlim((0, options.xaxis_break[0]))
#     axes[1].set_xlim((options.xaxis_break[1], xmax))
        
#     # Remove artifacts
#     axes[0].spines.right.set_visible(False)
#     axes[0].set_yticks(y, df["application"], fontsize=options.ylabel_font_sz)
    
#     axes[1].spines.left.set_visible(False)
#     axes[1].yaxis.set_visible(False)

#     # Plot slanted line markers at the break
#     kwargs = dict(marker=[(-0.5, -1), (0.5, 1)], markersize=options.xtick_font_sz,
#                     linestyle="none", color='k', mec='k', mew=1, clip_on=False)
#     axes[0].plot(0, 0, transform=axes[0].transAxes, **kwargs)
#     axes[1].plot(1, 0, transform=axes[1].transAxes, **kwargs)

#     # Set figure params
#     fig.suptitle(title)
#     fig.legend(loc='upper right', ncols=1,
#                fontsize=options.legend_font_sz)
    
#     return fig, axes