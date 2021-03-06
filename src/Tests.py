import unittest
from Shared.Classes.File import File, Cell
from Shared.RuntimeConstants.Runtime_Datasets import TimeFrameColumns
from CLI.UI import Console


class HIPANormalizeToOneTest(unittest.TestCase):

    def setUp(self):
        Console.clear_console()
        self.baseline_means = [1487081.8921335714, 767143.2721442856, 1302190.2019421428, 1113130.6746035714,
                               730617.289225, 727189.5820014286, 936338.2629921428, 836700.6484707142,
                               858294.0763600001, 574486.6794642857, 600562.2055735714, 537954.3985042857,
                               1172866.5845135713, 1485344.8824335714, 622592.5966892857, 322743.4487364285,
                               1320165.877627857, 373303.8651064286, 867237.4988342858, 954028.9279242856,
                               1092703.4592564288, 487314.5808435714, 1171332.1299921428, 521986.17593857145,
                               872894.6925192857, 1177744.4341307143, 733837.2835971429, 649010.5102799999,
                               659096.1782657143, 1615544.4767764283, 736935.1047107143, 630746.2065414286,
                               771146.2786028573, 551325.5801535713, 828896.3158521428, 824434.8758892856,
                               1342635.6592607142, 846031.2291607143, 839358.5765878572, 704612.856605,
                               2194129.325722143, 898577.7755135715, 64155.768782142855]

        self.counts_per_minute_to_one = [2, 1, 0, 0, 1, 2]
        self.spikes_per_minute_per_cell_to_one = [405, 342, 331, 281]
        self.spikes_per_minute_per_cell_to_one_mean = [9.878048780487806, 8.341463414634147, 8.073170731707316,
                                                       6.853658536585366]
        self.interval_high_counts_to_one = [269, 324, 323, 118]

        self.file = File("ExampleData/time_traces.txt")
        self.file.stimulation_time_frames = [372, 696, 1019]
        self.file.threshold = 0.6
        self.file.calculate_baseline_mean()
        self.file.normalize_time_frames_with_to_ones()
        self.file.calculate_time_frame_maximum()
        self.file.calculate_threshold()
        self.file.detect_above_threshold()
        self.file.count_high_intensity_peaks_per_minute()
        self.file.summarize_high_intensity_peaks()
        self.file.split_cells()
        self.file.calculate_high_stimulus_count_per_interval()

    def test_created_cells(self):
        """
        Tests that each cell is created correctly
        """
        self.assertEqual(len(self.file.cells), 41)
        for cell in self.file.cells:
            # Test column count
            self.assertEqual(len(cell.time_frames.columns), 3)
            # Test rows count
            self.assertEqual(len(cell.time_frames), 1400)

            self.assertEqual(cell.time_frames[TimeFrameColumns.TIME_FRAME_VALUE.value].dtype, float)
            # Check maximum minutes
            self.assertEqual(cell.time_frames[TimeFrameColumns.INCLUDING_MINUTE.value].max(), 90)
            self.assertEqual(cell.time_frames[TimeFrameColumns.INCLUDING_MINUTE.value][15], 0.0)
            self.assertEqual(cell.time_frames[TimeFrameColumns.INCLUDING_MINUTE.value][16], 1.0)

    def test_calculate_minutes(self):
        self.assertEqual(self.file.total_detected_minutes, 91)

    def test_cell_baseline_mean(self):
        """
        Checks each baseline mean, with pre calculated values, which are assumed to be correct
        """
        index = 0
        for cell in self.file.cells:
            self.assertEqual(cell.baseline_mean, self.baseline_means[index])
            index += 1

    def test_cell_normalization_to_one(self):
        """
        Tests that the greatest value is 1
        """
        for cell in self.file.cells:
            self.assertEqual(cell.normalized_time_frames[TimeFrameColumns.TIME_FRAME_VALUE.value].max(), 1)
            for index, row in cell.normalized_time_frames.iterrows():
                self.assertLessEqual(int(row[TimeFrameColumns.TIME_FRAME_VALUE.value]), 1)

    def test_cell_threshold_calculation(self):
        """
        Checks if the threshold calculation is working
        """
        for cell in self.file.cells:
            self.assertEqual(cell.threshold, 0.6)

    def test_above_threshold_detection(self):
        """
        Checks if the threshold detection is working
        """
        for cell in self.file.cells:
            for index, row in cell.normalized_time_frames.iterrows():
                if row[TimeFrameColumns.TIME_FRAME_VALUE.value] < 0.6:
                    self.assertEqual(row[TimeFrameColumns.ABOVE_THRESHOLD.value], False)
                else:
                    self.assertEqual(row[TimeFrameColumns.ABOVE_THRESHOLD.value], True)
        pass

    def test_high_intensity_counts(self):
        """
        Tests the first 6 rows of the first cell to check if counting is working as intended
        """
        cell_counts = self.file.cells[0].high_intensity_counts[:6]
        for x in range(6):
            self.assertEqual(cell_counts['Count'][x], self.counts_per_minute_to_one[x])

    def test_summarize_high_intensity_count(self):
        """
        Tests the high intensity count per cell calculations
        """
        for x in range(4):
            self.assertEqual(self.spikes_per_minute_per_cell_to_one[x], self.file.total_spikes_per_minutes[x])
            self.assertEqual(self.spikes_per_minute_per_cell_to_one_mean[x], self.file.total_spikes_per_minute_mean[x])

    def test_interval_comparison(self):
        """
        Tests how often high counts are occurring in each interval
        """
        cell: Cell = self.file.cells[0]
        for x in range(4):
            self.assertEqual(cell.interval_high_intensity_counts['Count'][x], self.interval_high_counts_to_one[x])

    def test_file_output(self):
        pass
        # Write.high_stimulus_counts(self.data)


class HIPANormalizeBaselineTest(unittest.TestCase):

    def setUp(self):
        self.baseline_means = [1487081.8921335714, 767143.2721442856, 1302190.2019421428, 1113130.6746035714,
                               730617.289225, 727189.5820014286, 936338.2629921428, 836700.6484707142,
                               858294.0763600001, 574486.6794642857, 600562.2055735714, 537954.3985042857,
                               1172866.5845135713, 1485344.8824335714, 622592.5966892857, 322743.4487364285,
                               1320165.877627857, 373303.8651064286, 867237.4988342858, 954028.9279242856,
                               1092703.4592564288, 487314.5808435714, 1171332.1299921428, 521986.17593857145,
                               872894.6925192857, 1177744.4341307143, 733837.2835971429, 649010.5102799999,
                               659096.1782657143, 1615544.4767764283, 736935.1047107143, 630746.2065414286,
                               771146.2786028573, 551325.5801535713, 828896.3158521428, 824434.8758892856,
                               1342635.6592607142, 846031.2291607143, 839358.5765878572, 704612.856605,
                               2194129.325722143, 898577.7755135715, 64155.768782142855]

        self.file = File("ExampleData/time_traces.txt")
        self.file.stimulation_time_frames = [372, 969, 1019]
        self.file.threshold = 0.6
        self.file.calculate_baseline_mean()
        # Switch this back to baseline normalization if needed
        self.file.normalize_time_frames_with_to_ones()
        self.file.calculate_time_frame_maximum()
        self.file.calculate_threshold()
        self.file.detect_above_threshold()
        self.file.count_high_intensity_peaks_per_minute()
        self.file.summarize_high_intensity_peaks()
        self.file.split_cells()
        self.file.calculate_high_stimulus_count_per_interval()


if __name__ == '__main__':
    test_classes_to_run = [HIPANormalizeBaselineTest, HIPANormalizeToOneTest]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)
