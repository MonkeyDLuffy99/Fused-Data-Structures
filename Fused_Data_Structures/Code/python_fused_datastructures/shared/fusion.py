from typing import List

import python_jerasure

GALOIS_W = 16


class FusionAccessor:
    def __init__(self, number_of_primaries: int, number_of_faults: int):
        self.__number_of_primaries = number_of_primaries
        self.__number_of_faults = number_of_faults

        self.__rs_array = python_jerasure.calculate_rs_matrix(number_of_primaries, number_of_faults, GALOIS_W)

    def get_updated_code(self, code: int, code_index: int, old_value: int, new_value: int, source_id: int):
        rs_matrix_element = self.__rs_array[code_index *  self.__number_of_primaries + source_id]
        return python_jerasure.calculate_rs_code(
            self.__number_of_primaries,
            self.__number_of_faults,
            GALOIS_W,
            code,
            code_index,
            old_value,
            new_value,
            source_id,
            rs_matrix_element
        )

    def get_recovered_data(self, code_words: List[int], data_words: List[int], erasures: List[int]):
        return python_jerasure.recover_data(
            self.__number_of_primaries,
            self.__number_of_faults,
            GALOIS_W,
            code_words,
            data_words,
            erasures
        )
