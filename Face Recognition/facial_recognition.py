from functions import send_user_data_to_server, update_users_dictionary
from datetime import datetime
import _thread
import cv2
import cognitive_face as CF
import os
import copy
from pyimagesearch.centroidtracker import CentroidTracker


USERS = {}
USER_DATA_POST_URL = "http://192.168.0.55:3002/post/user/identified"
LOCATION_ID = "GH6JK30L"


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
video_capture = cv2.VideoCapture(0)

saved_faces = 0
saved = False
running = False


USERS = update_users_dictionary(USERS)


TRACKED_FACES = [] #{objectID: xxxx, personName: xxxx, personID: xxxx}
TRACKED_OBJECTS = []


def add_face_to_lists(image_location, face_list):
    return CF.face_list.add_face(image_location, face_list)


def save_face(face_tracker_id, x, y):
    global saved, saved_faces, frame

    sub_face = frame[y-150:y+150, x-150:x+150]
    img_location = os.path.join("images", "face_" + str(face_tracker_id) + ".jpg")
    cv2.imwrite(img_location, sub_face)

    print("Image Saved:",face_tracker_id)

    # FACE-GROUP: secstudents
    _thread.start_new_thread(process_image_with_azure, tuple([img_location, "detected_faces", face_tracker_id]))
    #_thread.start_new_thread(add_user_to_face_list, tuple(["images\grandad_cropped.jpg", "detected_faces", "John Angus"]))


    saved_faces += 1
    saved = True


def process_image_with_azure(image_path: str, face_list: str, face_tracker_id: int):
    print("Processing Image")
    data, face_attributes = find_similar_face(image_path, face_list)

    print("Similar Faces Data:",data)
    print("Face Attribute Data:",face_attributes)



    results = process_similar_face_data(data)
    print(results)

    # print("RESULTS",results)
    if results[3] == True:
        print("Welcome",USERS[results[2]])

    print("DEBUG: process_image_with_azure")

    TRACKED_FACES.append({"objectID": face_tracker_id, "personName": USERS[results[2]], "personID": results[2]})
    print(TRACKED_FACES)

    payload = {"userID": results[2],
               "locationID": "GH6JK30L",
               "timestamp": str(datetime.now()),
               "faceAttributes":face_attributes}

    send_user_data_to_server(USER_DATA_POST_URL, payload)

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

num_faces = 0
ct = CentroidTracker()

while True:
    global frame, _x, _y, _w, _h
    font = cv2.FONT_HERSHEY_SIMPLEX
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    drawn_frame = copy.copy(frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(100, 100)
    )

    rects = []

    for face in faces:
        x,y,w,h = face
        rect = copy.copy(face)
        rect[2] = rect[2] + rect[0]
        rect[3] = rect[3] + rect[1]
        cv2.rectangle(drawn_frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        rects.append(rect)

    objects = ct.update(rects)

    for (objectID, centroid) in objects.items():
        # print(centroid)
        _name = "UNKNOWN"
        for face in TRACKED_FACES:
            if face['objectID'] == objectID:
                _name = face['personName']

        text = str(objectID) + ': ' + _name
        cv2.putText(drawn_frame, text, (centroid[0] - 10, centroid[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(drawn_frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

        if objectID not in TRACKED_OBJECTS:
            TRACKED_OBJECTS.append(objectID)
            _thread.start_new_thread(save_face, tuple([objectID, centroid[0], centroid[1]]))


    # Display the resulting frame
    cv2.imshow('Face Detection', drawn_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
