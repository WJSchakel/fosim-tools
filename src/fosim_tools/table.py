"""
Table to display multiple statistics on console or to get multiple statistics as a data frame.

@author: wjschakel
"""
from pandas.core.frame import DataFrame

from fosim_tools.statistic import Statistic
from fosim_tools.trace_file import TraceFile


class Table(object):
    """
    Table to display multiple statistics on console or to get multiple statistics as a data frame.
    
    Attributes:
    -----------
    _data_frame : DataFrame
        Data frame of label, value and unit per statistic.
    """

    def __init__(self, statistics: list[Statistic], trace_files: list[TraceFile]):
        """
        Constructor.
        """
        if len(statistics) is not len(trace_files):
            raise ValueError('Statistics list and trace file list are not of equal length.')
        labels = []
        values = []
        units = []
        for i in range(len(statistics)):
            labels.append(statistics[i].get_label())
            values.append(statistics[i].get(trace_files[i]))
            units.append(statistics[i].get_unit())
        # first column name is an empty string such that the table prints nicely
        self._data_frame = DataFrame({'': labels, 'Value': values, 'Unit': units})
    
    def print_to_console(self, decimal_places: int=2):
        """
        Prints the table to console.
        """
        print(self._data_frame.to_string(
            formatters={
                '': '{{:<{}s}}'.format(self._data_frame[''].str.len().max()).format, # left-align labels by appending spaces
                'Value': '{{:.{}f}}'.format(decimal_places).format # decimal places in values
            }, index=False))
    
    def as_data_frame(self) -> DataFrame:
        """
        Returns the table as a data frame. This is a safe copy of an internal data frame.
        """
        return self._data_frame.copy()
