import datetime
from typing import Annotated, Literal, Optional

import pydantic

from . import base, field_parsers


class FirmDetails(base.Base):
    """Core details for a firm on the FCA register.

    This model represents the main firm details returned by the register,
    including identifiers, status information, key regulatory flags and
    links to related resources. It is the primary type returned by
    high-level methods such as ``Client.get_firm``.

    The field definitions handle common FCA patterns such as mixed-case
    field names, date parsing and normalisation of status and type values.
    """

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
            description="Additional information about exceptional notices associated with the firm.",
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
    """Address details for a firm.

    Includes contact information (such as phone and website) as well as the
    full postal address as shown in the FCA register.
    """

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
    """Details of a controlled function associated with a firm.

    Represents roles such as significant influence or controlled functions
    that individuals perform for the firm, together with effective dates
    and any associated restrictions.
    """

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
            description="The date on which the controlled function ended, if applicable.",
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
            description="The start date of any restrictions associated with the controlled function.",
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


class FirmIndividual(base.Base):
    """An individual associated with a firm."""

    irn: Annotated[
        str,
        pydantic.Field(
            description="The individual reference number (IRN) of the individual.",
        ),
    ]
    name: Annotated[
        str,
        pydantic.StringConstraints(
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The name of the individual.",
        ),
    ]
    status: Annotated[
        str,
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The status of the individual.",
        ),
    ]

    url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="The URL of the individual record in the FCA register.",
        ),
    ]


class FirmPermission(base.Base):
    """A permission associated with a firm."""

    name: Annotated[
        str,
        pydantic.Field(
            description="The name of the permission.",
            validation_alias=pydantic.AliasChoices("fca_api_permission_name", "name"),
            serialization_alias="name",
        ),
    ]
    customer_type: Annotated[
        Optional[list[str]],
        pydantic.Field(
            description="The types of customers the permission applies to.",
            validation_alias=pydantic.AliasChoices("customer type", "customer_type"),
            serialization_alias="customer_type",
            default=None,
        ),
    ]
    limitation: Annotated[
        Optional[list[str]],
        pydantic.Field(
            description="Any limitations associated with the permission.",
            default=None,
        ),
    ]
    limitation_not_found: Annotated[
        Optional[list[str]],
        pydantic.Field(
            description="Limitations referenced in the FCA data but not resolved to a known limitation entry.",
            validation_alias=pydantic.AliasChoices("limitation not found", "limitation_not_found"),
            serialization_alias="limitation_not_found",
            default=None,
        ),
    ]
    investment_type: Annotated[
        Optional[list[str]],
        pydantic.Field(
            description="The types of investments the permission relates to.",
            validation_alias=pydantic.AliasChoices("investment type", "investment_type"),
            serialization_alias="investment_type",
            default=None,
        ),
    ]
    acting_as_cbtl_advisor: Annotated[
        Optional[bool],
        pydantic.Field(
            description="Indicates whether the permission involves acting as a CBTL advisor.",
            validation_alias=pydantic.AliasChoices("acting as a cbtl advisor", "acting_as_cbtl_advisor"),
            serialization_alias="acting_as_cbtl_advisor",
            default=None,
        ),
    ]
    acting_as_cbtl_administrator: Annotated[
        Optional[bool],
        pydantic.Field(
            description="Indicates whether the permission involves acting as a CBTL administrator.",
            validation_alias=pydantic.AliasChoices("acting as a cbtl administrator", "acting_as_cbtl_administrator"),
            serialization_alias="acting_as_cbtl_administrator",
            default=None,
        ),
    ]
    acting_as_cbtl_arranger: Annotated[
        Optional[bool],
        pydantic.Field(
            description="Indicates whether the permission involves acting as a CBTL arranger.",
            validation_alias=pydantic.AliasChoices("acting as a cbtl arranger", "acting_as_cbtl_arranger"),
            serialization_alias="acting_as_cbtl_arranger",
            default=None,
        ),
    ]
    acting_as_cbtl_lender: Annotated[
        Optional[bool],
        pydantic.Field(
            description="Indicates whether the permission involves acting as a CBTL lender or provider of credit.",
            validation_alias=pydantic.AliasChoices("acting as a cbtl lender", "acting_as_cbtl_lender"),
            serialization_alias="acting_as_cbtl_lender",
            default=None,
        ),
    ]
    cbtl_effective_date: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="The effective date for CBTL-related permissions.",
            validation_alias=pydantic.AliasChoices("cbtl effective date", "cbtl_effective_date"),
            serialization_alias="cbtl_effective_date",
            default=None,
        ),
        field_parsers.ParseFcaDate,
    ]
    cbtl_status: Annotated[
        Optional[str],
        pydantic.Field(
            description="The status for CBTL-related permissions.",
            validation_alias=pydantic.AliasChoices("cbtl status", "cbtl_status"),
            serialization_alias="cbtl_status",
            default=None,
        ),
    ]


