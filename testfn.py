import pandas as pd
import json

my_list = [{'id':1,'name':'alic'},
           {'id':2,'name':'bob'},]
my_df = pd.DataFrame(my_list)
print(my_df)

inventory = '''{
    "warehouse_1": {"apples": 30, "oranges": 20, "pears": 15},
    "warehouse_2": {"apples": 25, "oranges": 30, "pears": 5, "bananas": 50},
    "warehouse_3": {"apples": 40, "bananas": 60}
}
'''

inventory = json.loads(inventory)
inventory = pd.DataFrame(inventory)
print(inventory)