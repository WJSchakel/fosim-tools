'''
Tests reading and filtering a trace file.

@author: wjschakel
'''
import unittest

from fosim_tools import statistic
from fosim_tools.filter import InSet, Range, Area
from fosim_tools.statistic import TotalTimeSpent, TotalDistanceTraveled, MeanSpeed, Density, Flow, NumberOfLaneChanges
from fosim_tools.table import Table
from fosim_tools.trace_file import TraceFile


class Test(unittest.TestCase):

    def test_name(self):
        
        fos_file = '../resources/Trace.fos'
        filename = '../resources/Inv_21.trc'
        detections = TraceFile(filename, fos_file=fos_file)
        filtered_detections = detections.filter(InSet('type', {'1', '2'})).filter(Range('t (s)', 15.0, 18.0))
        print(detections._data_frame.head(5))
        print(filtered_detections._data_frame.head(5))
        
        # Note: values are nonsense because .ddt is not a vehicles samples file.
        # (It does however contain columns 'id', 'pos (m)' and 't (s)', which we need to technically test statistics.)
        filename = '../resources/Inv_21.ddt'
        area = Area(600.0, 1800.0, 1000.0, 2000.0)
        travel_time = TraceFile(filename, fos_file=fos_file)
        travel_time_filtered = travel_time.filter(area)
        
        tts = TotalTimeSpent()
        tdt = TotalDistanceTraveled()
        statistics = [tts, tdt, MeanSpeed(tts, tdt), Density(tts, area), Flow(tdt, area)]
        
        trace_file = travel_time
        for _ in range(0, 2):
            for statistic in statistics:
                print(statistic.get_label() + ": " + str(statistic.get(trace_file)) + " [" + statistic.get_unit() + "]")
            trace_file = travel_time_filtered
            
        filename = '../resources/Inv_21.lct'
        lane_changes = TraceFile(filename, fos_file=fos_file)
        statistic = NumberOfLaneChanges()
        print(statistic.get_label() + ": " + str(statistic.get(lane_changes)) + " [" + statistic.get_unit() + "]")
        
        statistics.append(statistic)
        trace_files = [travel_time, travel_time, travel_time, travel_time, travel_time, lane_changes]
        table = Table(statistics, trace_files)
        print(table.as_data_frame().head(3))
        table.print_to_console(decimal_places=4)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_name']
    unittest.main()
