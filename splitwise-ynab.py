from splitwise import Splitwise
from config import *

import ynab
from ynab.rest import ApiException

############################################################################
# Splitwise functions
############################################################################

def test_splitwise():
    '''Prints all the details needed from a splitwise transcation, if the
    transaction is a debt to current user.
    '''
    sw = Splitwise(splitwise_customer_key,
                   splitwise_customer_secret, api_key=splitwise_api_key)
    currentUser = sw.getCurrentUser()
    expenses = sw.getExpenses()
    for expense in expenses:
        # help(expense)
        # print(f"Cost: {expense.getCost()}")
        debts = expense.getRepayments()
        for debt in debts:
            if debt.getFromUser() == currentUser.getId():
                print(f"CreatedBy: {expense.getCreatedBy().getFirstName()}")
                print(f"Date: {expense.getDate()}")
                print(f"Description: {expense.getDescription()}")
                print(f"Debt : {debt.getAmount()}")
                print()

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

def get_splitwise_account_id(api_client, budget_id):
    '''Returns the splitwise account id for the name provided by config file
    for an associated budget ID'''
    # create an instance of the API class
    api_instance = ynab.AccountsApi(api_client)

    try:
        # List budgets
        api_response = api_instance.get_accounts(budget_id)
        for account in api_response.data.accounts:
            if account.name == ynab_splitwise_account_name:
                return account.id
        raise RuntimeError("Account Name 'Splitwise' not found.")
    except ApiException as e:
        print("Exception when calling BudgetsApi->get_budgets: %s\n" % e)

def test_ynab():
    # Configure API key authorization: bearer
    configuration = ynab.Configuration()
    configuration.api_key['Authorization'] = ynab_access_token
    # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
    configuration.api_key_prefix['Authorization'] = 'Bearer'
    api_client = ynab.ApiClient(configuration)

    budget_id = get_budget_id(api_client)
    account_id = get_splitwise_account_id(api_client, budget_id)

if __name__ == '__main__':
    test_splitwise()
    test_ynab()
