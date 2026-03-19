from setuptools import setup, Extension
from Cython.Build import cythonize

ext_modules = [
    Extension(
        name="integrate_cy",
        sources=["integrate_cy.pyx"],
    )
]

setup(
    name="integrate_cy",
    ext_modules=cythonize(ext_modules, language_level=3),
)
