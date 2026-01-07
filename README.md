<div align="center">
  
[![CI](https://github.com/sr-murthy/release-art/fca-api/workflows/ci.yml/badge.svg)](https://github.com/release-art/fca-api/actions/workflows/ci.yml)
[![CodeQL](https://github.com/release-art/fca-api/actions/workflows/codeql.yml/badge.svg)](https://github.com/release-art/fca-api/actions/workflows/codeql.yml)
[![License: MPL
2.0](https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![PyPI version](https://img.shields.io/pypi/v/fca-api?logo=python&color=41bb13)](https://pypi.org/project/financial-services-register-api)
![PyPI Downloads](https://static.pepy.tech/badge/fca-api)

</div>

# fca-api

A lightweight async Python client library for the UK [Financial Services Register](https://register.fca.org.uk/s/) [RESTful API](https://register.fca.org.uk/Developer/s/).

The [PyPI package](https://pypi.org/project/fca-api) is currently at version `0.0.0`.

> [!NOTE]
> This is an async fork of the excellent [`financial-services-register-api` package](https://github.com/sr-murthy/financial-services-register-api).

The Financial Services Register, or FS Register, is a **public** database of all firms, individuals, funds, and other entities, that are either currently, or have been previously, authorised and/or regulated by the UK [Financial Conduct Authority (FCA)](https://www.fca.org.uk) and/or the [Prudential Regulation Authority (PRA)](http://bankofengland.co.uk/pra).

> [!NOTE]
> The FS Register API is free to use but accessing it, including via this library, requires [registration](https://register.fca.org.uk/Developer/ShAPI_LoginPage?ec=302&startURL=%2FDeveloper%2Fs%2F#). Registration involves a free sign up with an email, which is used as the API username in requests, and basic personal information. Once registered an API key is available from your registration profile.

See the [Sphinx documentation](https://financial-services-register-api.readthedocs.io/en/latest/) for more details on:

* [understanding the FS Register API](https://financial-services-register-api.readthedocs.io/en/latest/sources/financial-services-register-api.html)
* [usage](https://financial-services-register-api.readthedocs.io/en/latest/sources/usage.html)
* [contributing](https://financial-services-register-api.readthedocs.io/en/latest/sources/contributing.html)
* [API reference](https://financial-services-register-api.readthedocs.io/en/latest/sources/api-reference.html)
