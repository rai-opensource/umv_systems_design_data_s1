import numpy as np
from plotting import Plot2D, Plot3D, Vline
from copy import copy
import pandas as pd
from scipy import signal


def dict_from_csv(path: str) -> dict[str, np.ndarray]:
    """
    Extract timeseries data from csv as dictionary.

    :param path: relative path of file, including extension
    :returns: data dictionary of timeseries
    """
    df = pd.read_csv(path)
    data = {}
    for col in df.columns:
        first = str(df[col].dropna().iloc[0]).strip()
        # check if the data is stored as such: "[1.0 2.0 3.0]"
        if first.startswith("[") and first.endswith("]"):
            # convert to numpy array
            parsed_series = df[col].apply(
                lambda x: np.fromstring(str(x).strip("[]"), sep=" ")
            )
            # stack series of 1D arrays into (N, 3) 2D numpy array
            data[col] = np.vstack(parsed_series)
        else:
            data[col] = df[col].to_numpy()
    return data


def filter_fftconvolve(
    data: np.ndarray, size: int = 50, p: float = 0.5, sig: int = 2
) -> np.ndarray:
    """
    filter data using a convolution.

    :param data: input array.
    :param size:
            Low size = less smoothing, cutoff frequency gets higher.
            High size = more smoothing, cutoff frequency gets lower
    :param p:
            Low p = sharper.
            High p = leads to more rectangular but smoother result.
    :param sig:
            Low sig = less smoothing.
            High sig = more smoothing.
    :returns: filtered array.
    """
    window = signal.windows.general_gaussian(size + 1, p=p, sig=sig)
    filtered = signal.fftconvolve(data, window, mode="same")
    return (np.average(data) / np.average(filtered)) * filtered


def fig_3() -> None:
    """
    Generate figure 3, 3D plot of clearance positions for the lateral hopping experiment
    """
    data = dict_from_csv("csv/fig_3_lateral_hop.csv")
    plot = Plot3D(name="fig_3", N_subplots=1, title=False)
    ax = plot.get_next_subplot(xlab="x (m)", ylab="y (m)", zlab=r"z (m)", labelpad=10)
    pos_clear_hist = data["pos_clear_hist"]
    # air
    pos_clear_air = copy(pos_clear_hist)
    pos_clear_air[:, 0] = np.where(pos_clear_air[:, 2] > 0, pos_clear_air[:, 0], np.nan)
    pos_clear_air[:, 1] = np.where(pos_clear_air[:, 2] > 0, pos_clear_air[:, 1], np.nan)
    pos_clear_air[:, 2] = np.clip(pos_clear_hist[:, 2], 0.0, np.inf)

    # contact
    pos_clear_contact = copy(pos_clear_hist)
    pos_clear_contact[:, 0] = np.where(
        pos_clear_contact[:, 2] < 0, pos_clear_contact[:, 0], np.nan
    )
    pos_clear_contact[:, 1] = np.where(
        pos_clear_contact[:, 2] < 0, pos_clear_contact[:, 1], np.nan
    )
    pos_clear_contact[:, 2] = np.where(
        pos_clear_contact[:, 2] < 0, pos_clear_contact[:, 2], np.nan
    )

    ax.plot(
        *data["pos_com_hist"].T,
        color="b",
        label=r"$p_\text{CoM}$",
        zorder=100,
    )
    ax.plot(
        *pos_clear_contact.T,
        color="purple",
        label=r"$p_\text{clearance}$ in contact",
        zorder=40,
    )
    ax.plot(
        *pos_clear_air.T,
        color="r",
        label=r"$p_\text{clearance}$ in air",
        zorder=50,
    )
    h_clear_hist_filtered = filter_fftconvolve(
        pos_clear_hist[:, 2], size=2500, p=50, sig=250
    )
    # get indices of local minima
    hop_indices = signal.argrelextrema(h_clear_hist_filtered, np.less, order=100)
    footsteps = pos_clear_hist[hop_indices, :]
    heading_vec_hist = data["heading_vec_hist"]
    footstep_heading_vecs = heading_vec_hist[hop_indices, :]

    ax.quiver(
        *footsteps.T,
        *footstep_heading_vecs.T,
        arrow_length_ratio=0.075,
        color="orange",
        label="heading",
        zorder=0,
        capstyle="round",
    )
    ax.set_xticks(np.arange(-0.5, 2.0, 0.5))
    ax.set_zticks(np.arange(0.0, 1.5, 0.5))
    ax.view_init(azim=225, elev=15)
    plot.set_scale_equal(ax)
    ax.set_zlim3d(bottom=0)
    ax.legend(
        loc=(0.65, 0.65),
        framealpha=1.0,
        borderpad=0.1,
        labelspacing=0.1,
    )
    plot.save_img(extension=".pdf")


