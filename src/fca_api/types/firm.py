import datetime
from typing import Annotated, Literal, Optional

import pydantic

from . import base, field_parsers


class FirmDetails(base.Base):
    frn: Annotated[str, pydantic.Field(alias="frn")]
    name: Annotated[
        str,
        pydantic.Field(
            description="Name of the company.",
            validation_alias=pydantic.AliasChoices("organisation name", "name"),
            serialization_alias="name",
        ),
    ]
    status: Annotated[
        str,
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The firm's status.",
        ),
    ]
    type: Annotated[
        str,
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The type of the resource.",
            validation_alias=pydantic.AliasChoices("business type", "type"),
            serialization_alias="type",
        ),
    ]
    companies_house_number: Annotated[
        str,
        pydantic.Field(
            description="The firm's Companies House number.",
            validation_alias=pydantic.AliasChoices("companies house number", "companies_house_number"),
            serialization_alias="companies_house_number",
        ),
    ]
    client_money_permission: Annotated[
        str,
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="Indicates whether the firm has client money permission.",
            validation_alias=pydantic.AliasChoices("client money permission", "client_money_permission"),
            serialization_alias="client_money_permission",
        ),
    ]
    timestamp: Annotated[
        datetime.datetime,
        pydantic.Field(
            description="The timestamp when the data was retrieved from the FCA register.",
            validation_alias=pydantic.AliasChoices("system timestamp", "timestamp"),
            serialization_alias="timestamp",
        ),
        field_parsers.ParseFcaDate,
    ]
    status_effective_date: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="The effective date when the status was active from.",
            validation_alias=pydantic.AliasChoices("status effective date", "status_effective_date"),
            serialization_alias="status_effective_date",
        ),
        field_parsers.ParseFcaDate,
    ]
    sub_status: Annotated[
        Optional[str],
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="Related sub-status to the firm's status.",
            validation_alias=pydantic.AliasChoices("sub-status", "sub_status"),
            serialization_alias="sub_status",
        ),
    ]
    sub_status_effective_from: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="Date from which the sub-status was effective.",
            validation_alias=pydantic.AliasChoices("sub status effective from", "sub_status_effective_from"),
            serialization_alias="sub_status_effective_from",
        ),
        field_parsers.ParseFcaDate,
    ]
    mutual_society_number: Annotated[
        Optional[str],
        pydantic.Field(
            description="Registered number as a Mutual Society.",
            validation_alias=pydantic.AliasChoices("mutual society number", "mutual_society_number"),
            serialization_alias="mutual_society_number",
        ),
    ]
    mlrs_status: Annotated[
        Optional[str],
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="Status under the Money Laundering Regulations.",
            validation_alias=pydantic.AliasChoices("mlrs status", "mlrs_status"),
            serialization_alias="mlrs_status",
        ),
    ]
    mlrs_status_effective_date: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="Date from which the MLRs Status was effective.",
            validation_alias=pydantic.AliasChoices("mlrs status effective date", "mlrs_status_effective_date"),
            serialization_alias="mlrs_status_effective_date",
        ),
        field_parsers.ParseFcaDate,
    ]
    e_money_agent_status: Annotated[
        Optional[str],
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="Status as an E-Money Agent.",
            validation_alias=pydantic.AliasChoices("e-money agent status", "e_money_agent_status"),
            serialization_alias="e_money_agent_status",
        ),
    ]
    e_money_agent_effective_date: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="Date from which the E-Money Agent Status was effective.",
            validation_alias=pydantic.AliasChoices("e-money agent effective date", "e_money_agent_effective_date"),
            serialization_alias="e_money_agent_effective_date",
        ),
        field_parsers.ParseFcaDate,
    ]
    psd_emd_status: Annotated[
        Optional[str],
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="Status under the Payment Services Directive or the Electronic Money Directive.",
            validation_alias=pydantic.AliasChoices("psd / emd status", "psd_emd_status"),
            serialization_alias="psd_emd_status",
        ),
    ]
    psd_emd_effective_date: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="Date from which the PSD/EMD Status was effective.",
            validation_alias=pydantic.AliasChoices("psd / emd effective date", "psd_emd_effective_date"),
            serialization_alias="psd_emd_effective_date",
        ),
        field_parsers.ParseFcaDate,
    ]
    psd_agent_status: Annotated[
        Optional[str],
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="Status as a PSD Agent.",
            validation_alias=pydantic.AliasChoices("psd agent status", "psd_agent_status"),
            serialization_alias="psd_agent_status",
        ),
    ]
    psd_agent_effective_date: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="Date from which the PSD Agent Status was effective.",
            validation_alias=pydantic.AliasChoices("psd agent effective date", "psd_agent_effective_date"),
            serialization_alias="psd_agent_effective_date",
        ),
        field_parsers.ParseFcaDate,
    ]
    exceptional_info_details: Annotated[
        list,
        pydantic.Field(
            description="Additional information about the notices associated with the firm.",
            validation_alias=pydantic.AliasChoices("exceptional info details", "exceptional_info_details"),
            serialization_alias="exceptional_info_details",
        ),
    ]

    # URLs
    names_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="URL to fetch other trading name/brand name for the firm.",
            validation_alias=pydantic.AliasChoices("name", "names_url"),
            serialization_alias="names_url",
        ),
    ]
    individuals_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="URL to fetch the individuals associated with the firm.",
            validation_alias=pydantic.AliasChoices("individuals", "individuals_url"),
            serialization_alias="individuals_url",
        ),
    ]
    requirements_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="URL to fetch associated requirements of the firm.",
            validation_alias=pydantic.AliasChoices("requirements", "requirements_url"),
            serialization_alias="requirements_url",
        ),
    ]
    permissions_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="URL to fetch the associated permissions of the firm.",
            validation_alias=pydantic.AliasChoices("permission", "permissions_url"),
            serialization_alias="permissions_url",
        ),
    ]
    passports_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="URL to fetch the associated passports of the firm.",
            validation_alias=pydantic.AliasChoices("passport", "passports_url"),
            serialization_alias="passports_url",
        ),
    ]
    regulators_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="URL to fetch the associated regulators of the firm.",
            validation_alias=pydantic.AliasChoices("regulators", "regulators_url"),
            serialization_alias="regulators_url",
        ),
    ]
    waivers_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="URL to fetch the associated waivers of the firm.",
            validation_alias=pydantic.AliasChoices("waivers", "waivers_url"),
            serialization_alias="waivers_url",
        ),
    ]
    exclusions_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="URL to fetch the exclusions associated with the firm.",
            validation_alias=pydantic.AliasChoices("exclusions", "exclusions_url"),
            serialization_alias="exclusions_url",
        ),
    ]
    address_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="The URL of the firm's address record in the FCA register.",
            validation_alias=pydantic.AliasChoices("address", "address_url"),
            serialization_alias="address_url",
        ),
    ]
    appointed_representative_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="The URL of the firm's appointed representative list in the FCA register.",
            validation_alias=pydantic.AliasChoices("appointed representative", "appointed_representative_url"),
            serialization_alias="appointed_representative_url",
        ),
    ]
    disciplinary_history_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="The URL of the firm's disciplinary history in the FCA register.",
            validation_alias=pydantic.AliasChoices("disciplinaryhistory", "disciplinary_history_url"),
            serialization_alias="disciplinary_history_url",
        ),
    ]


