import nox


nox.options.sessions = ["tests"]


@nox.session(python=["3.8", "3.7"])
def tests(session):
    args = session.posargs or ["--cov=pytailor", "tests"]
    session.run("poetry", "install", external=True)
    session.run("pytest", *args)


@nox.session(python="3.8")
def black(session):
    args = session.posargs or ["src", "tests", "examples", "test_scripts", "noxfile.py"]
    session.install("black")
    session.run("black", *args)