def fig_4a() -> None:
    """
    Generate figure 4a, clearance height, and electrical power demand for the table jump
    """
    vlines = [
        Vline(
            x=0.85,
            y=0.9,
            label="lift-off",
            ha="right",
            va="top",
        ),
        Vline(
            x=1.2,
            y=0.1,
            label="impact",
            ha="left",
            va="bottom",
        ),
        Vline(
            x=2.95,
            y=0.1,
            label="drop",
            ha="right",
            va="bottom",
        ),
        Vline(
            x=3.25,
            y=0.9,
            label="impact",
            ha="right",
            va="top",
        ),
    ]
    data = dict_from_csv("csv/fig_4a_table_jump.csv")
    plot = Plot2D(
        name="fig_4a",
        N_subplots=3,
        title=False,
        gridspec_kw={"height_ratios": [2, 1, 1]},
    )
    xlab = "Time (s)"
    q_stamps = data["timestamps"]
    ax = plot.get_next_subplot(xlab=xlab, ylab="Height (m)")
    ax.plot(
        q_stamps,
        data["h_com_hist"],
        label=r"$h_\text{CoM}$",
        color="blue",
    )
    ax.plot(
        q_stamps,
        data["h_clear_hist"],
        label=r"$h_\text{clearance}$",
        color="red",
    )
    ax.set_ylim(bottom=0, top=2.5)
    ax.legend()

    if vlines is not None:
        plot.plot_vlines(ax, vlines, show_label=True)

    # Current and Voltage
    m_stamps = data["motor_timestamps"]
    m_current_total = data["motor_current"]
    m_voltage_total = data["motor_voltage"]
    m_power_total = data["motor_power"]
    ax = plot.get_next_subplot(xlab=xlab, ylab="Current (A)")
    (p1,) = ax.plot(m_stamps, m_current_total, label="Current", color="tab:blue")
    ax2 = ax.twinx()
    ax2.set_ylabel("Voltage (V)")
    (p2,) = ax2.plot(m_stamps, m_voltage_total, label="Bus Voltage", color="tab:red")
    ax2.legend(
        handles=[p1, p2],
        loc="center right",
        handlelength=1.0,
        borderpad=0.1,
        labelspacing=0.1,
    )
    if vlines is not None:
        plot.plot_vlines(ax, vlines, show_label=False)

    # Total Power
    ax = plot.get_next_subplot(xlab=xlab, ylab="Power (W)")
    ax.plot(m_stamps, m_power_total, label="Power (W)", color="tab:orange")
    ax.set_yticks(np.arange(-2500, 7500, 2500))
    if vlines is not None:
        plot.plot_vlines(ax, vlines, show_label=False)
    plot.adjust_hspace(0.1)
    plot.save_img(extension=".pdf")


