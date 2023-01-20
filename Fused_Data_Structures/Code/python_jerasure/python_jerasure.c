#include <Python.h>

#include "./libjerasure/jerasure.h"
#include "./libjerasure/reed_sol.h"

PyObject* calculate_rs_matrix(PyObject* self, PyObject* args)
{
    int num_primary_structures, num_backup_structures, w, i;

    if (!PyArg_ParseTuple(args, "iii", &num_primary_structures, &num_backup_structures, &w)) {
        printf("could not parse all arguments in calculate_rs_matrix\n");
        return NULL;
    }

    // Require RS matrix from jerasure...
    int* matrixRaw = reed_sol_vandermonde_coding_matrix(num_primary_structures, num_backup_structures, w);

    // Convert result to Python list...
    PyObject* matrixList = PyList_New(num_primary_structures * num_backup_structures);
    for (i = 0; i < num_primary_structures * num_backup_structures; i++) {
        PyList_SetItem(matrixList, i, PyLong_FromLong(matrixRaw[i]));
    }

    return matrixList;
}

PyObject* calculate_rs_code(PyObject* self, PyObject* args)
{
    int num_primary_structures, num_backup_structures, w, code, code_index, old_value, new_value, position, mat_element;

    if (!PyArg_ParseTuple(args, "iiiiiiiii", &num_primary_structures, &num_backup_structures, &w, &code, &code_index, &old_value,
            &new_value, &position, &mat_element)) {
        printf("could not parse all arguments in calculate_rs_code\n");
        return NULL;
    }

    long code_long = (long)code;
    long old_value_long = (long)old_value;
    long new_value_long = (long)new_value;

    char* code_char = (char*)malloc(sizeof(char) * sizeof(long));
    char* old_value_char = (char*)malloc(sizeof(char) * sizeof(long));
    char* new_value_char = (char*)malloc(sizeof(char) * sizeof(long));

    // Convert the code/old value/new value into a long char*, as required by jerasure..
    memcpy(code_char, &code_long, sizeof(long));
    memcpy(old_value_char, &old_value_long, sizeof(long));
    memcpy(new_value_char, &new_value_long, sizeof(long));

    jerasure_update_single_code(num_primary_structures, num_backup_structures, w, mat_element, code_char, code_index,
        sizeof(long), old_value_char, new_value_char, position);

    return PyLong_FromLong(*(long*)code_char);
}

PyObject* recover_data(PyObject* self, PyObject* args)
{
    int num_primary_structures, num_backup_structures, w, i;

    PyObject* dataRaw = NULL;
    PyObject* codesRaw = NULL;
    PyObject* erasuresRaw = NULL;

    if (!PyArg_ParseTuple(
            args, "iiiOOO", &num_primary_structures, &num_backup_structures, &w, &codesRaw, &dataRaw, &erasuresRaw)) {
        printf("could not parse all arguments in recover\n");
        return NULL;
    }

    PyObject* dataIter = PyObject_GetIter(dataRaw);
    PyObject* codesIter = PyObject_GetIter(codesRaw);
    PyObject* erasuresIter = PyObject_GetIter(erasuresRaw);

    // Ensure all expected inputs are lists...
    if (!codesIter || !dataIter || !erasuresIter) {
        printf("could not build iterators for all input lists in recover\n");
        return NULL;
    }

    // Allocate memory for input lists...
    char** data = (char**)malloc(num_primary_structures * sizeof(char*));
    char** codes = (char**)malloc(num_backup_structures * sizeof(char*));
    int* erasures = (int*)malloc((num_backup_structures + 1) * sizeof(int));

    // Read data list...
    for (i = 0; i < num_primary_structures; i++) {
        PyObject* next = PyIter_Next(dataIter);

        if (!next) {
            printf("len(data) < num_primary_structures in recover\n");
            return NULL;
        }
        if (!PyLong_Check(next)) {
            printf("encountered non-integer data list member in recover\n");
            return NULL;
        }

        long value = PyLong_AsLong(next);

        // Cast value into a long char*, as required by jerasure
        data[i] = (char*)malloc(sizeof(long) * sizeof(char));
        memcpy(data[i], &value, sizeof(long));
    }

    // Read codes list...
    for (i = 0; i < num_backup_structures; i++) {
        PyObject* next = PyIter_Next(codesIter);

        if (!next) {
            printf("len(codes) < num_backup_structures in recover\n");
            return NULL;
        }
        if (!PyLong_Check(next)) {
            printf("encountered non-integer codes list member in recover\n");
            return NULL;
        }

        long value = PyLong_AsLong(next);

        // Cast value into a long char*, as required by jerasure
        codes[i] = (char*)malloc(sizeof(long) * sizeof(char));
        memcpy(codes[i], &value, sizeof(long));
    }

    // Read erasures list...
    for (i = 0; i < num_backup_structures + 1; i++) {
        PyObject* next = PyIter_Next(erasuresIter);

        if (!next) {
            printf("len(erasures) < num_backup_structures + 1 in recover\n");
            return NULL;
        }
        if (!PyLong_Check(next)) {
            printf("encountered non-integer erasures list member in recover\n");
            return NULL;
        }

        int value = PyLong_AsLong(next);
        erasures[i] = value;
    }

    // Calculate RS matrix and decode...
    int* matrix = reed_sol_vandermonde_coding_matrix(num_primary_structures, num_backup_structures, w);
    jerasure_matrix_decode(num_primary_structures, num_backup_structures, w, matrix, 1, erasures, data, codes, sizeof(long));

    // Build list of recovered data...
    PyObject* recoveredList = PyList_New(num_primary_structures);
    for (i = 0; i < num_primary_structures; i++) {
        PyObject* value = PyLong_FromLong(*(long*)data[i]);
        PyList_SetItem(recoveredList, i, value);
    }

    return recoveredList;
}