class FirmRequirement(base.RelaxedBase):
    """A requirement associated with a firm."""

    model_config = pydantic.ConfigDict(extra="allow")

    reference: Annotated[
        str,
        pydantic.Field(
            description="The reference identifier for the requirement.",
            validation_alias=pydantic.AliasChoices("requirement reference", "reference"),
            serialization_alias="reference",
        ),
        pydantic.StringConstraints(
            strip_whitespace=True,
            to_upper=True,
        ),
    ]
    effective_date: Annotated[
        datetime.datetime,
        pydantic.Field(
            description="The date from which the requirement became effective.",
            validation_alias=pydantic.AliasChoices("effective date", "effective_date"),
            serialization_alias="effective_date",
        ),
        field_parsers.ParseFcaDate,
    ]
    financial_promotions_requirement: Annotated[
        bool,
        pydantic.Field(
            description="Indicates whether the requirement is related to financial promotions.",
            validation_alias=pydantic.AliasChoices(
                "financial promotions requirement", "financial_promotions_requirement"
            ),
            serialization_alias="financial_promotions_requirement",
        ),
    ]
    financial_promotions_investment_types: Annotated[
        Optional[pydantic.HttpUrl],
        pydantic.Field(
            description="URL to fetch the investment types associated with the requirement.",
            validation_alias=pydantic.AliasChoices(
                "financial promotions investment types", "financial_promotions_investment_types"
            ),
            serialization_alias="financial_promotions_investment_types",
            default=None,
        ),
    ]


class FirmRequirementInvestmentType(base.Base):
    """An investment type associated with a firm requirement."""

    name: Annotated[
        str,
        pydantic.Field(
            description="The name of the investment type.",
            validation_alias=pydantic.AliasChoices("investment type name", "name"),
            serialization_alias="name",
        ),
        pydantic.StringConstraints(
            strip_whitespace=True,
            to_lower=True,
        ),
    ]


class FirmRegulator(base.Base):
    """A regulator associated with a firm."""

    name: Annotated[
        str,
        pydantic.Field(
            description="The name of the regulator.",
            validation_alias=pydantic.AliasChoices("regulator name", "name"),
            serialization_alias="name",
        ),
        pydantic.StringConstraints(
            strip_whitespace=True,
        ),
    ]
    effective_date: Annotated[
        datetime.datetime,
        pydantic.Field(
            description="The date from which the regulator association became effective.",
            validation_alias=pydantic.AliasChoices("effective date", "effective_date"),
            serialization_alias="effective_date",
        ),
        field_parsers.ParseFcaDate,
    ]
    termination_date: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="The date on which the regulator association was terminated, if applicable.",
            validation_alias=pydantic.AliasChoices("termination date", "termination_date"),
            serialization_alias="termination_date",
            default=None,
        ),
        field_parsers.ParseFcaDate,
    ]


