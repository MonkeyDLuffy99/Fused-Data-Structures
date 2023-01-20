#ifndef __PYREED_H__
#define __PYREED_H__

#include <Python.h>

PyObject* recover_data(PyObject*, PyObject*);
PyObject* calculate_rs_code(PyObject*, PyObject*);
PyObject* calculate_rs_matrix(PyObject*, PyObject*);

#endif