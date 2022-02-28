from splitwise import Splitwise
from config import *

import ynab
from ynab.rest import ApiException

############################################################################
# Splitwise functions
############################################################################

class Splitwise_transaction:
    '''Class represnting a Splitwise transaction'''
    def __init__(self, name, amount, date, details) -> None:
        self.name = name
        self.amount = int(float(amount) * 1000)
        self.date = date
        self.details = details


def get_splitwise_transactions(splitwise_customer_key, splitwise_customer_secret, splitwise_api_key):
    '''Returns all the details needed from a splitwise transcation, if the
    transaction is a debt to current user.
    '''
    sw = Splitwise(splitwise_customer_key,
                   splitwise_customer_secret, api_key=splitwise_api_key)
    currentUser = sw.getCurrentUser()
    expenses = sw.getExpenses()
    transactions = []
    for expense in expenses:
        debts = expense.getRepayments()
        for debt in debts:
            if debt.getFromUser() == currentUser.getId():
                transactions.append(
                    Splitwise_transaction(
                        name=expense.getCreatedBy().getFirstName(),
                        amount=debt.getAmount(),
                        date=expense.getDate(),
                        details=expense.getDescription()
                    )
                )
    return transactions

############################################################################
# YNAB functions
############################################################################

def get_budget_id(api_client):
    '''Returns the budget id of a YNAB budget that matches the budget name'''
    # create an instance of the API class
    api_instance = ynab.BudgetsApi(api_client)

    try:
        # List budgets
        api_response = api_instance.get_budgets()
        for budget in api_response.data.budgets:
            if budget.name == ynab_budget_name:
                return budget.id
        raise RuntimeError("Budget Name not found.")
    except ApiException as e:
        print("Exception when calling BudgetsApi->get_budgets: %s\n" % e)

def verify_splitwise_account_name(api_client, budget_id, account_name):
    '''Returns the splitwise account id for the name provided by config file
    for an associated budget ID'''
    # create an instance of the API class
    api_instance = ynab.AccountsApi(api_client)

    try:
        # List budgets
        api_response = api_instance.get_accounts(budget_id)
        for account in api_response.data.accounts:
            if account.name == account_name:
                return account.id
        raise RuntimeError(f"Account Name: {account_name} not found.")
    except ApiException as e:
        print(f"Exception when calling BudgetsApi->get_budgets: {e}")

def convert_transactions(api_client, account_id, splitwise_transactions):
    '''Converts all Splitwise transactions to ynab transactions'''
    ynab_transactions = []
    for transaction in splitwise_transactions:
        ynab_transactions.append(
            ynab.SaveTransaction(
                account_id=account_id,
                date=transaction.date,
                amount=transaction.amount,
                payee_name=transaction.name,
                memo=transaction.details,
                import_id=f"SW-{transaction.amount}-{transaction.date}"
            )
        )

    return ynab_transactions

def create_transactions(api_client, budget_id, account_id, splitwise_transactions):
    '''Create transactions in YNAB'''
    api_instance = ynab.TransactionsApi(api_client)
    ynab_transactions = convert_transactions(api_client, account_id, splitwise_transactions)

    bulk_transactions = ynab.BulkTransactions(ynab_transactions)
    try:
        # Bulk create transactions
        api_response = api_instance.bulk_create_transactions(budget_id, bulk_transactions)
        print(api_response)
    except ApiException as e:
        print(f"Exception when calling TransactionsApi->bulk_create_transactions: {e}")

def splitwise_to_ynab():
    # Configure API key authorization: bearer
    configuration = ynab.Configuration()
    configuration.api_key['Authorization'] = ynab_access_token
    # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
    configuration.api_key_prefix['Authorization'] = 'Bearer'
    api_client = ynab.ApiClient(configuration)

    budget_id = get_budget_id(api_client)
    account_id = verify_splitwise_account_name(
        api_client,
        budget_id=budget_id,
        account_name=ynab_splitwise_account_name
    )

    splitwise_transactions = get_splitwise_transactions(
        splitwise_customer_key,
        splitwise_customer_secret,
        splitwise_api_key
    )
    # Upload transcations to the ynab as bulk transactions
    create_transactions(
        api_client,
        budget_id=budget_id,
        account_id=account_id,
        splitwise_transactions=splitwise_transactions
    )


if __name__ == '__main__':
    # TODO : Use last-updated to avoid older transactions
    splitwise_to_ynab()
