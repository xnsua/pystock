import numba
import numpy

from common.scipy_helper import pdSr, nparr


class StockIndicator:
    @staticmethod
    def mdd_info(arr_like):
        arr = numpy.array(arr_like)
        right = numpy.argmax(numpy.maximum.accumulate(arr) - arr)  # end of the period
        left = numpy.argmax(arr[:right]) if right != 0 else 0  # start of period
        return left, right

    @staticmethod
    def min_poses(arr_like, window_len):
        pdsr = pdSr(arr_like)
        val_r = pdsr.rolling(window=window_len, center=True).min()
        predicate = (val_r == pdsr)
        return predicate.values

    @staticmethod
    def max_poses(arr_like, window_len):
        pdsr = pdSr(arr_like)
        val_r = pdsr.rolling(window=window_len, center=True).max()
        predicate = (val_r == pdsr)
        return predicate.values

    @staticmethod
    @numba.jit('Tuple((i8[:],f8[:]))( f8[:], b1[:], b1[:] )', nopython=True)
    def _jit_trend_len_and_slope(arr_like, is_maxs, is_mins):
        last_index = 0
        trend_len = numpy.zeros_like(arr_like, dtype=numpy.int64)
        slope = numpy.empty_like(arr_like, dtype=numpy.float64)
        # If last index is min value, make index minus
        for i in range(len(arr_like)):
            trend_len[i] = 0
            slope[i] = 0
            if is_mins[i]:
                last_index = i
                break
            elif is_maxs[i]:
                last_index = -i
                break
        if last_index == 0:
            last_index = len(arr_like) - 1
        trend_len[0] = 0
        slope[0] = 0.
        for i in range(1, numpy.abs(last_index) + 1):
            trend_len[i] = i
            slope[i] = (arr_like[i] - arr_like[0]) / i - 0

        new_start = True
        for i in range(numpy.abs(last_index) + 1, len(arr_like)):
            if new_start:
                trend_len[i] = 1
                slope[i] = arr_like[i] - arr_like[i - 1]
                new_start = False
            else:
                abs_last_index = numpy.abs(last_index)
                if is_mins[i] and last_index < 0 or is_maxs[i] and last_index > 0:
                    new_start = True
                    if is_mins[i]:
                        last_index = i
                    else:
                        last_index = -i
                trend_len[i] = trend_len[i - 1] + 1
                slope[i] = (arr_like[i] - arr_like[abs_last_index]) / (i - abs_last_index)
        return trend_len, slope

    @staticmethod
    def trend_len_and_slope(arr_like, window_len):
        is_mins = StockIndicator.min_poses(arr_like, window_len)
        is_maxs = StockIndicator.max_poses(arr_like, window_len)
        val = StockIndicator._jit_trend_len_and_slope(arr_like, is_maxs, is_mins)
        return val


def main():
    arr1 = nparr([1, 2, 1, 0, 1, 2, 3, 2], dtype=numpy.float64)
    val1 = StockIndicator.trend_len_and_slope(arr1, window_len=5)
    print(val1)
    val2 = StockIndicator.trend_len_and_slope(arr1, window_len=5)
    print(val2)

    pass


if __name__ == '__main__':
    main()
