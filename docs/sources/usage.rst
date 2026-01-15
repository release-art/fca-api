=====
Usage
=====

The library exposes two layers of API clients:

* a **high-level async client** (:py:class:`fca_api.async_api.Client`) that returns typed Pydantic models and handles pagination; and
* a **low-level raw client** (:py:class:`fca_api.raw_api.RawClient`) that maps closely to the underlying HTTP endpoints and returns thin response wrappers.

In most cases you should use :py:class:`fca_api.async_api.Client`. The raw client is intended for advanced use cases where full control over the HTTP layer or raw payloads is required.

High-level async client
=======================

The recommended entry point is :py:class:`fca_api.async_api.Client`. It is designed to be used as an async context manager and requires your FCA API username (signup email) and API key:

.. code:: python

   import asyncio
   from fca_api.async_api import Client


   async def main() -> None:
      async with Client(
         credentials=("<signup email>", "<API key>"),
      ) as client:
         firms = await client.search_frn("revolution")
         async for firm in firms:
            print(f"{firm.name} (FRN: {firm.frn})")


   if __name__ == "__main__":
      asyncio.run(main())

The high-level client returns rich Pydantic models defined in :mod:`fca_api.types` and uses :class:`fca_api.types.pagination.MultipageList` for all paginated results. See :doc:`../sources/api-reference` for the full API surface.

Low-level raw client
====================

For situations where you want to work directly with the JSON payloads returned by the FCA API, you can use :py:class:`fca_api.raw_api.RawClient`. This client exposes one method per HTTP endpoint and returns :class:`fca_api.raw_api.FcaApiResponse` objects, which wrap an underlying :class:`httpx.Response`.

Each :class:`~fca_api.raw_api.FcaApiResponse` has convenience properties for the four API-specific fields commonly present in responses:

* :py:attr:`~fca_api.raw_api.FcaApiResponse.fca_api_status` - FCA API status code for the request.
* :py:attr:`~fca_api.raw_api.FcaApiResponse.message` - human-readable status message.
* :py:attr:`~fca_api.raw_api.FcaApiResponse.data` - the response payload (usually a mapping or list of mappings).
* :py:attr:`~fca_api.raw_api.FcaApiResponse.result_info` - pagination metadata when the endpoint is paginated.

Example (raw client)::

   import asyncio
   from fca_api.raw_api import RawClient


   async def main() -> None:
      async with RawClient(
         credentials=("<signup email>", "<API key>"),
      ) as client:
         res = await client.get_firm("805574")
         print(res.fca_api_status, res.message)
         print(res.data)


   if __name__ == "__main__":
      asyncio.run(main())

.. _usage.common-search:

Common Search
=============

The common search HTTP endpoint can be accessed via the low-level :py:meth:`~fca_api.raw_api.RawClient.common_search()` method to make generic queries for firms, individuals, or funds. It requires two arguments, a resource name (or name substring) to search for, and a resource type which must be one of the following strings: ``"firm"``, ``"individual"``, or ``"fund"``. The method then calls the common search endpoint with a URL-encoded string of the form below:

.. code:: bash

   q=resource_name&type=resource_type

where ``q`` is a parameter whose value should be the name (or name substring) of a resource (firm, individual, or fund), and ``type`` is a parameter whose value should be one of ``'firm'``, ``'individual'``, ``'fund'``.

Some examples of common search are given below for Barclays Bank Plc.

.. code:: python

   >>> res = await client.common_search('barclays bank', 'firm')
   >>> res
   <Response [200]>
   >>> res.data
   [{'URL': 'https://register.fca.org.uk/services/V0.1/Firm/759676',
     'Status': 'Authorised',
     'Reference Number': '759676',
     'Type of business or Individual': 'Firm',
     'Name': 'Barclays Bank UK PLC (Postcode: E14 5HP)'},
    ...
   {'URL': 'https://register.fca.org.uk/services/V0.1/Firm/122702',
    'Status': 'Authorised',
    'Reference Number': '122702',
    'Type of business or Individual': 'Firm',
    'Name': 'Barclays Bank Plc (Postcode: E14 5HP)'}]
   >>> res.status
   'FSR-API-04-01-00'
   >>> res.message
   'Ok. Search successful'
   >>> res.resultinfo
   {'page': '1', 'per_page': '20', 'total_count': '9'}

Here are some further examples of common search for firms, individuals and funds.

