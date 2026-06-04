[doc("Typecheck all code")]
check:
    mypy --incremental --strict --pretty src tests

[default]
[doc("Run tests")]
test: check
    PYTHONPATH="src" coverage run --branch -m unittest discover -s tests

[doc("Show test coverage")]
cover: test
    coverage report -m
