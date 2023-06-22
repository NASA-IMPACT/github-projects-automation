"""Sphinx configuration."""
project = "Github Projects Automation"
author = "Ashish Acharya"
copyright = "2023, Ashish Acharya"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
