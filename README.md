# fca-api

[![CI](https://github.com/release-art/fca-api/actions/workflows/ci.yml/badge.svg)](https://github.com/release-art/fca-api/actions/workflows/ci.yml)
[![CodeQL](https://github.com/release-art/fca-api/actions/workflows/codeql.yml/badge.svg)](https://github.com/release-art/fca-api/actions/workflows/codeql.yml)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![PyPI version](https://img.shields.io/pypi/v/fca-api?logo=python&color=41bb13)](https://pypi.org/project/fca-api)

A lightweight async Python client library for the UK Financial Conduct Authority's [Financial Services Register](https://register.fca.org.uk/s/) [RESTful API](https://register.fca.org.uk/Developer/s/).

## Overview

This package provides a simple, asynchronous interface to interact with the FCA's Financial Services Register API, allowing you to query information about:

- Financial firms and their details
- Individual professionals in the financial services industry
- Investment funds and their characteristics
- Regulatory permissions and restrictions
- Disciplinary actions and enforcement history

> **Note:** This is an async fork of the [`financial-services-register-api`](https://github.com/sr-murthy/financial-services-register-api) package, optimized for modern async/await patterns.

## Requirements

- Python 3.11 or higher
- httpx library for async HTTP requests

## Installation

Install from PyPI using pip:

```bash
pip install fca-api
```
<!-- 
## Quick Start

Here's a simple example to get you started:

```python
import asyncio
from fca_api import FinancialServicesRegisterApiClient

async def main():
    async with FinancialServicesRegisterApiClient() as client:
        # Search for firms
        firms = await client.search_firms(name="Barclays")
        print(f"Found {len(firms)} firms matching 'Barclays'")
        
        # Get detailed information about a specific firm
        if firms:
            firm_details = await client.get_firm(firms[0]['id'])
            print(f"Firm name: {firm_details['name']}")

if __name__ == "__main__":
    asyncio.run(main())
``` -->

## Key Features

- **Asynchronous Operations**: Built with async/await for efficient concurrent requests
- **Type Hints**: Full type annotation support for better development experience  
- **Comprehensive Coverage**: Access to all major FCA Register endpoints
- **Easy to Use**: Intuitive API design with sensible defaults
- **Lightweight**: Minimal dependencies with httpx as the only requirement

## Documentation

For detailed API reference, usage examples, and advanced configuration options, visit the [complete documentation](https://docs.release.art/fca-api/).

## Contributing

Contributions are welcome! Please see [contributing guidelines](https://docs.release.art/fca-api/sources/contributing.html) on how to contribute to this project.

## License

This project is licensed under the Mozilla Public License 2.0. See the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please:

1. Check the [documentation](https://docs.release.art/fca-api/)
2. Search existing [GitHub issues](https://github.com/release-art/fca-api/issues)
3. Create a new issue if your problem hasn't been addressed