import requests
import openpyxl
import random

def send_user_data_to_server(server_url, post_data):
    r = requests.post(server_url, data=post_data)


def update_users_dictionary(USERS):
    with open("faces.txt", "r") as f:
        for line in f:
            foo = line.strip().split(",")
            USERS[foo[0]] = foo[1]

    return USERS


def identify_tracked_face():
    return 0

def rect_mean_pos(x, y, w, h) -> (float, float):
    return ((x+(w/2)),(y+(h/2)))


def tracker_id_generator(prev):
    r = random.random()
    while r in prev:
        r = random.random()
    return r


def find_closest(number, list):
    curr_closest = -1

    for num in list:
        if abs(number - num) < abs(number-curr_closest):
            curr_closest = num

    return (curr_closest)

def update_face_tracker(old_pos, mean_pos, trackers):
    id = find_face_tracker_with_pos(old_pos, trackers)
    trackers[id].current_mean_pos = mean_pos
    trackers[id].currently_tracked = True
    return trackers

def find_face_tracker_with_pos(old_pos, trackers):
    for i in range(len(trackers)):
        _x, _y = trackers[i].current_mean_pos
        _m = (_x ** 2 + _y ** 2) ** (1/2)
        if old_pos == _m:
            return i