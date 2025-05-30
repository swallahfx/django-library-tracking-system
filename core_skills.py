import random

rand_list = [random.randint(1,20) for i in range(10)]

list_comprehension_below_10 = [i for i in rand_list if i < 10]

list_comprehension_below_10 = list(filter(lambda i: i < 10, rand_list))