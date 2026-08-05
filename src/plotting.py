import os
from dataclasses import dataclass

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import mpl_fontkit as fk
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.transforms import blended_transform_factory
from mpl_toolkits.mplot3d.axes3d import Axes3D

OUTPUT_DIR = "output/"

fk.install("Noto Sans", verbose=False)
fk.set_font("Noto Sans")
matplotlib.use("qtagg")
plt.rcParams.update(
    {
        "lines.linewidth": 2,
        "text.usetex": True,
        "font.size": 20,
        "font.family": "sans-serif",
        "font.sans-serif": ["Noto Sans"],
        # change default color cycle
        "axes.prop_cycle": matplotlib.cycler(color=["r", "k", "c", "orange"]),
        "text.latex.preamble": r"\usepackage{amsmath}\usepackage[cm]{sfmath}\usepackage{bm}",
    }
)


def get_rows(total: int, cols: int) -> int:
    """
    Get number of rows in plot based on total number of subplots and columns

    :param total: number of subplots
    :param cols: number of columns
    :returns: number of rows
    """
    rows = total // cols
    if total % cols != 0:
        rows += 1
    return rows


@dataclass
class Vline:
    """Parameters for plotting a vertical line"""

    x: float
    """x coordinate of vline"""

    y: float
    """y coordinate used for label"""

    label: str
    """label to be optionally added to plot"""

    color: str = "gray"
    """line color of the vline"""

    linestyle: str = "dashed"
    """line style"""

    ha: str = "right"
    """horizontal alignment of label"""

    va: str = "top"
    """vertical alignment of label"""


class Plot2D:
    def __init__(
        self,
        name: str,
        N_subplots: int = 1,
        cols: int = 1,
        fontsize: int = 20,
        sharex: bool = True,
        title: bool = True,
        gridspec_kw: dict | None = None,
        grid: str | None = None,
    ):
        """
        2D Plot class

        :param name: name of the plot for title and filename
        :param N_subplots: number of subplots
        :param cols: number of columns
        :param fontsize: font size
        :param sharex: whether to share the x-axis
        :param title: whether or not to show the title
        :param gridspec_kw: use to specify ratio of subplot sizes
        :param grid: specify grid axis for ax.grid(), or None. {'both', 'x', 'y'}
        :returns: None
        """
        self.name = name
        self.N_subplots = N_subplots
        self.cols = cols
        self.sharex = sharex
        self.title = title
        gridspec_kw = {} if gridspec_kw is None else gridspec_kw

        plt.rc("font", size=fontsize)
        # --- #
        self._k = -1
        self.colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        self.rows = get_rows(self.N_subplots, self.cols)
        self.axs: list[Axes]
        self.fig, self.axs = plt.subplots(
            self.rows, self.cols, sharex=sharex, gridspec_kw=gridspec_kw
        )
        height = max(10, 2 * N_subplots)
        width = max(10, 5 * cols)
        self.fig.set_size_inches(width, height)
        if self.N_subplots > 1:
            for ax in self.axs:
                if grid is not None:
                    ax.grid(axis=grid)
        else:
            if grid is not None:
                self.axs.grid(axis=grid)

    def get_next_subplot(self, xlab: str, ylab: str, ylab_rotation: int = 90) -> Axes:
        """
        Get the next subplot and add axis labels

        :param xlab: x-axis label
        :param ylab: y-axis label
        :param ylab_rotation: y-axis label orientation
        :returns: Axes object
        """
        self._k += 1
        # ax = self.fig.add_subplot(self.rows, self.cols, self.k)
        if self.N_subplots > 1:
            ax = self.axs[self._k]
        else:
            ax = self.axs

        ax.set_xlabel(xlab)
        ax.set_ylabel(ylab, rotation=ylab_rotation)
        return ax

    def plot_vlines(self, ax: Axes, vlines: list[Vline], show_label=True) -> None:
        """
        Plot list of Vline objects.
        The reason you'd want to do it as a list is that you may want multiple plots with the same vlines representing timesteps

        :param ax: Axes object
        :param vlines: list of Vlines to be plotted
        :param show_label: whether or not to display the vline.label
        :returns: None
        """
        for vline in vlines:
            if show_label:
                ax.text(
                    x=vline.x,
                    y=vline.y,
                    s=vline.label,
                    transform=blended_transform_factory(ax.transData, ax.transAxes),
                    rotation=90,
                    ha=vline.ha,
                    va=vline.va,
                )
            ax.axvline(
                vline.x, color=vline.color, label=vline.label, linestyle=vline.linestyle
            )

    def plot_trendline_aligned(
        self, ax: Axes, x: np.ndarray, y: np.ndarray, c: str
    ) -> None:
        """
        Plot trendline with equation aligned

        :param ax: Axes object
        :param x: x-axis data
        :param y: y-axis data
        :param c: color
        """
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        equation = f"slope = {z[0]:.2f}"
        ax.plot(
            x,
            p(x),
            ls="--",
            c=c,
        )
        ax.text(
            x=x[-1],
            y=p(x)[-1],
            s="\n " + equation,
            rotation=np.rad2deg(np.atan(z[0])),
            rotation_mode="anchor",
            ha="right",
            va="top",
            transform_rotates_text=True,
        )

    def add_legend(
        self,
        ax: Axes,
        handles: list[Artist] | None = None,
        zorder: int | None = None,
        **kwargs,
    ) -> None:
        """
        Add legend without duplicate labels

        :param ax: Axes object
        :param handles: list of Artists to be added to the legend
        :param zorder: drawing order of artists
        :returns: None
        """
        if handles is None:
            handles, labels = plt.gca().get_legend_handles_labels()
        else:
            labels = [x.get_label() for x in handles]
        by_label = dict(zip(labels, handles))
        leg = ax.legend(by_label.values(), by_label.keys(), **kwargs)
        if zorder is not None:
            leg.set_zorder(zorder)

    def adjust_hspace(self, hspace: float) -> None:
        """
        Specify height of padding between subplots
        :param hspace: height of padding
        :returns: None
        """
        self.fig.subplots_adjust(hspace=hspace)

    def set_tight_fig(self) -> None:
        """
        Rearrange figure to prevent overlapping labels, etc.
        """
        self.fig.tight_layout()

    def set_tight_axes(self) -> None:
        """
        Remove whitespace within axes objects
        """
        plt.axis("tight")

    def set_scale_equal(self, ax: Axes) -> None:
        """
        Make axes of 2D plot have equal scale but inequal aspect

        :param ax: matplotlib axis
        :returns: None
        """
        x_limits = ax.get_xlim()
        y_limits = ax.get_ylim()
        x_range = abs(x_limits[1] - x_limits[0])
        y_range = abs(y_limits[1] - y_limits[0])
        ax.set_box_aspect(y_range / x_range)

    def save_img(
        self,
        show: bool = False,
        extension: str = ".png",
        keep_open: bool = False,
    ) -> None:
        """
        Save the image to file.

        :param show: whether or not to bring up interactive GUI
        :param extension: filetype
        :param keep_open: prevent plot from being closed
        :returns: None
        """
        if self.N_subplots > 1:
            self.set_tight_axes()
            self.set_tight_fig()
            for ax in self.axs:
                if self.sharex:
                    ax.label_outer()

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        plt.savefig(
            OUTPUT_DIR + self.name + extension,
            dpi=200,
        )
        if show:
            plt.show()
        elif not keep_open:
            plt.close()