class FirmPassport(base.Base):
    """A passport associated with a firm."""

    country: Annotated[
        str,
        pydantic.Field(
            description="The country associated with the passport.",
        ),
        pydantic.StringConstraints(
            strip_whitespace=True,
            to_upper=True,
        ),
    ]
    permissions: Annotated[
        str,
        pydantic.Field(
            description="The permissions granted under the passport.",
        ),
        pydantic.StringConstraints(
            strip_whitespace=True,
            to_lower=True,
        ),
    ]
    direction: Annotated[
        Literal["in", "out"],
        pydantic.Field(
            description="The direction of the passport (inbound or outbound).",
            validation_alias=pydantic.AliasChoices("passportdirection", "direction"),
            serialization_alias="direction",
        ),
        pydantic.BeforeValidator(
            lambda val: {
                "passporting out": "out",
                "passporting in": "in",
            }.get(val.strip().lower(), val)
        ),
    ]


class PassportPermission(base.Base):
    """A permission associated with a firm passport."""

    name: Annotated[
        str,
        pydantic.Field(
            description="The name of the passport permission.",
            validation_alias=pydantic.AliasChoices("Name", "name"),
            serialization_alias="name",
        ),
        pydantic.StringConstraints(
            strip_whitespace=True,
            to_lower=True,
        ),
    ]
    investment_types: Annotated[
        list[str],
        pydantic.Field(
            description="The investment types associated with the passport permission.",
            validation_alias=pydantic.AliasChoices("InvestmentTypes", "investment_types"),
            serialization_alias="investment_types",
        ),
    ]


class FirmPassportPermission(FirmPassport):
    """A permission associated with a firm passport."""

    directive: Annotated[
        str,
        pydantic.Field(
            description="The directive under which the passport permission is granted.",
        ),
        pydantic.StringConstraints(
            strip_whitespace=True,
            to_lower=True,
        ),
    ]
    type: Annotated[
        str,
        pydantic.Field(
            description="The type of the passport.",
            validation_alias=pydantic.AliasChoices("passporttype", "type"),
            serialization_alias="type",
        ),
        pydantic.StringConstraints(
            strip_whitespace=True,
            to_lower=True,
        ),
    ]
    permissions: Annotated[
        list[PassportPermission],
        pydantic.Field(
            description="The specific permissions granted under the passport.",
        ),
    ]


class FirmWaiver(base.Base):
    """A waiver associated with a firm."""

    rule_article_numbers: Annotated[
        list[str],
        pydantic.Field(
            description="The rule or article numbers associated with the waiver.",
            validation_alias=pydantic.AliasChoices("rule_articleno", "rule_article_numbers"),
            serialization_alias="rule_article_numbers",
        ),
    ]
    discretions: Annotated[
        Optional[str],
        pydantic.Field(
            description="The discretions granted under the waiver.",
            validation_alias=pydantic.AliasChoices("waivers_discretions", "discretions"),
            serialization_alias="discretions",
        ),
    ]
    discretions_url: Annotated[
        Optional[pydantic.HttpUrl],
        pydantic.Field(
            description="URL to fetch more details about the discretions associated with the waiver.",
            validation_alias=pydantic.AliasChoices("waivers_discretions_url", "discretions_url"),
            serialization_alias="discretions_url",
        ),
    ]


class FirmExclusion(base.Base):
    """An exclusion associated with a firm."""

    type: Annotated[
        str,
        pydantic.Field(
            description="The type of the exclusion.",
            validation_alias=pydantic.AliasChoices("psd2_exclusion_type", "type"),
            serialization_alias="type",
        ),
        pydantic.StringConstraints(
            strip_whitespace=True,
            to_lower=True,
        ),
    ]
    description_of_services: Annotated[
        str,
        pydantic.Field(
            description="Description of the services excluded.",
        ),
    ]
    particular_exclusion_relied_upon: Annotated[
        Optional[str],
        pydantic.Field(
            description="Details of the particular exclusion relied upon.",
        ),
    ]


