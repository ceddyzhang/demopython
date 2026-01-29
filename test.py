import pandas as pd

test_list = [{'name': 'a', 'id': 1}, {'name': 'b', 'id': 2}, {'name': 'c', 'id': 3}]

test_df = pd.DataFrame(test_list)

print(test_df)

"""
users_pages = [{'user_id': 1, 'page_id': [21, 25]},{'user_id': 2, 'page_id': [25,23,24]}]
users_pages_df = pd.DataFrame(users_pages).explode('page_id').reset_index(drop=True)#.astype({'page_id':'Int64'})

#print(users_pages_df)

users_friends = [{'user_id': 1, 'friend_id': [2, 4,5]},{'user_id': 2, 'friend_id': [1,3]}]
users_friends_df = pd.DataFrame(users_friends).explode(['friend_id']).reset_index().astype({'friend_id':'Int64'})[['user_id','friend_id']]
#print(users_friends_df)
#print(users_friends_df.dtypes)

#print(users_friends_df.explode('friend_id').reset_index())

users_pages_df = users_pages_df.sort_values(by=['user_id'],ascending=[True])

users_pages_summary_df = users_pages_df.astype({'page_id': str}).groupby(by=['user_id']).agg(','.join).reset_index()
users_pages_summary_df = users_pages_summary_df.rename(columns={'page_id':'page_id_summary'})
#print(users_pages_summary_df)

users_friends_pages_df = pd.merge(users_friends_df,users_pages_df,how='left',left_on='friend_id',right_on='user_id')
users_friends_pages_df = users_friends_pages_df.drop(columns=['user_id_y']).rename(columns={'user_id_x':'user_id'})
users_friends_pages_df = users_friends_pages_df.rename(columns={'page_id':'friend_page_id'})
#print(users_friends_pages_df)

final_df = pd.merge(users_pages_summary_df,users_friends_pages_df,how='left',left_on='user_id',right_on='user_id')
def check_page_in_user_pages(row):
    return row['page_id_summary'].find(str(row['friend_page_id']))  >0


final_df['friend_page_id_in_user_pages'] = final_df.apply(check_page_in_user_pages,axis=1)
#print(final_df)
"""

###window function partition by order by
"""
my_df = pd.DataFrame({'department_id':['a','a','a','b','b','c'],
    'user_id': [1, 5, 3, 2, 4, 6],
        'score': [10, 20, 15, 10, 30, 25]})
my_df['next_score'] = my_df.sort_values(by=['department_id','user_id']).groupby(by=['department_id'])['score'].shift(-1)
my_df = my_df.sort_values(by=['department_id','user_id'])

#print(my_df)
"""

###window function rolling average
my_df = pd.DataFrame({'users':[1,1,1,1,1,2,2,2,3,3,3,3,4,],'values': [10, 15, 20, 25, 30, 35, 40, 45, 50, 55,pd.NA,10,1]}).sort_values(by=['users'])
my_df = my_df.astype({'values':'Int64'}) #without this type cast, numeric aggregation will fail with NaN values
#print(my_df)

my_df['past_3d_avg'] = my_df.groupby(by=['users'])['values'].rolling(window=3,min_periods=1,center=False).mean().reset_index(drop=True)
my_df['running_sum']=my_df.groupby(by=['users'])['values'].cumsum().reset_index(drop=True)
my_df['value_rank'] = my_df.sort_values(by=['values'],ascending=[False]).groupby(by=['users'])['values'].rank().reset_index(drop=True)
print(my_df)