class FirmNameAlias(base.Base):
    """Current or trading name/brand name of a firm."""

    name: Annotated[
        str,
        pydantic.Field(
            description="The name of the firm.",
            validation_alias=pydantic.AliasChoices("name", "organisation name"),
            serialization_alias="name",
        ),
    ]
    type: Annotated[
        Literal["current", "previous"],
        pydantic.Field(
            description="The type of the name (current or previous).",
            validation_alias=pydantic.AliasChoices("fca_api_address_type", "type"),
            serialization_alias="type",
        ),
    ]
    status: Annotated[
        str,
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The status of the name (e.g., trading, registered).",
        ),
    ]
    effective_from: Annotated[
        datetime.datetime,
        pydantic.Field(
            description="The date from which the name became effective.",
            validation_alias=pydantic.AliasChoices("effective from", "effective_from"),
            serialization_alias="effective_from",
        ),
        field_parsers.ParseFcaDate,
    ]

    effective_to: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="The date until which the name was effective.",
            validation_alias=pydantic.AliasChoices("effective to", "effective_to"),
            serialization_alias="effective_to",
            default=None,
        ),
        field_parsers.ParseFcaDate,
    ]


class FirmAddress(base.Base):
    """A firm address data structure."""

    type: Annotated[
        str,
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The type of an address (e.g., registered, trading).",
            validation_alias=pydantic.AliasChoices("address type", "type"),
            serialization_alias="type",
        ),
    ]
    phone_number: Annotated[
        Optional[str],
        pydantic.Field(
            description="The phone number associated with the address, if available.",
            validation_alias=pydantic.AliasChoices("phone number", "phone_number"),
            serialization_alias="phone_number",
        ),
    ]
    address_lines: Annotated[
        list[str],
        pydantic.Field(
            description="The address lines of the address.",
        ),
    ]

    town: Annotated[
        str,
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The town of the address.",
        ),
    ]
    postcode: Annotated[
        str,
        pydantic.StringConstraints(
            to_upper=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The postcode of the address.",
        ),
    ]
    county: Annotated[
        str,
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The county of the address.",
        ),
    ]
    country: Annotated[
        str,
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The country of the address.",
        ),
    ]

    website: Annotated[
        Optional[pydantic.HttpUrl],
        pydantic.Field(
            description="The website URL associated with the address, if available.",
            validation_alias=pydantic.AliasChoices("website address", "website_url"),
            serialization_alias="website_url",
        ),
        field_parsers.StrOrNone,
    ]
    individual: Annotated[
        Optional[str],
        pydantic.Field(
            description="The individual associated with the address, if available.",
            default=None,
        ),
        field_parsers.StrOrNone,
    ]

    address_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="The URL of the address record in the FCA register.",
            validation_alias=pydantic.AliasChoices("url", "address_url"),
            serialization_alias="address_url",
        ),
    ]


