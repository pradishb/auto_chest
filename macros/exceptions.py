''' Module to store exception classes '''


class CompletedAccount(Exception):
    ''' Raised when an completed account is detected '''


class BadResponseException(Exception):
    ''' Raised when the response from server is bad '''


class LootRetrieveException(Exception):
    ''' Raised when there is an error retriving loot '''