.. code:: python

   >>> (await client.common_search('revolut bank', 'firm')).data
   [{'URL': 'https://register.fca.org.uk/services/V0.1/Firm/833790',
     'Status': 'No longer authorised',
     'Reference Number': '833790',
     'Type of business or Individual': 'Firm',
     'Name': 'Revolut Bank UAB'}]
   #
   >>> (await client.common_search('mark carney', 'individual')).data
   [{'URL': 'https://register.fca.org.uk/services/V0.1/Individuals/MXC29012',
     'Status': 'Active',
     'Reference Number': 'MXC29012',
     'Type of business or Individual': 'Individual',
     'Name': 'Mark Carney'}]
   #
   >>> (await client.common_search('jupiter asia pacific income', 'fund')).data
   [{'URL': 'https://register.fca.org.uk/services/V0.1/CIS/635641',
     'Status': 'Recognised',
     'Reference Number': '635641',
     'Type of business or Individual': 'Collective investment scheme',
     'Name': 'Jupiter Asia Pacific Income Fund (IRL)'}]

The response data as stored in the :py:attr:`~fca_api.api.FinancialServicesRegisterApiResponse.data` property might be non-empty or empty depending on whether the combination of query and resource type is valid, e.g.:

.. code:: python

   >>> (await client.common_search('natwest', 'individual')).data
   # Null

.. _usage.regulated-markets:

Regulated Markets
-----------------

The high-level async client implements a `regulated markets <https://www.handbook.fca.org.uk/handbook/glossary/G978.html?date=2007-01-20>`_ search helper via :py:meth:`fca_api.async_api.Client.get_regulated_markets`:

.. code:: python

   >>> markets = await client.get_regulated_markets()
   >>> len(markets)
   5

   [{'Name': 'The London Metal Exchange',
     'TradingName': '',
     'Type of business or Individual': 'Exchange - RM',
     'Reference Number': '',
     'Status': '',
     'FirmURL': 'https://register.fca.org.uk/services/V0.1/Firm/'},
    {'Name': 'ICE Futures Europe',
     'TradingName': '',
     'Type of business or Individual': 'Exchange - RM',
     'Reference Number': '',
     'Status': '',
     'FirmURL': 'https://register.fca.org.uk/services/V0.1/Firm/'},
    {'Name': 'London Stock Exchange',
     'TradingName': '',
     'Type of business or Individual': 'Exchange - RM',
     'Reference Number': '',
     'Status': '',
     'FirmURL': 'https://register.fca.org.uk/services/V0.1/Firm/'},
    {'Name': 'Aquis Stock Exchange Limited',
     'TradingName': 'ICAP Securities & Derivatives Exchange Limited',
     'Type of business or Individual': 'Exchange - RM',
     'Reference Number': '',
     'Status': '',
     'FirmURL': 'https://register.fca.org.uk/services/V0.1/Firm/'},
    {'Name': 'Cboe Europe Equities Regulated Market',
     'TradingName': '',
     'Type of business or Individual': 'Exchange - RM',
     'Reference Number': '',
     'Status': '',
     'FirmURL': 'https://register.fca.org.uk/services/V0.1/Firm/'}]

.. _usage.searching-ref-numbers:

Searching for FRNs, IRNs and PRNs
=================================

Generally, firm reference numbers (FRN), individual reference numbers (IRN), and product reference numbers (PRN), may not be known in advance. These can be found via the following client search methods, which return strings in the case of unique matches, or a JSON arrays of matching records if there are non-unique matches:

* :py:meth:`fca_api.async_api.Client.search_frn()` - case-insensitive search for FRNs.
* :py:meth:`fca_api.async_api.Client.search_irn()` - case-insensitive search for IRNs.
* :py:meth:`fca_api.async_api.Client.search_prn()` - case-insensitive search for PRNs.

These high-level methods return :class:`fca_api.types.pagination.MultipageList` instances containing typed search result models from :mod:`fca_api.types.search`. On network or API errors they raise exceptions from :mod:`fca_api.exc` (for example :class:`fca_api.exc.FcaRequestError`).

FRNs, IRNs, and PRNs are associated with unique firms, individuals, and funds, respectively, in the Register, whether current or past. The more precise the name substring the more likely is an exact, unique result. Some examples are given below for each type of search, starting with FRNs:

.. code:: python

   >>> await client.search_frn('hiscox insurance company limited')
   '113849'

Imprecise or inadequality specified names in the search can produce non-unique matches, in which all matching records are returned in a JSON array, for example:

