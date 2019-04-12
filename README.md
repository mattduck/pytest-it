# pytest-it

Decorate your pytest suite with RSpec-inspired markers `describe`, `context` and
`it`. Then run `pytest --it` to see a plaintext spec of the test structure.

(image)


## Install

Pytest-it is available on PyPi: `pip install pytest-it`.

## Background

Pytest provides a lot of useful features for testing in Python, but we've found
that for some complex systems, it can be hard to clearly communicate the intent
of our tests using the standard `test_module.py::TestClass::test_function`
structure.

This is a problem that can be solved by BDD testing frameworks (eg. [Behave](https://github.com/behave/behave),
[Mamba](https://github.com/nestorsalceda/mamba), [Rspec](http://rspec.info), but it's not always desirable to migrate existing test suites
to a new framework.

There are some pytest plugins that attempt to bridge this gap, by providing
alternative ways to structure the tests (eg. [pytest-describe](https://github.com/ropez/pytest-describe), [pytest-bdd](https://github.com/pytest-dev/pytest-bdd)), or
altering the test report output (eg. [pytest-testdox](https://github.com/renanivo/pytest-testdox), [pytest-pspec](https://github.com/gowtham-sai/pytest-pspec)).

We have taken a similar approach to `pytest-testdox`, by providing pytest
markers that can describe the test output. `pytest-it` supports a few other
features, such as:

- A plaintext test structure that can easily be copied to markdown/org-mode documents.
- Arbitrary nesting of `describe` and `context` markers.
- Supporting the `--collect-only` pytest flag to display test structure.
- Displaying the full path to each test if `-v` is used.
- Neatly (author's opinion) integrating tests in the output if they don't use
  the pytest-it markers.

Although `pytest-it` does not change the behaviour of pytest tests, you may find it
a useful tool for thinking about test structure, and communicating the intention
of both the test code and the system under test.


## Examples
