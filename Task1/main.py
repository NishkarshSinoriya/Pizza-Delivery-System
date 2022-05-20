import json
from collections import deque
from operator import itemgetter
import time
from datetime import datetime
import csv
from threading import Thread

# opening, loading and sorting json file in desired order
f = open('orders.json')
data = json.load(f)
sorted_data = sorted(data, key=lambda k: k['Order_ID'])

# making desired dictionary from data to make an order queue out of it
order_dictionary = {}
for i in range(0, len(sorted_data)):
    order_dictionary[sorted_data[i]['Order_ID']] = [sorted_data[i]['Order_ID'], sorted_data[i]['Small_Pizza'],
                                                    sorted_data[i]['Medium_Pizza'], sorted_data[i]['Large_Pizza']]


# Queue implementation using deque
class Queue:

    def __init__(self):
        self.buffer = deque()

    def enqueue(self, val):
        self.buffer.appendleft(val)

    def dequeue(self):
        return self.buffer.pop()

    def is_empty(self):
        return len(self.buffer) == 0

    def size(self):
        return len(self.buffer)

    def view(self):
        for _ in range(self.size()):
            print(self.buffer[_])


# pushing dictionary to form an order queue
order_queue = Queue()
for i in order_dictionary:
    order_queue.enqueue(order_dictionary[i])

f.close()


class Order:
    def __init__(self, queue):
        self.queue = queue

    def pick_order(self):
        popped_order = self.queue.dequeue()
        return popped_order


class number_of_pizza:
    def __init__(self, order):
        self.order = order

    def no_of_small_pizzas(self):
        return self.order[1]

    def no_of_medium_pizzas(self):
        return self.order[2]

    def no_of_large_pizzas(self):
        return self.order[3]

    def no_of_total_pizzas(self):
        total = 0
        for j in self.order:
            total += j
        return total


class Ingredients:
    def __init__(self, dough, sauce, toppings):
        self.dough = dough
        self.sauce = sauce
        self.toppings = toppings


class Pizza:

    @staticmethod
    def small_pizza():
        return Ingredients(1, 1, 2)

    @staticmethod
    def medium_pizza():
        return Ingredients(2, 1, 3)

    @staticmethod
    def large_pizza():
        return Ingredients(3, 2, 4)


# Empty dough, sauce and toppings queues
dough_queue = Queue()
sauce_queue = Queue()
toppings_queue = Queue()


# Assignments ids to the elements of Ingredients
def add_new_ingredient_queue(que, length):
    for _i in range(1, length):
        if que == dough_queue:
            que.enqueue('D-' + str(time.time()))
        elif que == sauce_queue:
            que.enqueue('S-' + str(time.time()))
        else:
            que.enqueue('T-' + str(time.time()))
    return que


class Stock:

    # taking ingredients from stock

    @staticmethod
    def taking_ingredient(que, pizza_type):
        pizza_types = ['small', 'medium', 'large']
        used_ingredients = []
        if pizza_type == pizza_types[0]:
            if que == dough_queue:
                var = Pizza.small_pizza().dough
                for _i in range(0, var):
                    used_ingredients.append(dough_queue.dequeue())

            elif que == sauce_queue:
                var = Pizza.small_pizza().sauce
                for _i in range(0, var):
                    used_ingredients.append(sauce_queue.dequeue())

            elif que == toppings_queue:
                var = Pizza.small_pizza().toppings
                for _i in range(0, var):
                    used_ingredients.append(toppings_queue.dequeue())

        elif pizza_type == pizza_types[1]:
            if que == dough_queue:
                var = Pizza.medium_pizza().dough
                for _i in range(0, var):
                    used_ingredients.append(dough_queue.dequeue())

            elif que == sauce_queue:
                var = Pizza.medium_pizza().sauce
                for _i in range(0, var):
                    used_ingredients.append(sauce_queue.dequeue())

            elif que == toppings_queue:
                var = Pizza.medium_pizza().toppings
                for _i in range(0, var):
                    used_ingredients.append(toppings_queue.dequeue())

        elif pizza_type == pizza_types[2]:
            if que == dough_queue:
                var = Pizza.large_pizza().dough
                for _i in range(0, var):
                    used_ingredients.append(dough_queue.dequeue())

            elif que == sauce_queue:
                var = Pizza.large_pizza().sauce
                for _i in range(0, var):
                    used_ingredients.append(sauce_queue.dequeue())

            elif que == toppings_queue:
                var = Pizza.large_pizza().toppings
                for _i in range(0, var):
                    used_ingredients.append(toppings_queue.dequeue())

        return used_ingredients

    @staticmethod
    def refilling_stock():
        # Assuming number of dough pieces in one pack are 200
        add_new_ingredient_queue(dough_queue, 201)  # generating random numbers to make each dough piece unique
        # Assuming number of sauce servings in one sauce container are 400
        add_new_ingredient_queue(sauce_queue, 401)  # generating random numbers to make each sauce serving unique
        # Assuming number of toppings in one topping heap are 100
        add_new_ingredient_queue(toppings_queue, 101)  # generating random numbers to make each topping serving unique


class Error(Exception):
    pass


class Stock_not_enough(Error):
    pass