.. code:: python

   >>> await client.search_frn('hiscox')
   [{'URL': 'https://register.fca.org.uk/services/V0.1/Firm/812274',
     'Status': 'No longer authorised',
     'Reference Number': '812274',
     'Type of business or Individual': 'Firm',
     'Name': 'HISCOX ASSURE'},
    ...
    ...
    {'URL': 'https://register.fca.org.uk/services/V0.1/Firm/732312',
     'Status': 'Authorised',
     'Reference Number': '732312',
     'Type of business or Individual': 'Firm',
     'Name': 'Hiscox MGA Ltd (Postcode: EC2N 4BQ)'}
   ]

Searches for non-existent firms will trigger an exception from :mod:`fca_api.exc` indicating that no data was found in the Register for the given name:

.. code:: python

   >>> await client.search_frn('a nonexistent firm')
   Traceback (most recent call last):
   ...
   fca_api.api.FinancialServicesRegisterApiResponseException: No data found in FSR API response. Please check the search parameters and try again.

A few examples are given below of IRN searches.

.. code:: python

   >>> await client.search_irn('mark carney')
   'MXC29012'
   #
   >>> await client.search_irn('mark c')
   [{'URL': 'https://register.fca.org.uk/services/V0.1/Individuals/MWC01033',
     'Status': 'Active',
     'Reference Number': 'MWC01033',
     'Type of business or Individual': 'Individual',
     'Name': 'Mark William Cowell'},
    ...
    ...
    {'URL': 'https://register.fca.org.uk/services/V0.1/Individuals/RMG01106',
     'Status': 'Active',
     'Reference Number': 'RMG01106',
     'Type of business or Individual': 'Individual',
     'Name': 'Richard Mark Greenfield'}]
   #
   >>> await client.search_irn('a nonexistent individual')
   Traceback (most recent call last):
   ...
   fca_api.api.FinancialServicesRegisterApiResponseException: No data found in FSR API response. Please check the search parameters and try again.

A few examples are given below of PRN searches.

.. code:: python

   >>> await client.search_prn('jupiter asia pacific income')
   '635641'
   #
   >>> await client.search_prn('jupiter asia')
   [{'URL': 'https://register.fca.org.uk/services/V0.1/CIS/718428',
     'Status': 'Authorised',
     'Reference Number': '718428',
     'Type of business or Individual': 'Collective investment scheme',
     'Name': 'Jupiter Asian Income Fund'},
    ...
    ...
    {'URL': 'https://register.fca.org.uk/services/V0.1/CIS/140620',
     'Status': 'Terminated',
     'Reference Number': '140620',
     'Type of business or Individual': 'Collective investment scheme',
     'Name': 'JUPITER ASIAN FUND'}]
   #
   >>> client.search_prn('a nonexistent fund')
   Traceback (most recent call last):
   ...
   fca_api.api.FinancialServicesRegisterApiResponseException: No data found in FSR API response. Please check the search parameters and try again.

.. _usage.firms:

Firms
=====

Client methods for firm-specific requests, the associated API endpoints, resource parameters, and high-level return types are summarised in the table below.

