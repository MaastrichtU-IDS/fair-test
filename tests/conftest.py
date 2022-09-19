def pytest_addoption(parser):
    parser.addoption("--metric", action="store", default=None)
