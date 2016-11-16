from resonancesml.settings import SYN_CATALOG_PATH
from resonancesml.settings import CAT_CATALOG_PATH
from resonancesml.settings import PRO_CATALOG_PATH

from typing import List

from enum import Enum
from enum import unique

from .datainjection import ADatasetInjection
from .datainjection import KeplerInjection


@unique
class Catalog(Enum):
    syn = 'syn'
    cat = 'cat'
    pro = 'pro'

    @property
    def axis_index(self) -> int:
        return {
            'syn': 2,
            'cat': 2,
            'pro': 1,
        }[self.value]


class DatasetParameters:
    """
    DatasetParameters stores parameters for reading data from source and building dataset.
    """
    def __init__(self, indices_cases: List[List[int]], catalog_path: str, catalog_width: int,
                 delimiter: str, skiprows: int, injection: ADatasetInjection = None,
                 dataset_end: int = None):
        """
        :param indices_cases: matrix of indices that will be used for pointing
        data from dataset when it will be modifyied by injection.
        :param catalog_path: path to catalog contains asteroid numbers and Kepler elements.
        :param catalog_width: number of columns in catalog.
        :param delimiter: delimiter between headers in the catalog.
        :param skiprows: number of rows that should be skiped.
        :param injection: injection intended for modifying the dataset.
        :param dataset_end: number of last row. It is necessary if catalog should be loaded particularly.
        """
        self.indices_cases = indices_cases
        self.catalog_path = catalog_path
        self.catalog_width = catalog_width
        self.delimiter = delimiter
        self.skiprows = skiprows
        self.injection = injection
        if dataset_end is not None:
            assert dataset_end >= skiprows
            self.dataset_end = dataset_end - skiprows
        else:
            self.dataset_end = None


class CatalogException(Exception):
    def __init__(self, message = None):
        if not message:
            message = 'Unsupported catalog type'
        super(Exception, self).__init__(message)


def get_injection(by_catalog: Catalog) -> ADatasetInjection:
    if by_catalog == by_catalog.syn:
        return None
    elif by_catalog == by_catalog.cat:
        return KeplerInjection(['n'])
    raise CatalogException()


def get_learn_parameters(catalog: Catalog, injection: ADatasetInjection,
                               indices: List[List[int]] = None) -> DatasetParameters:
    if catalog == Catalog.syn:
        return DatasetParameters([[2,3,4,5],[2,3,5]] if not indices else indices,
                                SYN_CATALOG_PATH, 10, '  ', 2, injection, 406253)
    elif catalog == Catalog.cat:
        return DatasetParameters([[2, 3, 10], [2, 3, 4, 10]] if not indices else indices,
                                CAT_CATALOG_PATH, 8, "\.|,", 6, injection)
    elif catalog == Catalog.pro:
        return DatasetParameters([[1, 2], [1, 2, 3]] if not indices else indices,
                                PRO_CATALOG_PATH, 6, ";", 3, injection)
    raise CatalogException()


def get_compare_parameters(catalog: Catalog, injection: ADatasetInjection) -> DatasetParameters:
    if catalog == Catalog.syn:
        return DatasetParameters([[2,3,4],[2,3,5],[2,4,5],[3,4,5],[2,5]],
                         SYN_CATALOG_PATH, 10, '  ', 2, injection, 406253)
    elif catalog == Catalog.cat:
        return DatasetParameters([[2,3,4],[2,3,8],[2,4,8],[3,4,8],[2,8]],
                         CAT_CATALOG_PATH, 8, "\.|,", 6, injection)
    raise CatalogException()
