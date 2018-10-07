import requests
import openpyxl
import random

def send_user_data_to_server(server_url, post_data):
    r = requests.post(server_url, json=post_data)
    print(r.text)
    print("Data Sent to Server")


def update_users_dictionary(USERS):
    with open("users.txt", "r") as f:
        for line in f:
            foo = line.strip().split(",")
            USERS[foo[0]] = foo[1]

    return USERS