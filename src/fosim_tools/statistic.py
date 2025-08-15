"""
Statistics on trace file data.

@author: wjschakel
"""
from abc import abstractmethod, ABC

from fosim_tools.filter import Area
from fosim_tools.trace_file import TraceFile


class Statistic(ABC):
    """
    Super class of all statistic values.
    """

    def __init__(self, params):
        """
        Constructor.
        """
    
    @abstractmethod
    def get_label(self) -> str:
        """
        Returns the label of the statistic, for example for in a table.
        """
        pass
    
    @abstractmethod
    def get_unit(self) -> str:
        """
        Returns the preferred unit of the statistic, for example for in a table.
        """
        pass
    
    @abstractmethod
    def get_unit_si(self) -> str:
        """
        Returns the SI unit of the statistic, for example for in a table.
        """
        pass
    
    @abstractmethod
    def get(self, trace_file: TraceFile) -> float:
        """
        Returns the value of the statistic in preferred unit.
        """
        pass
    
    @abstractmethod
    def get_si(self, trace_file: TraceFile) -> float:
        """
        Returns the value of the statistic in SI unit.
        """
        pass
    
    def _check_column(self, column: str, trace_file: TraceFile):
        """
        Raises an error if a column with given name is not in the trace file.
        """
        if not column in trace_file.get_data_frame():
            raise ValueError('Column ' + column + ' is not in the provided trace file.')


class Total(Statistic):
    """
    Intermediate class for statistics that are a summation of the difference of each vehicles's maximum and minimum values of a
    column defined by a sub class. This class caches the value for a given trace file, as these statistics are reused in others.
    
    Attributes:
    -----------
    _column : str
        Column name.
    
    _value : float
        Cached value.
    
    _trace_file : TraceFile
        Trace file of cached value.
    """
    
    def __init__(self, column: str):
        self._column = column
        self._value = None
        self._trace_file = None
    
    @abstractmethod
    def get_label(self) -> str:
        pass
    
    def get_si(self, trace_file: TraceFile) -> float:
        self._check_column(self._column, trace_file)
        self._check_column('id', trace_file)
        if trace_file is not self._trace_file:
            ids = trace_file.get_data_frame()['id'].unique()
            value = 0.0
            for vehicle_id in ids:
                id_data = trace_file.get_data_frame()[trace_file.get_data_frame()['id'] == vehicle_id]
                value = value + id_data[self._column].max() - id_data[self._column].min()
            self._value = value
            self._trace_file = trace_file
        return self._value


class TotalTimeSpent(Total):
    """
    Summation of each vehicle's time in 'Vehicle Samples' trace file.
    """
    
    def __init__(self):
        super().__init__('t (s)')
        
    def get_label(self) -> str:
        return 'Total time spent'
    
    def get_unit(self) -> str:
        return 'h'
    
    def get_unit_si(self) -> str:
        return 's'
    
    def get(self, trace_file: TraceFile) -> float:
        return self.get_si(trace_file) / 3600.0


class TotalDistanceTraveled(Total):
    """
    Summation of each vehicle's distance in 'Vehicle Samples' trace file.
    """
    
    def __init__(self):
        super().__init__('pos (m)')
    
    def get_label(self) -> str:
        return 'Total distance traveled'
    
    def get_unit(self) -> str:
        return 'km'
    
    def get_unit_si(self) -> str:
        return 'm'
    
    def get(self, trace_file: TraceFile) -> float:
        return self.get_si(trace_file) / 1000.0

        
class MeanSpeed(Statistic):
    """
    Total distance traveled divided by the total time spent in 'Vehicle Samples' trace file.
    
    Attributes:
    -----------
    _total_time_spent : TotalTimeSpent
        Total time spent statistic.
    
    _total_distance_traveled : TotalDistanceTraveled
        Total distance traveled statistic.
    """
    
    def __init__(self, total_time_spent: TotalTimeSpent, total_distance_traveled: TotalDistanceTraveled):
        self._total_time_spent = total_time_spent
        self._total_distance_traveled = total_distance_traveled
    
    def get_label(self) -> str:
        return 'Mean speed'
    
    def get_unit(self) -> str:
        return 'km/h'
    
    def get_unit_si(self) -> str:
        return 'm/s'
    
    def get(self, trace_file: TraceFile) -> float:
        return self.get_si(trace_file) * 3.6
    
    def get_si(self, trace_file: TraceFile) -> float:
        return self._total_distance_traveled.get_si(trace_file) / self._total_time_spent.get_si(trace_file)


class PerArea(Statistic):
    """
    Intermediate class for statistics that divide another statistic, defined by a sub class, by a space-time area.
    
    Attributes:
    -----------
    _statistic : Statistic
        Statistice per area.
    
    _area : Area
        Area.
    """
    
    def __init__(self, statistic: Statistic, area: Area):
        self._statistic = statistic
        self._area = area
    
    @abstractmethod
    def get_label(self) -> str:
        pass
    
    def get_si(self, trace_file: TraceFile) -> float:
        return self._statistic.get_si(trace_file) / self._area.get_area()


class Density(PerArea):
    """
    Density as total time spent divided by area in 'Vehicle Samples' trace file.
    """
    
    def __init__(self, total_time_spent: TotalTimeSpent, area: Area):
        super().__init__(total_time_spent, area)
        
    def get_label(self) -> str:
        return 'Density'
    
    def get_unit(self) -> str:
        return '/km'
    
    def get_unit_si(self) -> str:
        return '/m'

    def get(self, trace_file: TraceFile) -> float:
        return self.get_si(trace_file) * 1000.0


class Flow(PerArea):
    """
    Flow as total distance traveled divided by area in 'Vehicle Samples' trace file.
    """
    
    def __init__(self, total_distance_traveled: TotalDistanceTraveled, area: Area):
        super().__init__(total_distance_traveled, area)
    
    def get_label(self) -> str:
        return 'Flow'
    
    def get_unit(self) -> str:
        return '/h'
    
    def get_unit_si(self) -> str:
        return '/s'
    
    def get(self, trace_file: TraceFile) -> float:
        return self.get_si(trace_file) * 3600.0


class NumberOfLaneChanges(Statistic):
    """
    Number of lane changes from 'Lane Changes' trace file.
    """
    
    def __init__(self):
        pass
    
    def get_label(self) -> str:
        return 'Number of lane changes'
    
    def get_unit(self) -> str:
        return '-'
    
    def get_unit_si(self) -> str:
        return '-'
    
    def get(self, trace_file: TraceFile) -> float:
        self._check_column('fromln', trace_file)
        self._check_column('tolane', trace_file)
        return len(trace_file.get_data_frame().index)
    
    def get_si(self, trace_file: TraceFile) -> float:
        return self.get(trace_file)
