from __future__ import annotations

from typing import List

from pytailor.common.base import APIBase
from pytailor.clients import RestClient
from pytailor.models import Account as AccountModel


class Account(APIBase):
    """
    Represents a Tailor Account.

    Parameters
    ----------
    account_model : tailor.models.Account
        An account data model (REST layer)
    """

    def __init__(self, account_model: AccountModel):
        self.id = account_model.id
        self.__account_model = account_model
        self.name = self.__account_model.organization_name
        self.workflow_definitions_owned = (
            self.__account_model.workflow_definitions_owned
        )

    @classmethod
    def get_my_accounts(cls) -> List[Account]:
        """Get list of all my accounts."""
        with RestClient() as client:
            account_models = cls._handle_request(
                client.get_accounts, error_msg=f"Error while fetching accounts."
            )
        accounts = []
        for account_model in account_models:
            accounts.append(cls(account_model))
        return accounts
