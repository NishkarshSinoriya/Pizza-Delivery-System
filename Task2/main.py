import json
from collections import deque
from operator import itemgetter
import time
from datetime import datetime
import csv
from multiprocessing import Process, Manager

'''
    The potential difficulty I see here is that the chef must wait for the storage to be filled 
    and the oven to become available for cooking.
    
    He must wait until the required materials are no longer available in the storage, 
    and he must keep onto that specific order, which he cannot send out for delivery.
    This causes deadlock in the system.
    
    The delivery person must wait for orders that have been placed on hold due to this deadlock.
    
    Ingredients utilised in an order, orders selected by a chef, and orders delivery given to a driver 
    are all locked/reserved to ensure efficient use of shared resources. Otherwise, it will result in live locking.
    
    If some ingredients are unavailable, the Process() was paused. Concurrent access was handled by doing this.
    
    To avoid live locking, multiprocessing is used to handle concurrent use of the Pizza Oven.
    
    Starvation was avoided in this system by restricting the number of iterations.
    
'''


# Assigning ids to the elements of Ingredients
def add_new_ingredient_queue(que, length):
    for _i in range(1, length):
        if que == dough_queue:
            que.put('D-' + str(time.time()))
        elif que == sauce_queue:
            que.put('S-' + str(time.time()))
        else:
            que.put('T-' + str(time.time()))
    # return que


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


class Order:
    def __init__(self, queue):
        self.queue = queue

    def pick_order(self):
        popped_order = self.queue.get()
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


class Stock:

    # taking ingredients from stock
    @staticmethod
    def taking_ingredient(que, pizza_type):
        pizza_types = ['small', 'medium', 'large']
        used_ingredients = []
        if pizza_type == pizza_types[0]:
            # if que == dough_queue:
            var = Pizza.small_pizza().dough
            for _i in range(0, var):
                used_ingredients.append(que.get())

            # elif que == sauce_queue:
            var = Pizza.small_pizza().sauce
            for _i in range(0, var):
                used_ingredients.append(que.get())

            # elif que == toppings_queue:
            var = Pizza.small_pizza().toppings
            for _i in range(0, var):
                used_ingredients.append(que.get())

        elif pizza_type == pizza_types[1]:
            # if que == dough_queue:
            var = Pizza.medium_pizza().dough
            for _i in range(0, var):
                used_ingredients.append(que.get())

            # elif que == sauce_queue:
            var = Pizza.medium_pizza().sauce
            for _i in range(0, var):
                used_ingredients.append(que.get())

            # elif que == toppings_queue:
            var = Pizza.medium_pizza().toppings
            for _i in range(0, var):
                used_ingredients.append(que.get())

        elif pizza_type == pizza_types[2]:
            # if que == dough_queue:
            var = Pizza.large_pizza().dough
            for _i in range(0, var):
                used_ingredients.append(que.get())

            # elif que == sauce_queue:
            var = Pizza.large_pizza().sauce
            for _i in range(0, var):
                used_ingredients.append(que.get())

            # elif que == toppings_queue:
            var = Pizza.large_pizza().toppings
            for _i in range(0, var):
                used_ingredients.append(que.get())

        return used_ingredients

    @staticmethod
    def refilling_stock(dough_que, sauce_que, toppings_que):
        # Assuming number of dough pieces in one pack are 200
        add_new_ingredient_queue(dough_que, 201)  # generating random numbers to make each dough piece unique
        # Assuming number of sauce servings in one sauce container are 400
        add_new_ingredient_queue(sauce_que, 401)  # generating random numbers to make each sauce serving unique
        # Assuming number of toppings in one topping heap are 100
        add_new_ingredient_queue(toppings_que, 101)  # generating random numbers to make each topping serving unique