class FirmControlledFunction(base.Base):
    """A firm controlled function data structure."""

    type: Annotated[
        Literal["current", "previous"],
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The type of the controlled function.",
            validation_alias=pydantic.AliasChoices("fca_api_lst_type", "type"),
            serialization_alias="type",
        ),
    ]
    name: Annotated[
        str,
        pydantic.StringConstraints(
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The name of the controlled function.",
        ),
    ]
    effective_date: Annotated[
        datetime.datetime,
        pydantic.Field(
            description="The date from which the controlled function became effective.",
            validation_alias=pydantic.AliasChoices("effective date", "effective_date"),
            serialization_alias="effective_date",
        ),
        field_parsers.ParseFcaDate,
    ]
    end_date: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="The date from which the controlled function became effective.",
            validation_alias=pydantic.AliasChoices("end date", "end_date"),
            serialization_alias="end_date",
            default=None,
        ),
        field_parsers.ParseFcaDate,
    ]
    individual_name: Annotated[
        str,
        pydantic.StringConstraints(
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The name of the individual associated with the controlled function.",
            validation_alias=pydantic.AliasChoices("individual name", "individual_name"),
            serialization_alias="individual_name",
        ),
    ]
    restriction: Annotated[
        Optional[str],
        pydantic.StringConstraints(
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="Any restrictions associated with the controlled function.",
        ),
        field_parsers.StrOrNone,
    ]
    restriction_end_date: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="The end date of any restrictions associated with the controlled function.",
            validation_alias=pydantic.AliasChoices("suspension / restriction end date", "restriction_end_date"),
            serialization_alias="restriction_end_date",
            default=None,
        ),
        field_parsers.ParseFcaDate,
    ]
    restriction_start_date: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="The end date of any restrictions associated with the controlled function.",
            validation_alias=pydantic.AliasChoices("suspension / restriction start date", "restriction_start_date"),
            serialization_alias="restriction_start_date",
            default=None,
        ),
        field_parsers.ParseFcaDate,
    ]
    url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="The URL of the controlled function record in the FCA register.",
        ),
    ]
