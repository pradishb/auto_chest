class Account:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __str__(self):
        return self.username


class AccountList:
    ''' Class to store a list of account objects '''

    def __init__(self):
        self.accounts = []

    def append(self, account):
        ''' Adds an account instance to list '''
        self.accounts.append(account)

    def current(self):
        if self.accounts == []:
            return None
        return self.accounts[0]

    def complete(self):
        return self.accounts.pop(0)
