from splitwise import Splitwise
from config import splitwise_customer_key, splitwise_customer_secret, splitwise_api_key

def test():
    sw = Splitwise(splitwise_customer_key, splitwise_customer_secret, api_key=splitwise_api_key)
    currentUser = sw.getCurrentUser()
    expenses = sw.getExpenses(limit=10)
    for expense in expenses:
        print(f"Description: {expense.getDescription()}")
        print(f"Cost: {expense.getCost()}")
        print(f"CreatedBy: {expense.getCreatedBy().getFirstName()}")
        debts = expense.getRepayments()
        for debt in debts:
            if debt.getFromUser() == currentUser.getId():
                print(f"Debt : {debt.getAmount()}")
                
        print()

if __name__ == '__main__':
    test()