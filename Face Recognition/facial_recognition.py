from threading import Timer
from functions import send_user_data_to_server, update_users_dictionary, tracker_id_generator, rect_mean_pos, find_closest, update_face_tracker, find_tracker_with_id
import _thread
import cv2
import cognitive_face as CF
import json
import requests
import os
from tracked_face import TrackedFace
import time
import copy


GENERATED_TRACKER_IDS = []

box_expander = 50
USERS = {}
SEVER_URL = "http://localhost:3000/"


FACE_USER = ""
FACE_CONFIDENCE = 0
FACE_ACCEPTED = False

KEY = '4b2ad21af4a146269f6386ef6fe0f644'  # Replace with a valid subscription key (keeping the quotes in place).
CF.Key.set(KEY)

BASE_URL = 'https://australiaeast.api.cognitive.microsoft.com/face/v1.0'  # Replace with your regional Base URL
CF.BaseUrl.set(BASE_URL)

cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
# "videos/multi_face_test_video.mp4"
video_capture = cv2.VideoCapture("videos/multi_face_test_video.mp4")

saved_faces = 0
saved = False
running = False


USERS = update_users_dictionary(USERS)


TRACKED_FACES = []



def add_face_to_lists(image_location, face_list):
    return CF.face_list.add_face(image_location, face_list)


def save_face(face_tracker_id, x, y):
    global saved, saved_faces, frame

    sub_face = frame[y-300:y+300, x-300:x+300]
    img_location = os.path.join("images", "face_" + str(face_tracker_id) + ".jpg")
    cv2.imwrite(img_location, sub_face)

    print("Image Saved:",face_tracker_id)

    _thread.start_new_thread(process_image_with_azure, tuple([img_location, "secstudents", face_tracker_id]))
    #_thread.start_new_thread(add_user_to_face_list, tuple(["images\grandad_cropped.jpg", "detected_faces", "John Angus"]))


    saved_faces += 1
    saved = True


def process_image_with_azure(image_path: str, face_list: str, face_tracker_id: float):
    print("Processing Image")
    data, face_attributes = find_similar_face(image_path, face_list)

    print("Similar Faces Data:",data)
    print("Face Attribute Data:",face_attributes)


    results = process_similar_face_data(data)
    print(results)

    tracked_face = TRACKED_FACES[find_tracker_with_id(face_tracker_id, TRACKED_FACES)]
    tracked_face.face_attribute_data = face_attributes
    tracked_face.face_id = results[2]
    if len(results[2]) != 0:
        tracked_face.face_name = USERS[results[2]]

    # print("RESULTS",results)
    if results[3] == True:
        print("Welcome",USERS[results[2]])

    print("DEBUG: process_image_with_azure")
    #send_user_data_to_server(SEVER_URL, {"user":USERS[results[2]], "userID":results[2], "faceAttributes":face_attributes})

    #CF.face_list.delete_face("detected_faces", "15b83ffe-6244-424f-808f-1779d018c5da")
    #print(CF.face_list.add_face('face_0.jpg', 'detected_faces'))
    #CF.face_list.create("detected_faces", "Detected Faces")

def find_similar_face(image_path: str, face_list: str) -> list:
    print("Detecting Similar Faces Using Microsoft Azure")

    return_data = CF.face.detect(image_path, attributes="age,gender,headPose,smile,facialHair,glasses,emotion,makeup,accessories")
    # print(return_data)
    face_id = return_data[0]['faceId']
    face_attributes = return_data[0]['faceAttributes']
    print("Face Detected. Face ID: "+str(face_id))
    # print(face_attributes)

    similar_faces = CF.face.find_similars(face_id, face_list)
    print("Similar Faces Found")

    return similar_faces, face_attributes

def process_similar_face_data(similar_faces_data: list) -> list:
    global FACE_ACCEPTED, FACE_CONFIDENCE, FACE_USER
    confidence = 0.0
    persistedID = ""

    if len(similar_faces_data) >= 1:
        confidence = similar_faces_data[0]["confidence"]
        persistedID = similar_faces_data[0]["persistedFaceId"]

        FACE_ACCEPTED = True
        FACE_USER = USERS[persistedID]
        FACE_CONFIDENCE = confidence

        return ["Face Has Been Detected", confidence, persistedID, True]
    else:
        return ["Face Has Not Been Detected", confidence, persistedID, False]