.. list-table::
   :align: left
   :widths: 75 75 20 20 20
   :header-rows: 1

    * - Method
       - API Endpoint
       - Request Method
       - Resource Parameters
       - High-level return type
    * - :py:meth:`fca_api.async_api.Client.get_firm()`
     - ``/V0.1/Firm/{FRN}``
     - ``GET``
     - FRN (str)
       - :class:`fca_api.types.firm.FirmDetails`
    * - :py:meth:`fca_api.async_api.Client.get_firm_addresses()`
     - ``/V0.1/Firm/{FRN}/Address``
     - ``GET``
     - FRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.firm.FirmAddress`
    * - :py:meth:`fca_api.async_api.Client.get_firm_appointed_representatives()`
     - ``/V0.1/Firm/{FRN}/AR``
     - ``GET``
     - FRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.firm.FirmAppointedRepresentative`
    * - :py:meth:`fca_api.async_api.Client.get_firm_controlled_functions()`
     - ``/V0.1/Firm/{FRN}/CF``
     - ``GET``
     - FRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.firm.FirmControlledFunction`
    * - :py:meth:`fca_api.async_api.Client.get_firm_disciplinary_history()`
     - ``/V0.1/Firm/{FRN}/DisciplinaryHistory``
     - ``GET``
     - FRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.firm.FirmDisciplinaryHistory`
    * - :py:meth:`fca_api.async_api.Client.get_firm_exclusions()`
     - ``/V0.1/Firm/{FRN}/Exclusions``
     - ``GET``
     - FRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.firm.FirmExclusion`
    * - :py:meth:`fca_api.async_api.Client.get_firm_individuals()`
     - ``/V0.1/Firm/{FRN}/Individuals``
     - ``GET``
     - FRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.firm.FirmIndividual`
    * - :py:meth:`fca_api.async_api.Client.get_firm_names()`
     - ``/V0.1/Firm/{FRN}/Names``
     - ``GET``
     - FRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.firm.FirmNameAlias`
    * - :py:meth:`fca_api.async_api.Client.get_firm_passports()`
     - ``/V0.1/Firm/{FRN}/Passports``
     - ``GET``
     - FRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.firm.FirmPassport`
    * - :py:meth:`fca_api.async_api.Client.get_firm_passport_permissions()`
     - ``/V0.1/Firm/{FRN}/Passports/{Country}/Permission``
     - ``GET``
     - FRN (str), Country (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.firm.FirmPassportPermission`
    * - :py:meth:`fca_api.async_api.Client.get_firm_permissions()`
     - ``/V0.1/Firm/{FRN}/Permissions``
     - ``GET``
     - FRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.firm.FirmPermission`
    * - :py:meth:`fca_api.async_api.Client.get_firm_regulators()`
     - ``/V0.1/Firm/{FRN}/Regulators``
     - ``GET``
     - FRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.firm.FirmRegulator`
    * - :py:meth:`fca_api.async_api.Client.get_firm_requirements()`
     - ``/V0.1/Firm/{FRN}/Requirements``
     - ``GET``
     - FRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.firm.FirmRequirement`
    * - :py:meth:`fca_api.async_api.Client.get_firm_requirement_investment_types()`
     - ``/V0.1/Firm/{FRN}/Requirements/{ReqRef}/InvestmentTypes``
     - ``GET``
     - FRN (str), Requirement Reference (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.firm.FirmRequirementInvestmentType`
    * - :py:meth:`fca_api.async_api.Client.get_firm_waivers()`
     - ``/V0.1/Firm/{FRN}/Waiver``
     - ``GET``
     - FRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.firm.FirmWaiver`

Examples are given below for each request type for Barclays Bank Plc (FRN #122702).

.. grid:: 1

   .. grid-item-card:: **Barclays Bank (FRN #122702)** - firm details

      .. code:: python

         >>> client.get_firm('122702').data
         [{'Name': 'https://register.fca.org.uk/services/V0.1/Firm/122702/Names',
           'Individuals': 'https://register.fca.org.uk/services/V0.1/Firm/122702/Individuals',
           'Requirements': 'https://register.fca.org.uk/services/V0.1/Firm/122702/Requirements',
           'Permission': 'https://register.fca.org.uk/services/V0.1/Firm/122702/Permissions',
           'Passport': 'https://register.fca.org.uk/services/V0.1/Firm/122702/Passports',
           'Regulators': 'https://register.fca.org.uk/services/V0.1/Firm/122702/Regulators',
           'Appointed Representative': 'https://register.fca.org.uk/services/V0.1/Firm/122702/AR',
           'Address': 'https://register.fca.org.uk/services/V0.1/Firm/122702/Address',
           'Waivers': 'https://register.fca.org.uk/services/V0.1/Firm/122702/Waivers',
           'Exclusions': 'https://register.fca.org.uk/services/V0.1/Firm/122702/Exclusions',
           'DisciplinaryHistory': 'https://register.fca.org.uk/services/V0.1/Firm/122702/DisciplinaryHistory',
           'System Timestamp': '30/11/2024 20:34',
           'Exceptional Info Details': [],
           'Status Effective Date': '01/12/2001',
           'E-Money Agent Status': '',
           'PSD / EMD Effective Date': '',
           'Client Money Permission': 'Control but not hold client money',
           'Sub Status Effective from': '',
           'Sub-Status': '',
           'Mutual Society Number': '',
           'Companies House Number': '01026167',
           'MLRs Status Effective Date': '',
           'MLRs Status': '',
           'E-Money Agent Effective Date': '',
           'PSD Agent Effective date': '',
           'PSD Agent Status': '',
           'PSD / EMD Status': '',
           'Status': 'Authorised',
           'Business Type': 'Regulated',
           'Organisation Name': 'Barclays Bank Plc',
           'FRN': '122702'}]

.. grid:: 1

   .. grid-item-card:: **Barclays Bank (FRN #122702)** - addresses

      .. code:: python

         >>> client.get_firm_addresses('122702').data
         [{'URL': 'https://register.fca.org.uk/services/V0.1/Firm/122702/Address?Type=PPOB',
           'Website Address': 'www.barclays.com',
           'Phone Number': '+442071161000',
           'Country': 'UNITED KINGDOM',
           'Postcode': 'E14 5HP',
           'County': '',
           'Town': 'London',
           'Address Line 4': '',
           'Address LIne 3': '',
           'Address Line 2': '',
           'Address Line 1': 'One Churchill Place',
           'Address Type': 'Principal Place of Business'},
          {'URL': 'https://register.fca.org.uk/services/V0.1/Firm/122702/Address?Type=Complaint',
           'Website Address': '',
           'Phone Number': '+4403301595858',
           'Country': 'UNITED KINGDOM',
           'Postcode': 'NN4 7SG',
           'County': 'Northamptonshire',
           'Town': 'Northampton',
           'Address Line 4': '',
           'Address LIne 3': '',
           'Address Line 2': '',
           'Address Line 1': '1234 Pavilion Drive',
           'Individual': '',
           'Address Type': 'Complaints Contact'}]

.. grid:: 1

   .. grid-item-card:: **Barclays Bank (FRN #122702)** - controlled functions

      .. code:: python

         >>> client.get_firm_controlled_functions('122702').data
         [{'Current': {'(6707)SMF4 Chief Risk': {'Suspension / Restriction End Date': '',
             'Suspension / Restriction Start Date': '',
             'Restriction': '',
             'Effective Date': '16/02/2023',
             'Individual Name': 'Bevan Cowie',
             'Name': 'SMF4 Chief Risk',
             'URL': 'https://register.fca.org.uk/services/V0.1/Individuals/BXC00280'},
         ...
            '(22338)[PRA CF] Significant risk taker or Material risk taker': {'End Date': '30/06/2020',
             'Suspension / Restriction End Date': '',
             'Suspension / Restriction Start Date': '',
             'Restriction': '',
             'Effective Date': '07/03/2016',
             'Individual Name': 'Lynne Atkin',
             'Name': '[PRA CF] Significant risk taker or Material risk taker',
             'URL': 'https://register.fca.org.uk/services/V0.1/Individuals/LAA01049'}}}]

.. grid:: 1

   .. grid-item-card:: **Barclays Bank (FRN #122702)** - disciplinary history

      .. code:: python

         >>> client.get_firm_disciplinary_history('122702').data
         [{'TypeofDescription': "On 19 August 2009, the FSA imposed a penalty on Barclays Bank plc and Barclays Capital Securities Limited (Barclays) of £2,450,000 (discounted from £3,500,000 for early settlement) in respect of breaches of SUP 17 of the FSA Handbook and breaches of Principles 2 and 3 of the FSA's Principles for Businesses which occurred between 1 October 2006 and 31 October 2008. The breach of SUP 17 related to Barclays failure to submit accurate transaction reports as required in respect of an estimated 57.5 million transactions. Barclays breached Principle 2 by failing to conduct its business with due skill, care and diligence in failing to respond sufficiently to opportunities to review the adequacy of its transaction reporting systems. Barclays breached Principle 3 by failing to take reasonable care to organise and control its affairs responsibly and effectively, with adequate risk management systems, to meet the requirements to submit accurate transaction reports to the FSA",
           'TypeofAction': 'Fines',
           'EnforcementType': 'FSMA',
           'ActionEffectiveFrom': '08/09/2009'},
          ...
          {'TypeofDescription': "On 23 September 2022, the FCA decided to impose a financial penalty on Barclays Bank Plc. The reason for this action is because Barclays Bank Plc failed to comply with Listing Rule 1.3.3 in October 2008. This matter has been referred by Barclays Bank Plc to the Upper Tribunal. The FCA’s findings and proposed action are therefore provisional and will not take effect pending determination of this matter by the Upper Tribunal. The FCA’s decision was issued on 23 September 2022 and a copy of the Decision Notice is displayed on the FCA's web site here: https://www.fca.org.uk/publication/decision-notices/barclays-bank-plc-dn-2022.pdf \xa0",
           'TypeofAction': 'Fines',
           'EnforcementType': 'FSMA',
           'ActionEffectiveFrom': '23/09/2022'}]

.. grid:: 1

   .. grid-item-card:: **Barclays Bank (FRN #122702)** - exclusions

      .. code:: python

         >>> client.get_firm_exclusions('122702').data
         [{'PSD2_Exclusion_Type': 'Limited Network Exclusion',
           'Particular_Exclusion_relied_upon': '2(k)(iii) - may be used only to acquire a very limited range of goods or services',
           'Description_of_services': 'Precision pay Virtual Prepaid - DVLA Service'}]
         #
         >>> client.get_firm_individuals('122702').data
         [{'Status': 'Approved by regulator',
           'URL': 'https://register.fca.org.uk/services/V0.1/Individuals/BXC00280',
           'IRN': 'BXC00280',
           'Name': 'Bevan Cowie'},
         ...
          {'Status': 'Approved by regulator',
           'URL': 'https://register.fca.org.uk/services/V0.1/Individuals/TXW00011',
           'IRN': 'TXW00011',
           'Name': 'Herbert Wright'}]

.. grid:: 1

   .. grid-item-card:: **Barclays Bank (FRN #122702)** - alternative or secondary trading names

      .. code:: python

         >>> client.get_firm_names('122702').data
         [{'Current Names': [{'Effective From': '17/05/2013',
             'Status': 'Trading',
             'Name': 'Barclays Bank'},
         ...
            {'Effective To': '25/01/2010',
             'Effective From': '08/03/2004',
             'Status': 'Trading',
             'Name': 'Banca Woolwich'}]}]

.. grid:: 1

   .. grid-item-card:: **Barclays Bank (FRN #122702)** - passports

      .. code:: python

         >>> client.get_firm_passports('122702').data
         [{'Passports': [{'PassportDirection': 'Passporting Out',
             'Permissions': 'https://register.fca.org.uk/services/V0.1/Firm/122702/Passports/GIBRALTAR/Permission',
             'Country': 'GIBRALTAR'}]}]

.. grid:: 1

   .. grid-item-card:: **Barclays Bank (FRN #122702)** - firm country-specific passport permissions and activities

      .. code:: python

         >>> client.get_firm_passport_permissions('122702', 'Gibraltar').data
         [{'Permissions': [{'Name': '*  - additional MiFID services and activities subject to mutual recognition under the BCD',
             'InvestmentTypes': []},
         ...
          {'Permissions': [{'Name': 'Insurance Distribution or Reinsurance Distribution',
             'InvestmentTypes': []}],
           'PassportType': 'Service',
           'PassportDirection': 'Passporting Out',
           'Directive': 'Insurance Distribution',
           'Country': 'GIBRALTAR'}]

.. grid:: 1

   .. grid-item-card:: **Barclays Bank (FRN #122702)** - permissions and activities

      .. code:: python

         >>> client.get_firm_permissions('122702').data
         {'Debt Adjusting': [{'Limitation': ['This permission is limited to debt adjusting with no debt management activity']}],
          'Credit Broking': [{'Limitation Not Found': ['Valid limitation not present']}],
          ...
           'Accepting Deposits': [{'Customer Type': ['All']},
           {'Investment Type': ['Deposit']}]}

.. grid:: 1

   .. grid-item-card:: **Barclays Bank (FRN #122702)** - regulators

      .. code:: python

         >>> client.get_firm_regulators('122702').data
         [{'Termination Date': '',
           'Effective Date': '01/04/2013',
           'Regulator Name': 'Financial Conduct Authority'},
         ...
          {'Termination Date': '30/11/2001',
           'Effective Date': '25/11/1993',
           'Regulator Name': 'Securities and Futures Authority'}]

.. grid:: 1

   .. grid-item-card:: **Barclays Bank (FRN #122702)** - requirements

      .. code:: python

         >>> client.get_firm_requirements('122702').data
         [{'Effective Date': '23/03/2020',
           'Written Notice - Market Risk Consolidation': 'REQUIREMENTS RELEVANT TO THE MARKET RISK CONSOLIDATION PERMISSION THAT THE FIRM HAS SOUGHT AND THE PRA IMPOSES UNDER SECTION 55M (5) OF THE ACT 1.This Market Risk Consolidation Permission applies to an institution or undertaking listed in Table 1 only for as long as it remains part of the Barclays Group. The firm must notify the PRA promptly if any of those institutions or undertakings ceases to be part of the Barclays Group. 2.The firm must, no later than 23 business days after the end of each quarter, ending March, June, September and December submit, in respect of that quarter, a report to the PRA highlighting the capital impact of market risk consolidation for each of the institutions listed in Table 1. 3.The firm must: 1.ensure that any existing legal agreements or arrangements necessary for fulfilment of the conditions of Article 325(2) of the CRR as between any of the institutions in Table 1 are maintained; and 2.notify the PRA of any variation in the terms of such agreements, or of any change in the relevant legal or regulatory framework of which it becomes aware and which may have an impact on the ability of any of the institutions listed in Table 1 to meet the conditions of Article 325(2) of the CRR. THE MARKET RISK CONSOLIDATION PERMISSION Legal Entities 1.The Market Risk Consolidation Permission means that the firm may use positions in an institution or undertaking listed in Table 1 to offset positions in another institution or undertaking listed therein only for the purposes of calculating net positions and own funds requirements in accordance with Title IV of the CRR on a consolidated basis. Table 1 Institutions and Location of undertaking: Barclays Bank PLC (BBPLC) - UK Barclays Capital Securities Limited (BCSL) UK Barclays Bank Ireland - Ireland',
           'Requirement Reference': 'OR-0170047',
           'Financial Promotions Requirement': 'FALSE'},
          ...
          {'Effective Date': '01/10/2024',
           'Financial Promotion for other unauthorised clients': 'This firm can: (1) approve its own financial promotions as well as those of members of its wider group and, in certain circumstances, those of its appointed representatives; and (2) approve financial promotions for other unauthorised persons for the following types of investment:',
           'Requirement Reference': 'OR-0262545',
           'Financial Promotions Requirement': 'TRUE',
           'Financial Promotions Investment Types': 'https://register.fca.org.uk/services/V0.1/Firm/122702/Requirements/OR-0262545/InvestmentTypes'}]

.. grid:: 1

   .. grid-item-card:: **Barclays Bank (FRN #122702)** - investment types associated with a specific firm requirement

      .. code:: python

         >>> client.get_firm_requirement_investment_types('122702', 'OR-0262545').data
         [{'Investment Type Name': 'Certificates representing certain securities'},
          {'Investment Type Name': 'Debentures'},
          {'Investment Type Name': 'Government and public security'},
          {'Investment Type Name': 'Listed shares'},
          {'Investment Type Name': 'Warrants'}]

.. grid:: 1

   .. grid-item-card:: **Barclays Bank (FRN #122702)** - waivers

      .. code:: python

         >>> client.get_firm_waivers('122702').data
         [{'Waivers_Discretions_URL': 'https://register.fca.org.uk/servlet/servlet.FileDownload?file=00P0X00001YXBw1UAH',
           'Waivers_Discretions': 'A4823494P.pdf',
           'Rule_ArticleNo': ['CRR Ar.313']},
         ...
          {'Waivers_Discretions_URL': 'https://register.fca.org.uk/servlet/servlet.FileDownload?file=00P4G00002oJPciUAG',
           'Waivers_Discretions': 'A00003642P.pdf',
           'Rule_ArticleNo': ['Perm & Wav - CRR Ru 2.2']}]

.. _usage.individuals:

Individuals
===========

Client methods for individual-specific requests, the associated API endpoints, resource parameters, and high-level return types are summarised in the table below.

.. list-table::
   :align: left
   :widths: 75 75 20 20 20
   :header-rows: 1

    * - Method
       - API Endpoint
       - Request Method
       - Parameters
       - High-level return type
    * - :py:meth:`fca_api.async_api.Client.get_individual()`
     - ``/V0.1/Individuals/{IRN}``
     - ``GET``
     - IRN (str)
       - :class:`fca_api.types.individual.IndividualDetails`
    * - :py:meth:`fca_api.async_api.Client.get_individual_controlled_functions()`
     - ``/V0.1/Individuals/{IRN}/CF``
     - ``GET``
     - IRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.individual.IndividualControlledFunction`
    * - :py:meth:`fca_api.async_api.Client.get_individual_disciplinary_history()`
     - ``/V0.1/Individuals/{IRN}/DisciplinaryHistory``
     - ``GET``
     - IRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.individual.IndividualDisciplinaryHistory`

Some examples are given below for each type of request for a specific, existing individual, Mark Carney (IRN #MXC29012).

.. grid:: 1

   .. grid-item-card:: **Mark Carney (IRN #MXC29012)** - individual details

      .. code:: python

         >>> client.get_individual('MXC29012').data
         [{'Details': {'Disciplinary History': 'https://register.fca.org.uk/services/V0.1/Individuals/MXC29012/DisciplinaryHistory',
            'Current roles & activities': 'https://register.fca.org.uk/services/V0.1/Individuals/MXC29012/CF',
            'IRN': 'MXC29012',
            'Commonly Used Name': 'Mark',
            'Status': 'Certified / assessed by firm',
            'Full Name': 'Mark Carney'},
           'Workplace Location 1': {'Firm Name': 'TSB Bank plc',
            'Location 1': 'Liverpool'}}]

.. grid:: 1

   .. grid-item-card:: **Mark Carney (IRN #MXC29012)** - controlled functions

      .. code:: python

         >>> client.get_individual_controlled_functions('MXC29012').data
         [{'Previous': {'(5)Appointed representative dealing with clients for which they require qualification': {'Customer Engagement Method': 'Face To Face; Telephone; Online',
             'End Date': '05/04/2022',
             'Suspension / Restriction End Date': '',
             'Suspension / Restriction Start Date': '',
             'Restriction': '',
             'Effective Date': '23/10/2020',
             'Firm Name': 'HL Partnership Limited',
             'Name': 'Appointed representative dealing with clients for which they require qualification',
             'URL': 'https://register.fca.org.uk/services/V0.1/Firm/303397'},
         ...
            '(1)The London Institute of Banking and Finance (LIBF) - formerly known as IFS': {'Customer Engagement Method': '',
             'Suspension / Restriction End Date': '',
             'Suspension / Restriction Start Date': '',
             'Restriction': '',
             'Effective Date': '',
             'Firm Name': 'Echo Finance Limited',
             'Name': 'The London Institute of Banking and Finance (LIBF) - formerly known as IFS',
             'URL': 'https://register.fca.org.uk/services/V0.1/Firm/570073'}}}]


.. grid:: 1

   .. grid-item-card:: **Mark Carney (IRN #MXC29012)** - disciplinary history

      .. code:: python

         >>> client.get_individual_disciplinary_history('MXC29012').data
         # None

.. _usage.funds:

Funds
=====

Client methods for fund-specific requests, the associated API endpoints, resource parameters, and high-level return types are summarised in the table below.

.. list-table::
   :align: left
   :widths: 75 75 20 20 20
   :header-rows: 1

    * - Method
       - API Endpoint
       - Request Method
       - Parameters
       - High-level return type
    * - :py:meth:`fca_api.async_api.Client.get_fund()`
     - ``/V0.1/CIS/{PRN}``
     - ``GET``
     - PRN (str)
       - :class:`fca_api.types.products.ProductDetails`
    * - :py:meth:`fca_api.async_api.Client.get_fund_names()`
     - ``/V0.1/CIS/{PRN}/Names``
     - ``GET``
     - PRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.products.ProductNameAlias`
    * - :py:meth:`fca_api.async_api.Client.get_fund_subfunds()`
     - ``/V0.1/CIS/{PRN}/Subfund``
     - ``GET``
     - PRN (str)
       - :class:`fca_api.types.pagination.MultipageList` of :class:`fca_api.types.products.SubFundDetails`

Some examples are given below for each type of request for a specific, existing fund, abrdn Multi-Asset Fund (PRN #185045).

.. grid:: 1

   .. grid-item-card:: **abrdn Multi-Asset Fund (PRN #185045)** - fund details

      .. code:: python

         >>> client.get_fund('185045').data
         [{'Sub-funds': 'https://register.fca.org.uk/services/V0.1/CIS/185045/Subfund',
           'Other Name': 'https://register.fca.org.uk/services/V0.1/CIS/185045/Names',
           'CIS Depositary': 'https://register.fca.org.uk/services/V0.1/Firm/805574',
           'CIS Depositary Name': 'Citibank UK Limited',
           'Operator Name': 'abrdn Fund Managers Limited',
           'Operator': 'https://register.fca.org.uk/services/V0.1/Firm/121803',
           'MMF Term Type': '',
           'MMF NAV Type': '',
           'Effective Date': '23/12/1997',
           'Scheme Type': 'UCITS (COLL)',
           'Product Type': 'ICVC',
           'ICVC Registration No': 'SI000001',
           'Status': 'Authorised'}]

.. grid:: 1

   .. grid-item-card:: **abrdn Multi-Asset Fund (PRN #185045)** - alternative or secondary names

      .. code:: python

         >>> client.get_fund_names('185045').data
         [{'Effective To': '22/08/2019',
           'Effective From': '23/12/1997',
           'Product Other Name': 'ABERDEEN INVESTMENT FUNDS ICVC'},
          {'Effective To': '01/08/2022',
           'Effective From': '23/12/1997',
           'Product Other Name': 'Aberdeen Standard OEIC I'}]

.. grid:: 1

   .. grid-item-card:: **abrdn Multi-Asset Fund (PRN #185045)** - subfunds

      .. code:: python

         >>> client.get_fund_subfunds('185045').data
         [{'URL': 'https://register.fca.org.uk/services/apexrest/V0.1/CIS/185045',
           'Sub-Fund Type': 'Other',
           'Name': 'abrdn (AAM) UK Smaller Companies Fund'},
         ...
          {'URL': 'https://register.fca.org.uk/services/apexrest/V0.1/CIS/185045',
           'Sub-Fund Type': 'Other',
           'Name': 'abrdn Strategic Bond Fund'}]