class Plot3D:
    def __init__(
        self,
        name: str,
        N_subplots: int = 1,
        title: bool = True,
        grid: str | None = None,
        **kwargs,
    ):
        """
        3D Plot class

        :param name: name of the plot for title and filename
        :param N_subplots: number of subplots
        :param title: whether or not to show the title
        :param grid: specify grid axis for ax.grid(), or None. {'both', 'x', 'y', 'z'}
        :returns: None
        """

        self.name = name
        self.N_subplots = N_subplots
        self.title = title

        # --- #
        self._k = -1
        self.colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        self.cols = 1
        self.rows = get_rows(self.N_subplots, self.cols)
        self.fig = plt.figure()
        self.fig.set_size_inches(10, 10)
        self.axs: list[Axes3D]
        if N_subplots == 1:
            self.axs = self.fig.add_subplot(projection="3d", **kwargs)
            if grid is not None:
                self.axs.grid(axis=grid)
        else:
            self.axs = self.fig.add_subplot(
                self.rows, self.cols, projection="3d", **kwargs
            )
            for ax in self.axs:
                if grid is not None:
                    ax.grid(axis=grid)

    def get_next_subplot(
        self,
        xlab: str,
        ylab: str,
        zlab: str,
        fsize_label: int = 20,
        **kwargs,
    ) -> Axes3D:
        """
        Get the next subplot and add axis labels

        :param xlab: x-axis label
        :param ylab: y-axis label
        :param zlab: z-axis label
        :param fsize_label: fontsize for labels
        :returns: Axes3D object
        """
        self._k += 1
        # ax = self.fig.add_subplot(self.rows, self.cols, self.k)
        if self.N_subplots > 1:
            ax = self.axs[self._k]
        else:
            ax = self.axs

        ax.set_xlabel("\n" + xlab, fontsize=fsize_label, **kwargs)
        ax.set_ylabel("\n" + ylab, fontsize=fsize_label, **kwargs)
        ax.set_zlabel("\n" + zlab, fontsize=fsize_label, **kwargs)
        return ax

    def set_scale_equal(self, ax: Axes3D) -> None:
        """
        Make axes of 3D plot have equal scale but inequal aspect

        :param ax: Axes3D object
        """
        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()
        x_range = abs(x_limits[1] - x_limits[0])
        y_range = abs(y_limits[1] - y_limits[0])
        z_range = abs(z_limits[1] - z_limits[0])
        ax.set_box_aspect((x_range, y_range, z_range))

    def add_legend(
        self, ax: Axes, handles: list | None = None, zorder: int | None = None, **kwargs
    ) -> None:
        """
        Add legend without duplicate labels

        :param ax: Axes3D object
        :param handles: list of Artists to be added to the legend
        :param zorder: drawing order of artists
        :returns: None
        """
        if handles is None:
            handles, labels = plt.gca().get_legend_handles_labels()
        else:
            labels = [x.get_label() for x in handles]
        by_label = dict(zip(labels, handles))
        leg = ax.legend(by_label.values(), by_label.keys(), **kwargs)
        if zorder is not None:
            leg.set_zorder(zorder)

    def save_img(
        self,
        show: bool = False,
        extension: str = ".png",
        keep_open: bool = False,
    ) -> None:
        """
        Save the image to file.

        :param show: whether or not to bring up interactive GUI
        :param extension: filetype
        :param keep_open: prevent plot from being closed
        :returns: None
        """
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        plt.savefig(OUTPUT_DIR + self.name + extension, dpi=200)
        if show:
            plt.show()
        elif not keep_open:
            plt.close()
