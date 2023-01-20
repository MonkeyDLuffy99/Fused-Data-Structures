#include "python_jerasure.h"

char recover_docs[] = "Recover a list of data from Reed-Solomon codes";
char gen_rs_matrix_docs[] = "Generate Reed-Solomon matrix for the specified number of primary and backup nodes";
char calculate_rs_code_docs[] = "Calculate a Reed-Solomon code for the provided value";

PyMethodDef python_jerasure_functions[] = {
    { "recover_data", (PyCFunction)recover_data, METH_VARARGS, recover_docs },
    { "calculate_rs_code", (PyCFunction)calculate_rs_code, METH_VARARGS, calculate_rs_code_docs },
    { "calculate_rs_matrix", (PyCFunction)calculate_rs_matrix, METH_VARARGS, gen_rs_matrix_docs },
    { NULL }
};

char python_jerasure_docs[] = "Python adapter for Jerasure library";

PyModuleDef python_jerasure_module = {
    PyModuleDef_HEAD_INIT,
    "python_jerasure",
    python_jerasure_docs,
    -1,
    python_jerasure_functions,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC PyInit_python_jerasure(void) {
    return PyModule_Create(&python_jerasure_module);
}
