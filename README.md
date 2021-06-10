<!--
  THIS FILE IS EXCLUSIVELY MAINTAINED IN THE NAMESPACE ROOT PACKAGE. CHANGES HAVE TO BE DONE THERE.
-->
# lockname portion of ae namespace package

[![GitLabPipeline](https://img.shields.io/gitlab/pipeline/ae-group/ae_lockname/master?logo=python)](
    https://gitlab.com/ae-group/ae_lockname)
[![PyPIVersion](https://img.shields.io/pypi/v/ae_lockname)](
    https://pypi.org/project/ae-lockname/#history)

>The portions (modules and sub-packages) of the Application Environment for Python are within
the `ae` namespace and are providing helper methods and classes to develop
full-featured applications with Python.

[![Coverage](https://ae-group.gitlab.io/ae_lockname/coverage.svg)](
    https://ae-group.gitlab.io/ae_lockname/coverage/ae_lockname_py.html)
[![MyPyPrecision](https://ae-group.gitlab.io/ae_lockname/mypy.svg)](
    https://ae-group.gitlab.io/ae_lockname/lineprecision.txt)
[![PyLintScore](https://ae-group.gitlab.io/ae_lockname/pylint.svg)](
    https://ae-group.gitlab.io/ae_lockname/pylint.log)

[![PyPIImplementation](https://img.shields.io/pypi/implementation/ae_lockname)](
    https://pypi.org/project/ae-lockname/)
[![PyPIPyVersions](https://img.shields.io/pypi/pyversions/ae_lockname)](
    https://pypi.org/project/ae-lockname/)
[![PyPIWheel](https://img.shields.io/pypi/wheel/ae_lockname)](
    https://pypi.org/project/ae-lockname/)
[![PyPIFormat](https://img.shields.io/pypi/format/ae_lockname)](
    https://pypi.org/project/ae-lockname/)
[![PyPIStatus](https://img.shields.io/pypi/status/ae_lockname)](
    https://libraries.io/pypi/ae-lockname)
[![PyPIDownloads](https://img.shields.io/pypi/dm/ae_lockname)](
    https://pypi.org/project/ae-lockname/#files)


## installation


execute the following command to use the ae.lockname module in your
application. it will install ae.lockname into your python (virtual) environment:
 
```shell script
pip install ae-lockname
```

if you instead want to contribute to this portion then first fork
[the ae_lockname repository at GitLab](https://gitlab.com/ae-group/ae_lockname "ae.lockname code repository"),
then pull it to your machine and finally execute the following command in the root folder
of this repository (ae_lockname):

```shell script
pip install -e .[dev]
```

the last command will install this module portion into your virtual environment, along with
the tools you need to develop and run tests or to extend the portion documentation.
to contribute only to the unit tests or to the documentation of this portion replace
the setup extras key `dev` in the above command with `tests` or `docs` respectively.


## namespace portion documentation

more info on the features and usage of this portion are available at
[ReadTheDocs](https://ae.readthedocs.io/en/latest/_autosummary/ae.lockname.html#module-ae.lockname
"ae_lockname documentation").

<!-- common files version 0.2.77 deployed version 0.2.8 (with 0.2.77)
     to https://gitlab.com/ae-group as ae_lockname module as well as
     to https://ae-group.gitlab.io with CI check results as well as
     to https://pypi.org/project/ae-lockname as namespace portion ae-lockname.
-->
