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

[no-exit-message]
[doc("Run cli module")]
run *args:
    @PYTHONPATH="src" python -m simple_bank.cli {{ args }}