class FirmDisciplinaryRecord(base.Base):
    """A disciplinary record associated with a firm."""

    type_of_description: Annotated[
        str,
        pydantic.Field(
            description="Description of the disciplinary action taken.",
            validation_alias=pydantic.AliasChoices("typeofdescription", "type_of_description"),
            serialization_alias="type_of_description",
        ),
        pydantic.StringConstraints(
            strip_whitespace=True,
        ),
    ]

    type_of_action: Annotated[
        str,
        pydantic.Field(
            description="The type of disciplinary action taken.",
            validation_alias=pydantic.AliasChoices("typeofaction", "type_of_action"),
            serialization_alias="type_of_action",
        ),
        pydantic.StringConstraints(
            strip_whitespace=True,
            to_lower=True,
        ),
    ]

    enforcement_type: Annotated[
        str,
        pydantic.Field(
            description="The type of enforcement action taken.",
            validation_alias=pydantic.AliasChoices("enforcementtype", "enforcement_type"),
            serialization_alias="enforcement_type",
        ),
        pydantic.StringConstraints(
            strip_whitespace=True,
            to_upper=True,
        ),
    ]

    effective_from: Annotated[
        datetime.datetime,
        pydantic.Field(
            description="The date from which the disciplinary action became effective.",
            validation_alias=pydantic.AliasChoices("actioneffectivefrom", "effective_from"),
            serialization_alias="effective_from",
        ),
        field_parsers.ParseFcaDate,
    ]


class FirmAppointedRepresentative(base.Base):
    """An appointed representative associated with a firm."""

    type: Annotated[
        Literal["current", "previous"],
        pydantic.Field(
            description="The type of the appointed representative.",
            validation_alias=pydantic.AliasChoices("fca_api_lst_type", "type"),
            serialization_alias="type",
        ),
    ]
    subtype: Annotated[
        str,
        pydantic.StringConstraints(
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The subtype of the appointed representative.",
            validation_alias=pydantic.AliasChoices("recordsubtype", "subtype"),
            serialization_alias="subtype",
        ),
    ]
    name: Annotated[
        str,
        pydantic.StringConstraints(
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The name of the appointed representative.",
        ),
    ]
    url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="The URL of the appointed representative record in the FCA register.",
        ),
    ]
    frn: Annotated[
        str,
        pydantic.Field(
            description="The firm reference number (FRN) of the appointed representative.",
        ),
    ]
    principal_frn: Annotated[
        str,
        pydantic.Field(
            description="The firm reference number (FRN) of the principal firm.",
            validation_alias=pydantic.AliasChoices("principal frn", "principal_frn"),
            serialization_alias="principal_frn",
        ),
    ]
    principal_firm_name: Annotated[
        str,
        pydantic.StringConstraints(
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The name of the principal firm.",
            validation_alias=pydantic.AliasChoices("principal firm name", "principal_firm_name"),
            serialization_alias="principal_firm_name",
        ),
    ]
    effective_date: Annotated[
        datetime.datetime,
        pydantic.Field(
            description="The date from which the appointed representative became effective.",
            validation_alias=pydantic.AliasChoices("effective date", "effective_date"),
            serialization_alias="effective_date",
        ),
        field_parsers.ParseFcaDate,
    ]
    termination_date: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="The date on which the appointed representative was terminated, if applicable.",
            validation_alias=pydantic.AliasChoices("termination date", "termination_date"),
            serialization_alias="termination_date",
            default=None,
        ),
        field_parsers.ParseFcaDate,
    ]
    tied_agent: Annotated[
        bool,
        pydantic.Field(
            description="Indicates whether the appointed representative is a tied agent.",
            validation_alias=pydantic.AliasChoices("tied agent", "tied_agent"),
            serialization_alias="tied_agent",
        ),
    ]
    eea_tied_agent: Annotated[
        bool,
        pydantic.Field(
            description="Indicates whether the appointed representative is a tied agent.",
            validation_alias=pydantic.AliasChoices("eea tied agent", "eea_tied_agent"),
            serialization_alias="eea_tied_agent",
        ),
    ]