def add_user_to_face_list(user_image_path: str, face_list: str, user_name: str) -> str:
    print("Adding New User to Detection List")

    perm_id = CF.face_list.add_face(user_image_path, face_list)
    perm_id = perm_id['persistedFaceId']

    print("New User Added to Detection List:",face_list,"User Permanent ID is:", perm_id)

    print("Adding User to USERS List")
    with open("users.txt", "a") as f:
        print(perm_id+","+user_name, file=f)

    print("User Successfully Added to USERS List")

    print("Updating Dictionary")
    update_users_dictionary(USERS)
    print("Dictionary Updated")

    return perm_id


while True:
    for face in TRACKED_FACES:
        face.currently_tracked = False


    global frame, _x, _y, _w, _h
    font = cv2.FONT_HERSHEY_SIMPLEX
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    drawn_frame = copy.copy(frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(100, 100)
    )


    # Draw a rectangle around the faces
    if len(TRACKED_FACES) == 0:
        for (x, y, w, h) in faces:
            cv2.rectangle(drawn_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            _x, _y, _w, _h = faces[0][0], faces[0][1], faces[0][2], faces[0][3]
            t_id = tracker_id_generator(GENERATED_TRACKER_IDS)
            # print("TRACKER ID:",t_id)
            face_track = TrackedFace(rect_mean_pos(x, y, w, h), t_id, time.time())
            print("t_id:",face_track.tracker_id)
            TRACKED_FACES.append(face_track)
            print(TRACKED_FACES)
            _mx, _my = face_track.current_mean_pos
            cv2.line(drawn_frame, (int(_mx), int(_my)), (int(_mx), int(_my)), (255, 255, 255), 5)
    else:
        for (x, y, w, h) in faces:
            cv2.rectangle(drawn_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            _x, _y, _w, _h = faces[0][0], faces[0][1], faces[0][2], faces[0][3]

    new_mean_pos = []
    for (x,y,w,h) in faces:
        face_mean = rect_mean_pos(x,y,w,h)
        new_mean_pos.append(face_mean)

    old_face_pos = []
    for face in TRACKED_FACES:
        old_pos = face.current_mean_pos
        old_face_pos.append([old_pos, face.tracker_id])

    # print(new_mean_pos, old_face_pos)

    _dma = []
    for p in old_face_pos:
        _dx, _dy = p[0]
        _dm = (_dx ** 2 + _dy ** 2) ** (1 / 2)
        _dma.append(_dm)

    for pos in new_mean_pos:
        _fx, _fy = pos
        _fm = (_fx ** 2 + _fy ** 2) ** (1/2)
        # print("_fm: ", _fm)

        # print("_dma", _dma)
        x = find_closest(_fm, _dma)
        # print("X BEFORE REMOVAL: ", x)
        if x != -1:
            _dma.remove(x)
            TRACKED_FACES = update_face_tracker(x, pos, TRACKED_FACES)


    for face in TRACKED_FACES:
        _mx, _my = face.current_mean_pos
        _mx, _my = int(_mx), int(_my)

        cv2.line(drawn_frame, (_mx, _my), (_mx, _my), (64, 128, 96), 10)
        cv2.putText(drawn_frame, str(face.face_name), (_mx, _my-100), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
        if time.time() - face.identified_at >= 3 and face.captured == False:
            print("3 Seconds elapsed, capturing and identifying face.")
            face.captured = True
            save_face(face.tracker_id, _mx, _my)



    for face in TRACKED_FACES:
        if face.currently_tracked == False:
            TRACKED_FACES.remove(face)



    # if len(faces) == 1:
    #     if not running:
    #         saved = False
    #         print("Saving Image in 1 Seconds")
    #         running = True
    #         t = Timer(1.0, save_face)
    #         t.start()
    #
    # if len(faces) != 1:
    #     if running:
    #         print("Timer Cancelled. Face Saved: "+str(saved))
    #         t.cancel()
    #         running = False

    # Display the resulting frame
    cv2.imshow('Face Detection', drawn_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
