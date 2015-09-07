class account:
    
    def __init__(self, bank, sort, number, name, balance, available):

        self.bank = bank
        self.sort = sort
        self.number = number
        self.name = name
        self.balance = balance
        self.available = available

    def get_name(self):
        return self.name

    def __str__(self):
        return  self.sort + ' ' + \
                self.number + ' ' + \
                self.bank + ' ' + \
                self.name +' ' + \
                str(self.balance) + ' ' + \
                str(self.available)
