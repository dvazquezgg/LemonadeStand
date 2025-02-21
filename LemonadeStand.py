'''
Lemonade Stand

A program that will simulate a fixed amount of days of a lemonade stand.

A group of N players will start with a fixed amount of money and will be able to buy lemons, sugar, and cups to make lemonade.

They will then sell the lemonade at a fixed price.

The goal is to make as much money as possible.
'''

import random
from multiprocessing.reduction import recvfds


class Player:

    unit_per_package = {'lemons_kg': 18, 'sugar_kg': 30, 'cups_pack': 10}

    def __init__(self, name, money):
        self.name = name
        self.money = money
        self.lemons = 0
        self.sugar = 0
        self.cups = 0
        self.lemonade = 0
        self.sales = 0
        self.recipe = {'lemons': 3, 'sugar': 1, 'cups': 1}
        self.ingredient_prices = {'lemons': 0.25, 'sugar': 0.10, 'cups': 0.05}
        self.price = 1.00

    def buy(self, lemons_kg, sugar_kg, cups_pack, price):
        lemons = lemons_kg * self.unit_per_package['lemons_kg']
        sugar = sugar_kg * self.unit_per_package['sugar_kg']
        cups = cups_pack * self.unit_per_package['cups_pack']
        # Buy the ingredients
        cost = (lemons_kg * price['lemons'] +
                sugar_kg * price['sugar'] +
                cups_pack * price['cups'])
        cost = round(cost, 2)
        print(cost, self.money)
        if cost > self.money:
            print(f'{self.name} does not have enough money to buy the ingredients')
            return False
        self.money -= cost
        self.lemons += lemons
        self.sugar += sugar
        self.cups += cups
        return True

    def set_recipe(self, lemons, sugar):
        # Set the recipe for the lemonade per cup
        self.recipe['lemons'] = lemons
        self.recipe['sugar'] = sugar
        self.recipe['cups'] = 1

    def purchasing(self, recipe, lemonade_target):
        # Calculate the amount of ingredients needed to make the target amount of lemonade
        lemons = recipe['lemons'] * lemonade_target - self.lemons
        sugar = recipe['sugar'] * lemonade_target - self.sugar
        cups = recipe['cups'] * lemonade_target - self.cups
        print(f"For {lemonade_target} lemonades we need {lemons} lemons, {sugar} tbsp sugar, and {cups} cups")

        lemons_kg = lemons // self.unit_per_package['lemons_kg'] + 1
        sugar_kg = sugar // self.unit_per_package['sugar_kg'] + 1
        cups_pack = cups // self.unit_per_package['cups_pack'] + 1
        print(f"For {lemonade_target} lemonades we need {lemons_kg} kg lemons, {sugar_kg} kg sugar, and {cups_pack} packages of cups")

        return lemons_kg, sugar_kg, cups_pack

    def make(self):
        # Make the maximum amount of lemonade possible with the ingredients
        # using the minimum of the ingredients according to the recipe
        capacity = min(self.lemons // self.recipe['lemons'], self.sugar // self.recipe['sugar'], self.cups // self.recipe['cups'])
        if capacity > self.lemonade: # If the capacity is greater than the current amount of required lemonade
            self.lemons -= (self.lemonade * self.recipe['lemons'])
            self.sugar -= (self.lemonade * self.recipe['sugar'])
            self.cups -= self.lemonade
        else: # If the capacity is less than the current amount of required lemonade
            self.lemons -= (capacity * self.recipe['lemons'])
            self.sugar -= (capacity * self.recipe['sugar'])
            self.cups -= capacity
            self.lemonade = capacity

    def set_price(self, price):
        self.price = price

    def get_cost_per_cup(self):
        lemons_cost = self.recipe['lemons'] * self.ingredient_prices['lemons']
        sugar_cost = self.recipe['sugar'] * self.ingredient_prices['sugar']
        cups_cost = self.recipe['cups'] * self.ingredient_prices['cups']
        return lemons_cost + sugar_cost + cups_cost

    def sell(self, price, weather_pct, factor, recipe):
        pct_factor = weather_pct - (factor + recipe)
        # Sell the lemonade
        possible_sales = int(self.lemonade * (pct_factor/100))
        self.money += possible_sales * price
        self.sales += possible_sales
        self.lemonade = self.lemonade - possible_sales

    def __str__(self):
        return f'{self.name}: ${self.money:.2f} with {self.lemons} lemons, {self.sugar} sugar, {self.cups} cups, {self.lemonade} lemonade, and {self.sales} sales'


class Game:
    ingredient_prices = {'lemons': 1.5, 'sugar': 1.00, 'cups': 2.00}

    def __init__(self, players, days):
        self.players = players
        self.days = days
        self.price = 1.00
        self.weather = ('sunny', 80)
        self.lemonade_prices = []
        self.lemonade_recipe = []

    def get_random_weather(self):
        return random.choice([('Sunny', 100), ('Cloudy', 80), ('Rainy', 50), ('Windy', 25), ('Stormy', 10)])

    def enter_players(self, file=None):
        if file:
            with open(file) as f:
                players = []
                for line in f:
                    name, money = line.strip().split(',')
                    players.append(Player(name, float(money)))
                self.players = players
            return
        num_players = int(input('Enter the number of players: '))
        players = []
        for i in range(num_players):
            name = input(f'Enter the name of player {i + 1}: ')
            money = random.randint(50, 200)
            print (f'The amount of money for {name} is {money:0.2f} ')
            players.append(Player(name, money))
        self.players = players

    def enter_number_of_days(self):
        days = int(input('Enter the number of days: '))
        self.days = days

    def order_lemonade_prices(self):
        self.lemonade_prices = []  #clear the list
        for player in self.players:
            self.lemonade_prices.append((player, player.price));
        self.lemonade_prices.sort(key=lambda x: x[1]) #sort the list by price

    def order_lemonade_recipe(self):
        self.lemonade_recipe = []
        for player in self.players:
            self.lemonade_recipe.append((player, player.recipe['lemons'] / player.recipe['sugar']))
        self.lemonade_recipe.sort(key=lambda x: x[1])

    def updating_prices(self):
        # Update the prices of the ingredients
        for ingredient in self.ingredient_prices:
            if ingredient == 'cups':
                change = random.uniform(-0.05, 0.05)
            elif ingredient == 'lemons':
                change = random.uniform(-0.02, 0.02)
            elif ingredient == 'sugar':
                change = random.uniform(-0.04, 0.04)
            else:
                change = 0
            self.ingredient_prices[ingredient] += change

        print ('The new prices are: ')
        for ingredient in self.ingredient_prices:
            print (f'{ingredient}: {self.ingredient_prices[ingredient]:0.2f}')

    def get_current_prices(self):
        return self.ingredient_prices

    def purchase_ingredients(self, player):
        lemonade_target = player.lemonade
        print(f'{player.name}\'s turn. Purchasing {lemonade_target} lemonades')
        lemons, sugar, cups = player.purchasing(player.recipe, lemonade_target)
        message = f'{player.name} is buying {lemons} kg of lemons, {sugar} kg of sugar, and {cups} packages of cups'
        print(message)
        if player.buy(lemons, sugar, cups, self.ingredient_prices):
            return message
        return f'{player.name} does not have enough money {player.money} to buy the ingredients'

    def simulate_day(self, day):
        print(f'Day {day}')
        #self.weather = self.get_random_weather()
        print(f'The weather is {self.weather[0]} and the percentage is {self.weather[1]}')
        '''
        for player in self.players:
            player.set_price(self.select_price(player))
            lemonade_target = self.select_lemonades_target(player)
            print(f'{player.name}\'s turn. Purchasing {lemonade_target} lemonades')
            lemons, sugar, cups = player.purchasing(player.recipe, lemonade_target)
            print(f'{player.name} is buying {lemons} kg of lemons, {sugar} kg of sugar, and {cups} packages of cups')
            player.buy(lemons, sugar, cups, self.ingredient_prices)
        '''
        self.print_players_table()
        print()

        for player in self.players:
            print(f'{player.name}\'s turn. Making lemonade')
            player.make()

        self.print_players_table()
        print()

        self.order_lemonade_prices()
        self.order_lemonade_recipe()
        for player in self.players:
            print(f'{player.name}\'s turn. Selling lemonade')
            # find the player place in lemonade_prices, that is the factor
            factor = next((i for i, (first, second) in enumerate(self.lemonade_prices) if first == player), -1)
            recipe = next((i for i, (first, second) in enumerate(self.lemonade_recipe) if first == player), -1)
            player.sell(self.price, self.weather[1], factor, recipe)

        print()
        print(f'The weather was {self.weather[0]} and the percentage was {self.weather[1]}')
        self.print_players_table()
        print()

        print('Finishing the day')
        # self.updating_prices()
        for player in self.players:
            player.lemonade = 0

    def simulate(self):
        for day in range(1, self.days + 1):
            self.simulate_day(day)

    def select_lemonades_target(self, player):
        print(f'{player.name}\'s turn. Making lemonade')
        print ('Select the number of lemonades to make')
        while True:
            try:
                lemonade_target = int(input())
                if lemonade_target < 1:
                    raise ValueError
                return lemonade_target
            except ValueError:
                print('Please enter a valid number of lemonades')

    def select_price(self, player):
        print(f'{player.name}\'s turn. Setting the price of the lemonade')
        print(f'The cost per cup according to the recipe is {player.get_cost_per_cup():0.2f}')
        print ('Enter the price of the lemonade')
        while True:
            try:
                price = float(input())
                if price < 0.5:
                    raise ValueError
                return price
            except ValueError:
                print('Please enter a valid price')

    def lemonades_for_day(self, day):
        for player in self.players:
            lemonade_target = self.select_lemonades_target(player)
            print(f'{player.name}\'s turn. Purchasing {lemonade_target} lemonades')
            lemons, sugar, cups = player.purchasing(player.recipe, lemonade_target)
            print(f'{player.name} is buying {lemons} kg of lemons, {sugar} kg of sugar, and {cups} packages of cups')
            player.buy(lemons, sugar, cups, self.ingredient_prices)

    def modify_recipes(self):
        for player in self.players:
            print(f'{player.name}\'s turn. Modifying the recipe')
            lemons = self.enter_valid_lemons(player)
            sugar = self.enter_valid_sugar(player)
            player.set_recipe(lemons, sugar)

    def enter_valid_lemons(self, player):
        while True:
            try:
                lemons = input(f'Enter the number of lemons for {player.name} (currently {player.lemons}): ')
                if lemons == '':
                    lemons = player.lemons
                else:
                    lemons = int(lemons)
                if lemons < 1:
                    raise ValueError
                return lemons
            except ValueError:
                print('Please enter a valid number of lemons')

    def enter_valid_sugar(self, player):
        while True:
            try:
                sugar = input(f'Enter the number of sugar for {player.name} (currently {player.sugar}): ')
                if sugar == '':
                    sugar = player.sugar
                else:
                    sugar = int(sugar)
                if sugar < 1:
                    raise ValueError
                return sugar
            except ValueError:
                print('Please enter a valid number of sugar')

    def print_players_table(self):
        print('|    Player     | Money  | Lemons | Sugar | Cups | Lemonade | Sales |')
        print('|---------------|--------|--------|-------|------|----------|-------|')

        for player in self.players:
            print(f"|{player.name:15s}| {player.money:6.2f} | {player.lemons:6d} | {player.sugar:5d} | {player.cups:4d} | {player.lemonade:8d} | {player.sales:5d} |")

def main():
    game = Game([], 0)
    game.enter_players("players.txt")
    game.enter_number_of_days()
    for day in range(1, game.days + 1):
        game.modify_recipes()
        game.simulate_day(day)

    print('The final results are:')
    game.print_players_table()

if __name__ == '__main__':
    main()