def fig_4b() -> None:
    """
    Generate figure 4b, clearance height for the table jump repeatability experiment
    """
    data = dict_from_csv("csv/fig_4b_table_jump_repeatability.csv")
    plot = Plot3D(name="fig_4b", N_subplots=1, title=False)
    ax = plot.get_next_subplot(xlab="x (m)", ylab="y (m)", zlab=r"z (m)")
    pos_clear_hist = data["pos_clear_hist"]

    # split into individual loops
    h_clear_hist = pos_clear_hist[:, 2]
    N = len(h_clear_hist)
    split_indices = []
    for k in range(1, N):
        if h_clear_hist[k] > 0.1 and h_clear_hist[k - 1] < 0.1:
            # going from below to above a certain height tells us the robot has just started jumping
            split_indices.append(int(np.clip(k - 10, 0, N)))
    trials = np.split(pos_clear_hist, split_indices)
    # the first element isn't a full jump
    trials.pop(0)
    for trial in trials:
        # we only need the first half of each trial, the second half is just driving
        N_trial_half = int(len(trial) / 2)
        trial = trial[:N_trial_half]

    # compute mean
    N_trial = int(max([len(trial) for trial in trials]))
    dim = np.shape(trials[0])[1]
    mean = np.zeros((N_trial, dim))
    for k in range(N_trial):
        trials_k = [item for item in trials if len(item) > k]
        mean[k, :] = np.mean([trial[k] for trial in trials_k], axis=0)

    ax.plot(
        *mean.T,
        color="red",
        label="mean",
        zorder=50,
    )
    ax.plot(
        *pos_clear_hist.T,
        color="lightsalmon",
        label="trials",
        zorder=49,
    )
    plot.add_legend(ax)
    plot.save_img(extension=".pdf")


def fig_5() -> None:
    """
    Generate figure 5, whole-body inertia Iyy and angular velocity during the front flip
    """
    vlines = [
        Vline(
            x=0.45,
            y=0.6,
            label="lift-off",
            ha="right",
            va="top",
        ),
        Vline(
            x=0.9,
            y=0.98,
            label="impact",
            ha="right",
            va="top",
        ),
    ]
    data = dict_from_csv("csv/fig_5_flip.csv")
    timestamps = data["timestamps"]
    I_hist = data["I_hist"]
    h_com_hist = data["h_com_hist"]
    plot = Plot2D(
        name="fig_5",
        N_subplots=3,
        title=False,
        gridspec_kw={"height_ratios": [2, 1, 1]},
    )
    xlab = "Time (s)"
    ax = plot.get_next_subplot(xlab=xlab, ylab=r"$h_\text{CoM}$ (m)")
    ax.plot(
        timestamps,
        h_com_hist,
        label=r"$h_\text{CoM}$",
        color="blue",
    )
    ax.set_ylim(bottom=0, top=1.5)
    if vlines is not None:
        plot.plot_vlines(ax, vlines, show_label=False)

    ax = plot.get_next_subplot(xlab=xlab, ylab="Inertia (kg m²)")
    ax.plot(timestamps, I_hist[:, 0], label=r"$I_\text{xx}$")
    ax.plot(timestamps, I_hist[:, 1], label=r"$I_\text{yy}$")
    ax.plot(timestamps, I_hist[:, 2], label=r"$I_\text{zz}$")
    ax.legend(
        loc="upper right",
        handlelength=1.0,
        borderpad=0.1,
        labelspacing=0.1,
    )
    if vlines is not None:
        plot.plot_vlines(ax, vlines, show_label=True)

    ax = plot.get_next_subplot(xlab=xlab, ylab="Ang. Vel. (rad/s)")
    ax.plot(timestamps, data["angvel_base_hist"][:, 0], label=r"$\omega_x$")
    ax.plot(timestamps, data["angvel_base_hist"][:, 1], label=r"$\omega_y$")
    ax.plot(timestamps, data["angvel_base_hist"][:, 2], label=r"$\omega_z$")
    ax.set_yticks(np.arange(-5.0, 25.0, 5.0))
    ax.legend(
        handlelength=1.0,
        borderpad=0.1,
        labelspacing=0.1,
    )
    if vlines is not None:
        plot.plot_vlines(ax, vlines, show_label=False)
    plot.save_img(extension=".pdf")


if __name__ == "__main__":
    fig_3()
    fig_4a()
    fig_4b()
    fig_5()
