"""
Doctest the module from the project root using

export API_USERNAME=<API username> && \
    export API_KEY=<API key> && \
    PYTHONPATH=src python -m doctest -v src/financial_services_register_api/api.py && \
    unset API_USERNAME && unset API_KEY

"""

import doctest

doctest.testmod()
