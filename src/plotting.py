from dataclasses import dataclass
import matplotlib
import matplotlib.pyplot as plt
import mpl_fontkit as fk
from matplotlib.axes import Axes
from matplotlib.transforms import blended_transform_factory
from mpl_toolkits.mplot3d.axes3d import Axes3D
import os

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
        "text.latex.preamble": "".join(
            [
                r"\usepackage{amsmath}",
                r"\usepackage[cm]{sfmath}",  # makes arbitrary fonts compat with latex
                r"\usepackage{bm}",  # for \boldsymbol{}
            ]
        ),
    }
)


def get_rows(total: int, cols: int) -> int:
    rows = total // cols
    if total % cols != 0:
        rows += 1
    return rows


@dataclass
class Vline:
    x: float
    y: float
    label: str
    color: str = "gray"
    linestyle: str = "dashed"
    ha: str = "right"
    va: str = "top"


class Plot2D:
    def __init__(
        self,
        name: str,
        N_subplots: int = 1,
        cols: int = 1,
        fontsize: int = 20,
        sharex: bool = True,
        title: bool = True,
        gridspec_kw: dict = {},
        grid: str | None = None,
    ):
        """
        Plotting class

        :param name: name of the plot for title and filename
        :param N_subplots: number of subplots
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
        """move to and return next subplot"""
        self._k += 1
        # ax = self.fig.add_subplot(self.rows, self.cols, self.k)
        if self.N_subplots > 1:
            ax = self.axs[self._k]
        else:
            ax = self.axs

        ax.set_xlabel(xlab)
        ax.set_ylabel(ylab, rotation=ylab_rotation)
        return ax

    def plot_vlines(self, ax: Axes, vlines: list, show_label=True) -> None:
        # the reason you'd want to do it as a list is that you may want multiple plots with the same vlines representing timesteps
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

    def add_legend(
        self, ax: Axes, handles: list | None = None, zorder: int | None = None, **kwargs
    ) -> None:
        # adds legend without duplicate labels
        if handles is None:
            handles, labels = plt.gca().get_legend_handles_labels()
        else:
            labels = [x.get_label() for x in handles]
        by_label = dict(zip(labels, handles))
        leg = ax.legend(by_label.values(), by_label.keys(), **kwargs)
        if zorder is not None:
            leg.set_zorder(zorder)

    def adjust_hspace(self, hspace: float) -> None:
        # hspace: specify height of padding between subplots
        self.fig.subplots_adjust(hspace=hspace)

    def set_tight_fig(self) -> None:
        """
        tight_fig: rearrange figure to prevent overlapping labels, etc.
        """
        self.fig.tight_layout()

    def set_tight_axes(self) -> None:
        """
        tight_axes: remove whitespace within axes objects
        """
        plt.axis("tight")

    def set_scale_equal(self, ax: Axes) -> None:
        """
        Make axes of 2D plot have equal scale but inequal aspect

        ## Input
            ax: matplotlib axis
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
        show: whether or not to bring up interactive GUI
        """
        self.set_tight_axes()
        self.set_tight_fig()
        if self.N_subplots > 1:
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
        return None


class Plot3D:
    def __init__(
        self,
        name: str,
        N_subplots: int = 1,
        title: bool = True,
        grid: str | None = None,
        **kwargs,
    ):
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
        """move to and return next subplot"""
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

        ## Input
            ax: matplotlib axis
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
        # adds legend without duplicate labels
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
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        plt.savefig(OUTPUT_DIR + self.name + extension, dpi=200)
        if show:
            plt.show()
        elif not keep_open:
            plt.close()
        return None
