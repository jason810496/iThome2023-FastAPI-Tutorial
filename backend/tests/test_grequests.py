import grequests
import random
import time


USER_AMOUNT = 5000
QUERY_AMOUNT = 10000
UPDATE_AMOUNT = 100

BASE_URL = 'http://localhost:8000'
USERS_ROUTE = '/api/users'


def get_random_page_range_list_url():
    data = []
    for i in range(QUERY_AMOUNT//2):
        l = random.randrange(0,USER_AMOUNT-2)
        r = random.randrange(l+1,USER_AMOUNT-1)

        last = l
        limit = r-l+1

        data.append( f'{BASE_URL}{USERS_ROUTE}?last={last}&limit={limit}' )
        print( f'{BASE_URL}{USERS_ROUTE}?last={last}&limit={limit}' )

    return data

def get_random_user_list_url():
    data = []
    for i in range(QUERY_AMOUNT//2):
        used_id = random.randrange(100,USER_AMOUNT+50)
        data.append( f'{BASE_URL}{USERS_ROUTE}/{used_id}' )
        print( f'{BASE_URL}{USERS_ROUTE}/{used_id}' )

    return data

url_list =  get_random_page_range_list_url() + get_random_user_list_url()

# calculate the time
START = time.time()

rs = [ grequests.get(u) for u in url_list ]
responses = grequests.map(rs)

END = time.time()
# print(response)
# for response in responses:
#     print('response:', response)
#     print('status_code:', response.status_code)
#     print('text:', response.text)

print("\n")
GREEN_COL = '\033[92m'
END_COL = '\033[0m'
print(f'{GREEN_COL} Time : {END-START} {END_COL}')