class Cooking:
    # Stocking the stock for the very first time
    Stock().refilling_stock()
    collection_queue = []

    def preparing_pizza(self):
        pizza_types = ['small', 'medium', 'large']
        o = Order(order_queue)

        for __i in range(0, order_queue.size()):
            # pick the order to be cooked
            picked_order = o.pick_order()
            time_accepted = datetime.now().strftime("%H:%M:%S")
            small_pizzas = number_of_pizza(picked_order).no_of_small_pizzas()
            medium_pizzas = number_of_pizza(picked_order).no_of_medium_pizzas()
            large_pizzas = number_of_pizza(picked_order).no_of_large_pizzas()
            collection_dictionary = {'Order ID': picked_order[0], 'Time Accepted': time_accepted,
                                     'Number of Small Pizzas': small_pizzas,
                                     'Number of Medium Pizzas': medium_pizzas, 'Number of Large Pizzas': large_pizzas,
                                     'Total Pizzas': small_pizzas + medium_pizzas + large_pizzas, 'IDs for Dough': [],
                                     'IDs for Sauce': [], 'IDs for Toppings': []}

            # checking stock and preparing pizzas now----->
            try:
                if (dough_queue.size() >= small_pizzas * Pizza().small_pizza().dough and
                        sauce_queue.size() >= small_pizzas * Pizza().small_pizza().sauce and
                        toppings_queue.size() >= small_pizzas * Pizza().small_pizza().toppings):

                    for _i in range(0, small_pizzas):
                        # picking ingredients for small_pizzas **** 2
                        dough_ingredients = Stock().taking_ingredient(dough_queue, pizza_types[0])
                        collection_dictionary['IDs for Dough'] += dough_ingredients
                        sauce_ingredients = Stock().taking_ingredient(sauce_queue, pizza_types[0])
                        collection_dictionary['IDs for Sauce'] += sauce_ingredients
                        topping_ingredients = Stock().taking_ingredient(toppings_queue, pizza_types[0])
                        collection_dictionary['IDs for Toppings'] += topping_ingredients
                        time.sleep(.02)
            except Stock_not_enough:
                print("Not enough stock to make small pizzas for this order")

            try:
                if (dough_queue.size() >= medium_pizzas * Pizza().medium_pizza().dough and
                        sauce_queue.size() >= medium_pizzas * Pizza().medium_pizza().sauce and
                        toppings_queue.size() >= medium_pizzas * Pizza().medium_pizza().toppings):

                    for _i in range(0, medium_pizzas):
                        # picking ingredients for medium_pizzas **** 2
                        dough_ingredients = Stock().taking_ingredient(dough_queue, pizza_types[1])
                        collection_dictionary['IDs for Dough'] += dough_ingredients
                        sauce_ingredients = Stock().taking_ingredient(sauce_queue, pizza_types[1])
                        collection_dictionary['IDs for Sauce'] += sauce_ingredients
                        topping_ingredients = Stock().taking_ingredient(toppings_queue, pizza_types[1])
                        collection_dictionary['IDs for Toppings'] += topping_ingredients
                        time.sleep(.02)
            except Stock_not_enough:
                print("Not enough stock to make medium pizzas for this order")

            try:
                if (dough_queue.size() >= large_pizzas * Pizza().large_pizza().dough and
                        sauce_queue.size() >= large_pizzas * Pizza().large_pizza().sauce and
                        toppings_queue.size() >= large_pizzas * Pizza().large_pizza().toppings):

                    for _i in range(0, large_pizzas):
                        # picking ingredients for large_pizzas **** 1
                        dough_ingredients = Stock().taking_ingredient(dough_queue, pizza_types[2])
                        collection_dictionary['IDs for Dough'] += dough_ingredients
                        sauce_ingredients = Stock().taking_ingredient(sauce_queue, pizza_types[2])
                        collection_dictionary['IDs for Sauce'] += sauce_ingredients
                        topping_ingredients = Stock().taking_ingredient(toppings_queue, pizza_types[2])
                        collection_dictionary['IDs for Toppings'] += topping_ingredients
                        time.sleep(.02)
            except Stock_not_enough:
                print("Not enough stock to make large pizzas for this order")
            Cooking.cooking_pizza()
            self.collection_queue.append(collection_dictionary)
            self.collection_queue.sort(key=itemgetter('Total Pizzas'), reverse=True)
            # print(self.collection_queue)

    @staticmethod
    def cooking_pizza():
        for __o in sorted_data:
            time.sleep(0.01 * (__o['Small_Pizza'] + __o['Medium_Pizza'] + __o['Large_Pizza']))


class Delivery:
    def __init__(self):
        self.header = ['Order ID', 'Time Accepted', 'Number of Small Pizzas',
                       'Number of Medium Pizzas', 'Number of Large Pizzas', 'Total Pizzas',
                       'IDs for Dough', 'IDs for Sauce', 'IDs for Toppings', 'Time Collected']

    def create_header_in_csv(self):
        with open('csv_report.csv', 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.header)
            writer.writeheader()
        csvfile.close()

    def make_csv(self, present_order, time_collected):
        present_order['Time Collected'] = time_collected
        with open('csv_report.csv', 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.header)
            writer.writerow(present_order)
        csvfile.close()

    def deliver_pizza(self, present_order):
        time_collected = datetime.now().strftime("%H:%M:%S")
        self.make_csv(present_order, time_collected)


def start_cooking():
    Cooking().preparing_pizza()


def start_delivering():
    all_order = len(sorted_data)
    deliver_queue = Cooking.collection_queue
    while all_order != 0:
        if len(deliver_queue) > 0:
            single_order = deliver_queue.pop(0)
            Delivery().deliver_pizza(single_order)
            all_order -= 1


if __name__ == '__main__':
    thread1 = Thread(target=start_cooking, args=())
    thread2 = Thread(target=start_delivering, args=())
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    print(Cooking.collection_queue)
