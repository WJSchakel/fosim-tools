"""
A TraceFile represents the content from a trace file produced by FOSIM. It can be filtered, resulting in a TraceFile that
represent a subset of the data.

@author: wjschakel
"""
import re

from pandas.core.frame import DataFrame

from fosim_tools.filter import Filter
import pandas as pd


def _float_converter(value: str) -> float:
    try:
        return float(value)
    except:
        return float('NaN')


def _int_converter(value: str) -> int:
    try:
        return int(value)
    except:
        return -1


_converters = {'t (s)': _float_converter,
          'fromln': _int_converter,
          'tolane': _int_converter,
          'from a': _float_converter,
          'to a': _float_converter,
          'pos (m)': _float_converter,
          'v (m/s)': _float_converter,
          # 'type': str of name
          'id': _int_converter,
          'lane': _int_converter,
          # 'origin': str of name
          # 'dest': str of name
          'tt (s)': _float_converter,
          'dt (s)': _float_converter}


class TraceFile(object):
    """
    A TraceFile represents the content from a trace file produced by FOSIM. It can be filtered, resulting in a TraceFile that 
    represents a subset of the data.
    
    Attributes
    ----------
    _data_frame : DataFrame
        DataFrame that contains the data. Data is transformed in to the right type. What columns are contained depends on the
        original trace file that was loaded.
    
    """

    def __init__(self, filename: str, fos_file: str=None):
        """
        Constructor
        """
        
        # try to find the right format of the file
        if filename:
            with open(filename, 'r') as file:
                header = file.readline(-1);
                if '  ' in header:
                    # Fixed width, delimiter "  ...", decimal separator "."
                    delimiter = r'\s{2,}'
                    decimal = '.'
                elif ';' in header:
                    # Dutch CSV, delimiter ";", decimal separator ","
                    delimiter = ';'
                    decimal = ','
                else:
                    # Pure CSV, delimiter ",", decimal separator "."
                    delimiter = ','
                    decimal = '.'
         
        converters = dict(_converters)
        # sources = dict()
        # sinks = dict()
        types = dict()
        if fos_file != None and len(fos_file):
            with open(fos_file, 'r') as file:
                for line in file:
                    # if line.startswith('source') and not line.startswith('source to sink'):
                    #     index, field_value = self._get_fos_field(line, 4)
                    #     if not sources:
                    #
                    #         def source_converter(value: str):
                    #             return sources[int(value)]
                    #
                    #         converters['origin'] = source_converter
                    #     sources[index] = field_value
                    # elif line.startswith('sink'):
                    #     index, field_value = self._get_fos_field(line, 4)
                    #     if not sinks:
                    #
                    #         def sink_converter(value: str):
                    #             return sinks[int(value)]
                    #
                    #         converters['dest'] = sink_converter
                    #     sinks[index] = field_value
                    if line.startswith('vehicle types') and not line.startswith('vehicle types:'):
                        index, field_value = self._get_fos_field(line, 2)
                        if not types:

                            def type_converter(value: str):
                                return types[int(value)]

                            converters['type'] = type_converter
                        types[index] = field_value
        
        if str != None and len(filename):
            self._data_frame = pd.read_csv(
                filename, delimiter=delimiter, decimal=decimal, header=0, converters=converters, engine='python')
            self._data_frame.dropna(inplace=True)
    
    def filter(self, filt: Filter) -> 'TraceFile':
        """
        Filters the data frame and returns it in a new trace file. The original trace file and data frame are not affected.
        """
        out = TraceFile('')
        out._data_frame = filt.apply(self._data_frame)
        return out
    
    def get_data_frame(self) -> DataFrame:
        """
        Returns the underlying data frame for processing. This is not a safe copy and should not be altered. This data is made
        available only to calculate statistics from the data.
        """
        return self._data_frame
        
    def _get_fos_field(self, line: str, field_number: int):
        """
        Returns a tuple (x, y) from the line "some text  x: 1 2 3 4 y", where y can contain spaces. The field number determines
        the number of spaces that is skipped after the semicolon.
        """
        semi = line.split(':', maxsplit=1)
        index = int(semi[0].split(' ')[-1])
        field_value = re.split(r'\s+', semi[1].strip(), maxsplit=field_number - 1)[-1]
        return (index, field_value)
