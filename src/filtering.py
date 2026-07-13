from scipy import signal
import numpy as np


def filter_fftconvolve(
    data: np.ndarray, size: int = 50, p: float = 0.5, sig: int = 2
) -> np.ndarray:
    """
    filter data using a convolution.
    ## Arguments
        data: input array.
        size:
            Low size = less smoothing, cutoff frequency gets higher.
            High size = more smoothing, cutoff frequency gets lower
        p:
            Low p = sharper.
            High p = leads to more rectangular but smoother result.
        sig:
            Low sig = less smoothing.
            High sig = more smoothing.
    """
    window = signal.windows.general_gaussian(size + 1, p=p, sig=sig)
    filtered = signal.fftconvolve(data, window, mode="same")
    return (np.average(data) / np.average(filtered)) * filtered


def get_local_minima(data: np.ndarray, order: int = 1) -> list:
    """
    # Arguments
        data: the input
        order: how many points on either side to use for the comparison
    """
    return signal.argrelextrema(data, np.less, order=order)
