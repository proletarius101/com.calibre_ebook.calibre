#!/usr/bin/env python3
"""Do something useful."""
import argparse
import json
import os
import pathlib
import sys
import re


__dir__ = pathlib.Path(__file__).parent.absolute()
__version__ = "0.1.0"

EXCLUDED_PACKAGES = ["PyQt6_sip",
                     "PyQt6",
                     "PyQt6_WebEngine",
                     "parser",
                     "builder",
                     "dateutil"]


def is_for_linux(source):
    return source.get("os") == None or source.get("os").find("linux") >= 0


def is_pypi_source(source):
    return source.get("unix") and source.get("unix").get("urls") == ["pypi"]


def get_package_name(source):
    pattern = re.compile("(\w+)-[\d.]+\.(tar.gz|tar.bz2|zip)")
    matched = re.search(pattern, source["unix"]["filename"])
    if matched:
        return matched[1]


def get_package_version(source):
    pattern = re.compile("\w+-([\d.]+)\.(tar.gz|tar.bz2|zip)")
    matched = re.search(pattern, source["unix"]["filename"])
    if matched:
        return matched[1]


def convert_bypy_source_to_pip_requirement(bypy_source):
    name = get_package_name(bypy_source)
    version = get_package_version(bypy_source)
    return f"{name}=={version}"


def is_included(source):
    package_name = get_package_name(source)
    return not (package_name in EXCLUDED_PACKAGES)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('bypy_sources_path', action='store',
                        help="sources.json at bypy/sources.json of Calibre's repository")
    parser.add_argument('output', action='store', default='requirements.txt',
                        help='Specify output file name')
    args = parser.parse_args()

    bypy_sources_file = os.path.expanduser(args.bypy_sources_path)
    with open(bypy_sources_file, "rb") as f:
        sources = json.load(f)

    sources = filter(is_for_linux, sources)
    sources = filter(is_pypi_source, sources)
    sources = filter(is_included, sources)

    pip_requirements = map(convert_bypy_source_to_pip_requirement, sources)

    requirements_file = os.path.expanduser(args.output)
    with open(requirements_file, "w") as f:
        f.write("\n".join(pip_requirements))

    return 0


if __name__ == "__main__":
    sys.exit(main())