class Cooking:

    @staticmethod
    def cooking_pizza(sort_data):
        for __o in sort_data:
            time.sleep(0.01 * (__o['Small_Pizza'] + __o['Medium_Pizza'] + __o['Large_Pizza']))

    @staticmethod
    def preparing_pizza(ord_queue, collection_que, m_lock, dough_que, sauce_que, toppings_que, data_sorted, ):
        pizza_types = ['small', 'medium', 'large']
        o = ord_queue

        for _ in range(ord_queue.qsize()):
            if o.qsize() > 0:
                try:
                    m_lock.acquire()
                    # pick the order to be cooked
                    picked_order = o.get()
                    time_accepted = datetime.now().strftime("%H:%M:%S")
                    small_pizzas = number_of_pizza(picked_order).no_of_small_pizzas()
                    medium_pizzas = number_of_pizza(picked_order).no_of_medium_pizzas()
                    large_pizzas = number_of_pizza(picked_order).no_of_large_pizzas()
                    collection_dictionary = {'Order ID': picked_order[0], 'Time Accepted': time_accepted,
                                             'Number of Small Pizzas': small_pizzas,
                                             'Number of Medium Pizzas': medium_pizzas,
                                             'Number of Large Pizzas': large_pizzas,
                                             'Total Pizzas': small_pizzas + medium_pizzas + large_pizzas,
                                             'IDs for Dough': [], 'IDs for Sauce': [],
                                             'IDs for Toppings': []}

                    # checking stock and preparing pizzas now----->
                    if (dough_que.qsize() >= small_pizzas * Pizza().small_pizza().dough and
                            sauce_que.qsize() >= small_pizzas * Pizza().small_pizza().sauce and
                            toppings_que.qsize() >= small_pizzas * Pizza().small_pizza().toppings):

                        for _i in range(0, small_pizzas):
                            # picking ingredients for small_pizzas **** 2
                            dough_ingredients = Stock().taking_ingredient(dough_que, pizza_types[0])
                            collection_dictionary['IDs for Dough'] += dough_ingredients
                            sauce_ingredients = Stock().taking_ingredient(sauce_que, pizza_types[0])
                            collection_dictionary['IDs for Sauce'] += sauce_ingredients
                            topping_ingredients = Stock().taking_ingredient(toppings_que, pizza_types[0])
                            collection_dictionary['IDs for Toppings'] += topping_ingredients
                            time.sleep(.02)

                    if (dough_que.qsize() >= medium_pizzas * Pizza().medium_pizza().dough and
                            sauce_que.qsize() >= medium_pizzas * Pizza().medium_pizza().sauce and
                            toppings_que.qsize() >= medium_pizzas * Pizza().medium_pizza().toppings):

                        for _i in range(0, medium_pizzas):
                            # picking ingredients for medium_pizzas **** 2
                            dough_ingredients = Stock().taking_ingredient(dough_que, pizza_types[1])
                            collection_dictionary['IDs for Dough'] += dough_ingredients
                            sauce_ingredients = Stock().taking_ingredient(sauce_que, pizza_types[1])
                            collection_dictionary['IDs for Sauce'] += sauce_ingredients
                            topping_ingredients = Stock().taking_ingredient(toppings_que, pizza_types[1])
                            collection_dictionary['IDs for Toppings'] += topping_ingredients
                            time.sleep(.02)

                    if (dough_que.qsize() >= large_pizzas * Pizza().large_pizza().dough and
                            sauce_que.qsize() >= large_pizzas * Pizza().large_pizza().sauce and
                            toppings_que.qsize() >= large_pizzas * Pizza().large_pizza().toppings):

                        for _i in range(0, large_pizzas):
                            # picking ingredients for large_pizzas **** 1
                            dough_ingredients = Stock().taking_ingredient(dough_que, pizza_types[2])
                            collection_dictionary['IDs for Dough'] += dough_ingredients
                            sauce_ingredients = Stock().taking_ingredient(sauce_que, pizza_types[2])
                            collection_dictionary['IDs for Sauce'] += sauce_ingredients

                            # topping_ingredients = Stock().taking_ingredient(toppings_que, pizza_types[2])
                            # collection_dictionary['IDs for Toppings'] += topping_ingredients
                            time.sleep(.02)

                    Cooking.cooking_pizza(data_sorted)
                    collection_que.append(collection_dictionary)
                    collection_que.sort(key=itemgetter('Total Pizzas'), reverse=True)

                except IndexError:
                    pass

                finally:
                    m_lock.release()
            else:
                break


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


def start_cooking(o_queue, c_queue, processor_lock, d_queue, s_queue, t_queue, sorted__data, ):
    Cooking().preparing_pizza(o_queue, c_queue, processor_lock, d_queue, s_queue, t_queue, sorted__data, )


def start_delivering(deliver_queue, processor_lock, sorted__data):
    all_order = len(sorted__data)
    timer = 0
    while all_order != 0:
        try:
            processor_lock.acquire()
            if len(deliver_queue) > 0 and all_order > 0:
                single_order = deliver_queue.pop(0)
                Delivery().deliver_pizza(single_order)
                all_order -= 1
            if True:
                if timer == 50:
                    break
                else:
                    # print(timer)
                    timer += 1
        finally:
            processor_lock.release()


if __name__ == '__main__':
    manager = Manager()
    lock = Manager().Lock()

    # opening, loading and sorting json file in desired order
    f = open('orders.json')
    data = json.load(f)
    sorted_data = sorted(data, key=lambda k: k['Order_ID'])
    f.close()

    # making desired dictionary from data to make an order queue out of it
    order_dictionary = {}
    for i in range(0, len(sorted_data)):
        order_dictionary[sorted_data[i]['Order_ID']] = [sorted_data[i]['Order_ID'], sorted_data[i]['Small_Pizza'],
                                                        sorted_data[i]['Medium_Pizza'], sorted_data[i]['Large_Pizza']]

    order_queue = manager.Queue()
    # pushing dictionary to form an order queue
    for i in order_dictionary:
        order_queue.put(order_dictionary[i])

    # Empty dough, sauce and toppings queues
    dough_queue = manager.Queue()
    sauce_queue = manager.Queue()
    toppings_queue = manager.Queue()

    # Stocking the stock for the very first time
    Stock().refilling_stock(dough_queue, sauce_queue, toppings_queue)

    collection_queue = manager.list()

    no_of_chef = int(input('Give number of chefs at work today'))
    no_of_driver = int(input('Give number of drivers at work today'))

    processes = []
    for _ in range(no_of_chef):
        process = Process(target=start_cooking, args=(order_queue, collection_queue, lock,
                                                      dough_queue, sauce_queue, toppings_queue, sorted_data,))
        processes.append(process)
    for _ in range(no_of_driver):
        process = Process(target=start_delivering, args=(collection_queue, lock, sorted_data,))
        processes.append(process)

    for process in processes:
        process.start()

    for process in processes:
        process.join()
