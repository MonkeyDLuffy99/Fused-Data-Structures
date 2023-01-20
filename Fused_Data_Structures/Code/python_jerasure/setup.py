from distutils.core import setup, Extension

setup(
    name="python_jerasure",
    version="1.0",
    ext_modules=[
        Extension("python_jerasure", extra_compile_args=['-w'], sources=[
            "bind.c",
            "python_jerasure.c",
            "libjerasure/galois.c",
            "libjerasure/jerasure.c",
            "libjerasure/reed_sol.c"
        ])
    ]
)
