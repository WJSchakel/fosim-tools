"""
Filters on data from a TraceFile.

@author: wjschakel
"""
from abc import ABC, abstractmethod

from pandas import DataFrame


class Filter(ABC):
    """
    Defines a filter on trace file data.
    
    Attributes:
    -----------
    _column : str
        Name of the column in TraceFile to filter.
    """

    def __init__(self, column: str):
        """
        Constructor.
        """
        self._column = column
    
    @abstractmethod
    def apply(self, data_frame: DataFrame) -> DataFrame:
        """
        Applies the filter.
        """
        pass

class Range(Filter):
    """
    Defines a range of value to keep.
    
    Attributes
    ----------
    _min : float
        Minimum value.
    
    _max : float
        Maximum value.
    
    _min_inclusive : bool
        Include minimum value (default True).
    
    _max_inclusive : bool
        Include maximum value (default False).
    """
    
    def __init__(self, column: str, minimum: float, maximum: float, min_inclusive: bool=True, max_inclusive: bool=False):
        super().__init__(column)
        if minimum > maximum:
            raise ValueError('Minimum is larger than maximum in range filter.')
        self._min = minimum
        self._max = maximum
        self._min_inclusive = min_inclusive
        self._max_inclusive = max_inclusive 
    
    def apply(self, data_frame: DataFrame) -> DataFrame:
        if self._min_inclusive:
            min_bool = data_frame[self._column] >= self._min
        else:
            min_bool = data_frame[self._column] > self._min
        
        if self._max_inclusive:
            max_bool = data_frame[self._column] <= self._max
        else:
            max_bool = data_frame[self._column] < self._max
            
        return data_frame[min_bool & max_bool]

class Area(Filter):
    
    def __init__(self, min_t: float, max_t: float, min_pos: float, max_pos: float):
        self._area = (max_t - min_t) * (max_pos - min_pos)
        self._t_filter = Range('t (s)', min_t, max_t, True, True)
        self._pos_filter = Range('pos (m)', min_pos, max_pos, True, True)
    
    def get_area(self) -> float:
        """
        Returns the area of the space-time box: (max_t - min_t) * (max_pos - min_pos).
        """
        return self._area
    
    def apply(self, data_frame: DataFrame) -> DataFrame:
        return self._pos_filter.apply(self._t_filter.apply(data_frame))

class InSet(Filter):
    """
    Filters a TraceFile by maintaining all values in a column that are in a given set.
    
    Attributes:
    -----------
    _values : set
        Set of string values to keep.
    """
    
    def __init__(self, column: str, values: set[str]):
        super().__init__(column)
        self._values = values
        
    def apply(self, data_frame: DataFrame) -> DataFrame:
        return data_frame[data_frame[self._column].isin(self._values)]