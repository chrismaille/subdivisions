from subdivisions.events import (
    AccountEvents,
    AdsEvents,
    CompanyEvents,
    HubspotEvents,
    ProposalEvents,
    UserEvents,
)


class TestEvents:
    def test_event_user_events(self):
        assert UserEvents.USER_REGISTERED
        assert UserEvents.USER_ACTIVATED
        assert UserEvents.USER_LOGGED_IN

    def test_event_account_events(self):
        assert AccountEvents.BANK_ACCOUNT_REGISTERED
        assert AccountEvents.AD_ACCOUNT_REGISTERED
        assert AccountEvents.POLISHED_STATEMENT_TABLE

    def test_event_proposal_events(self):
        assert ProposalEvents.PROPOSAL_SELECTED
        assert ProposalEvents.PROPOSAL_APPROVED
        assert ProposalEvents.PROPOSAL_ACCEPTED

    def test_event_company_events(self):
        assert CompanyEvents.COMPANY_REGISTERED

    def test_event_hubspot_events(self):
        assert HubspotEvents.ORIGINATION_REGISTERED

    def test_event_ads_events(self):
        assert AdsEvents.ADS_ACCOUNT_CONNECTION
