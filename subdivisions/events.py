"""PubSub Events.

Declare here all PubSub topics which will be used.

These Topics will be created on AWS, when you send his first message.

"""
from enum import Enum


class UserEvents(Enum):
    USER_REGISTERED = "user_registered"
    USER_ACTIVATED = "user_activated"
    USER_LOGGED_IN = "user_logged_in"


class AccountEvents(Enum):
    BANK_ACCOUNT_REGISTERED = "bank_account_registered"
    AD_ACCOUNT_REGISTERED = "google_ad_account_registered"
    POLISHED_STATEMENT_TABLE = "polished_statement_table"


class ProposalEvents(Enum):
    PROPOSAL_SELECTED = "proposal_selected"
    PROPOSAL_APPROVED = "proposal_approved"
    PROPOSAL_ACCEPTED = "proposal_accepted"


class CompanyEvents(Enum):
    COMPANY_REGISTERED = "company_registered"


class HubspotEvents(Enum):
    ORIGINATION_REGISTERED = "origination_registered"


class AdsEvents(Enum):
    ADS_ACCOUNT_CONNECTION = "ads_account_connection"
