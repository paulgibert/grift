# Standard lib
from typing import Tuple, List

# 3rd party
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


class PMCPlot:
    def __init__(self, figsize: Tuple[int, int]=None,
                 marker_sz: float=20, line_width: float=1,
                 x_font_sz: int=10,
                 y_font_sz: int=8,
                 legend_font_sz: int=12):
        self._fig, self._ax = plt.subplots(figsize=figsize)
        self._y_map = []
        self._ave_lines = []

        # Figure configs
        self.marker_sz = marker_sz
        self.line_width = line_width
        self.x_font_sz = x_font_sz
        self.y_font_sz = y_font_sz
        self.legend_font_sz = legend_font_sz

        # Figure adjustments
        matplotlib.rcParams["font.family"] = "serif"
        sns.despine(ax=self._ax)


    def _adjust_ax(self):
        # Axis adjustments
        N = len(self._y_map)
        self._ax.margins(x=0)
        self._ax.set_ylim((-0.5, N-0.5))
        self._ax.tick_params(axis='x', which='both', labelsize=self.x_font_sz)
        self._ax.set_yticks(np.arange(N), self._y_map,
                            fontsize=self.y_font_sz)
    
    def _get_y(self, applications: List[str]):
        for app in applications:
            if app not in self._y_map:
                self._y_map.append(app)    
        return np.array([self._y_map.index(app) for app in applications])
    
    def plot(self, data: np.ndarray, applications: List[str], label: str=None, color: str=None) -> float:
        y = self._get_y(applications)
        self._ax.scatter(data, y, color=color, s=self.marker_sz,
                         label=label)
        
        ave = np.mean(data)
        self._ave_lines.append((ave, color))
        
        
        self._adjust_ax()
        self._fig.tight_layout()

        return ave

    def average_lines(self):
        N = len(self._y_map)
        for ave, color in self._ave_lines:
            self._ax.vlines(ave, 0, N, color=color,
                            linewidth=self.line_width,
                            linestyle="--",
                            zorder=-1)
        
            ylim = self._ax.get_ylim()[1] + 0.5
            text = str(np.round(ave, decimals=1))
            self._ax.text(ave, ylim, text, ha='center',
                        va='bottom', color=color,
                        fontsize=self.x_font_sz)

    def set_title(self, label: str, pad: int=20):
        self._ax.set_title(label, pad=pad)
        self._fig.tight_layout()
    
    def set_xlabel(self, label: str):
        self._ax.set_xlabel(label)
        self._fig.tight_layout()

    def set_ylabel(self, label: str):
        self._ax.set_ylabel(label)
        self._fig.tight_layout()
    
    def set_xlim(self, *args, **kwargs):
        self._ax.set_xlim(*args, **kwargs)

    def legend(self, *args, **kwargs):
        default_kwargs = {
            "loc": "upper right",
            "ncols": 1,
            "fontsize": self.legend_font_sz,
            "framealpha": 0.5,
            "bbox_to_anchor": (1, 0.9),
            "bbox_transform": plt.gcf().transFigure
        }

        default_kwargs.update(kwargs)

        self._fig.legend(*args, **default_kwargs)
        self._fig.tight_layout()
    
    def savefig(self, *args, **kwargs):
        self._fig.savefig(*args, **kwargs)
