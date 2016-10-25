import numpy as np
from abc import abstractclassmethod
from typing import List
from os.path import join as opjoin
from os.path import exists as opexist
from os import remove
from resonancesml.shortcuts import get_target_vector
from resonancesml.shortcuts import ProgressBar


class ADatasetInjection(object):
    def __init__(self, headers: List[str]):
        super(ADatasetInjection, self).__init__()
        self.headers = headers


    @abstractclassmethod
    def update_data(self, X: np.ndarray) -> np.ndarray:
        pass


class KeplerInjection(ADatasetInjection):
    def update_data(self, X: np.ndarray) -> np.ndarray:
        axises = np.array(X[:,2], dtype='float64')
        mean_motions = np.sqrt([0.0002959122082855911025 / axises ** 3.])
        X = np.hstack((X, mean_motions.T))
        return X


class _DataFilter(ADatasetInjection):
    def __init__(self, headers: List[str], resonant_axis: float, axis_swing: float, axis_index: int):
        super(_DataFilter, self).__init__(headers)
        self.axis_swing = axis_swing
        self.axis_index = axis_index
        self.resonant_axis = resonant_axis

    def update_data(self, X: np.ndarray) -> np.ndarray:
        X = X[np.where(np.abs(X[:, self.axis_index] - self.resonant_axis) <= self.axis_swing)]
        #integers = np.array([[5, -2, -2]] * X.shape[0])
        #X = np.hstack((X, integers))
        return X


class ClearDecorator(_DataFilter):
    """
    ClearDecorator clears off asteroids with unsuitable axis passed data.
    Axises will be got by index form dataset. Suitable axis is determined by
    absolute value of subtraheading of resonant axis and axis swing.
    """
    def __init__(self, decorating: ADatasetInjection, resonant_axis,
                 axis_swing: float, axis_index: int):
        super(ClearDecorator, self).__init__(decorating.headers, resonant_axis,
                                             axis_swing, axis_index)
        self._decorating = decorating

    def update_data(self, X: np.ndarray) -> np.ndarray:
        X = super(ClearDecorator, self).update_data(X)
        return self._decorating.update_data(X)


class ClearInjection(ADatasetInjection):
    def __init__(self, resonant_axis: float, axis_swing: float, axis_index: int):
        super(ClearInjection, self).__init__([], resonant_axis, axis_swing, axis_index)


class ClearKeplerInjection(KeplerInjection):
    def __init__(self, headers: List[str], resonant_axis, axis_swing: float, axis_index: int):
        super(ClearKeplerInjection, self).__init__(headers, resonant_axis, axis_swing, axis_index)

    def update_data(self, X: np.ndarray) -> np.ndarray:
        X = super(ClearKeplerInjection, self).update_data(X)
        return X

class IntegersInjection(ADatasetInjection):
    """
    InegersInjection adds integers satisfying D'Alambert of every resonance
    that suitable for asteroid by semi major axis. If seeveral resonances are
    suitable for one resonance, vector of features will be duplicated.
    """
    def __init__(self, headers: List[str], filepath: str, axis_index: int, librations_folder: str,
                 clear_cache: bool):
        super(IntegersInjection, self).__init__(headers)
        self._resonances = np.loadtxt(filepath, dtype='float64')
        self._axis_index = axis_index
        self._librations_folder = librations_folder
        self._clear_cache = clear_cache
        self._data_len = None
        self._INTEGERS_LEN = 3

    def set_data_len(self, value):
        self._data_len = value

    def _get_resonance_dataset(self, for_feature_matrix: np.ndarray, for_resonance: np.ndarray,
                               librating_asteroids: np.ndarray) -> np.ndarray:
        """
        _get_resonance_dataset prepares dataset for one resonance.
        It makes:
            1) 3 features contains integers, satisfying D'Alambert rule.
            2) Feature vector contains squares of difference between resonance
            semi-major axis and asteroid semi-major axis.
            3) Target vector and moves it to right.
        """
        #if not len(librating_asteroid_vector.shape):
            #resonance_librations_count = 1
        #else:
            #resonance_librations_count = librating_asteroid_vector.shape[0]
        Y = get_target_vector(librating_asteroids, for_feature_matrix.astype(int))
        #Y = np.zeros(feature_matrix.shape[0])
        #resonance_librations_count = 0

        N = for_feature_matrix.shape[0]
        #integers_value = str(resonance[:integers_len])[1:-1].strip().replace('.', '')
        integers = np.tile(np.hstack(for_resonance[:self._INTEGERS_LEN]), (N, 1))
        for_feature_matrix = np.hstack((for_feature_matrix, integers))
        resonant_axis = for_resonance[-1:]
        axis_diffs = np.array([np.power((for_feature_matrix[:, 2] - resonant_axis), 2)]).T
        #axis_diffs = np.array([feature_matrix[:, 2] - resonant_axis]).T
        for_feature_matrix = np.hstack((for_feature_matrix, axis_diffs))

        #librations_count += resonance_librations_count
        #feature_matrix = np.hstack((feature_matrix, np.repeat(resonance_librations_count, N).reshape(1, N).T))
        dataset = np.hstack((for_feature_matrix, np.array([Y]).T))
        return dataset

    def update_data(self, X: np.ndarray) -> np.ndarray:
        X[:, 0] = X[:, 0].astype(int)
        cache_filepath = '/tmp/cache.txt'
        if self._clear_cache:
            try:
                remove(cache_filepath)
            except Exception:
                pass
        if opexist(cache_filepath):
            print('dataset has been loaded from cache')
            res = np.loadtxt(cache_filepath)
            return res[:self._data_len]

        print('\n')
        bar = ProgressBar(self._resonances.shape[0], 80, 'Building dataset')
        res = np.zeros((1, X.shape[1] + 5))
        #librations_count = 0
        for resonance in self._resonances:  # type: np.ndarray
            bar.update()
            axis = resonance[6]
            feature_matrix = X[np.where(np.abs(X[:, self._axis_index] - axis) <= 0.01)]
            if not feature_matrix.shape[0]:
                continue

            filename = 'JUPITER-SATURN_%s' % '_'.join([
                str(int(x)) for x in resonance[:self._INTEGERS_LEN]])
            librated_asteroid_filepath = opjoin(self._librations_folder, filename)
            if not opexist(librated_asteroid_filepath):
                continue

            librating_asteroid_vector = np.loadtxt(librated_asteroid_filepath, dtype=int)
            if not librating_asteroid_vector.shape or librating_asteroid_vector.shape[0] < 50:
                continue

            dataset = self._get_resonance_dataset(feature_matrix, resonance,
                                                  librating_asteroid_vector)
            res = np.vstack((res, dataset))

        res = np.delete(res, 0, 0)
        #libration_probability_vector = np.array([res[:,-2] / librations_count]).T
        #res = np.hstack((res, libration_probability_vector))
        #res[:,[-1,-2]] = res[:,[-2,-1]]
        sorted_res = res[res[:,0].argsort()]
        np.savetxt(cache_filepath, sorted_res,
                   fmt='%d %f %f %f %f %.18e %.18e %.18e %.18e %d %d %d %d %f %d')
                   #fmt='%d %f %f %f %f %.18e %.18e %.18e %.18e %d %d %d %d %d')
                   #fmt='%s %f %f %f %f %.18e %.18e %.18e %.18e %d %d %d %d %d %d %f')
        return sorted_res[:self._data_len]
