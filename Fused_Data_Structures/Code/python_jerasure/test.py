import python_jerasure
import unittest


class TestJerasureMethods(unittest.TestCase):
    def test_calculate_rs_matrix_valid(self):
        # Test for 1 primary, 1 backup
        matrix = python_jerasure.calculate_rs_matrix(1, 1, 16)
        self.assertEqual(matrix, [1])

        # Test for 3 primaries, 5 backups
        matrix = python_jerasure.calculate_rs_matrix(3, 5, 16)
        self.assertEqual(matrix, [1, 1, 1, 1, 24578, 40964, 1,
                         34820, 48562, 1, 48563, 34821, 1, 61447, 61446])

    def test_calculate_rs_matrix_invalid(self):
        # Test invalid number of arguments
        self.assertRaises(TypeError, python_jerasure.calculate_rs_matrix, 0)

        # Test invalid argument types
        self.assertRaises(TypeError, python_jerasure.calculate_rs_matrix, 'a', 'b', 'c')

    def test_calculate_rs_code_valid(self):
        # Test calculation of code "111"
        code = python_jerasure.calculate_rs_code(3, 3, 16, 41169, 1, 222, 0, 1, 24578)
        self.assertEqual(code, 111)

        # Test calculation of code "333"
        code = python_jerasure.calculate_rs_code(3, 3, 16, 0, 0, 0, 333, 1, 1)
        self.assertEqual(code, 333)

    def test_calculate_rs_code_invalid(self):
        # Test invalid number of arguments
        self.assertRaises(TypeError, python_jerasure.calculate_rs_code, 0)

        # Test invalid argument types
        self.assertRaises(TypeError, python_jerasure.calculate_rs_code, 'a', 'b', 'c', 'e', 'f', 'g', 'h', 'i', 'j')

    def test_recover_data_valid(self):
        # Test recovery of sequence [789, 0, 0]
        codes = [789, 789, 789]
        data = [0, 0, 0]
        erasures = [0, 1, 2, -1]

        restored = python_jerasure.recover_data(3, 3, 16, codes, data, erasures)
        self.assertEqual(restored, [123, 456, 789])

    def test_recover_data_invalid(self):
        # Test invalid number of arguments
        self.assertRaises(TypeError, python_jerasure.recover_data, 0)

        # Test invalid argument types
        self.assertRaises(TypeError, python_jerasure.recover_data, 'a', 'b', 'c', 'e', 'f', 'g')


if __name__ == '__main__':
    unittest.main()
