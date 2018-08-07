import _thread
import requests

SERVER_URL = "http://192.168.0.55:3000/"


def send_user_data_to_server(server_url, post_data):
    r = requests.post(server_url, data=post_data)


def main():
    send_user_data_to_server(SERVER_URL, {"name":"liam", "age":16})

if __name__ == '__main__':
    main()