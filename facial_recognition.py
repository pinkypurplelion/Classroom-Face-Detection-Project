from threading import Timer
import _thread
import cv2
import cognitive_face as CF
import json

USERS = {}

def update_users_dictionary():
    global USERS

    with open("users.txt", "r") as f:
        for line in f:
            foo = line.strip().split(",")
            USERS[foo[0]] = foo[1]

    print(USERS)

update_users_dictionary()


FACE_USER = ""
FACE_CONFIDENCE = 0
FACE_ACCEPTED = False

KEY = '4b2ad21af4a146269f6386ef6fe0f644'  # Replace with a valid subscription key (keeping the quotes in place).
CF.Key.set(KEY)

BASE_URL = 'https://australiaeast.api.cognitive.microsoft.com/face/v1.0'  # Replace with your regional Base URL
CF.BaseUrl.set(BASE_URL)

cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)

video_capture = cv2.VideoCapture(0)

saved_faces = 0
saved = False
running = False


def add_face_to_list(image_location, face_list):
    return CF.face_list.add_face(image_location, face_list)


def save_face():
    global saved, saved_faces, frame
    img_location = "face_"+str(saved_faces)+".jpg"
    cv2.imwrite(img_location, frame)
    print("Image Saved")

    _thread.start_new_thread(process_image_with_azure, tuple([img_location, "detected_faces"]))
    #_thread.start_new_thread(add_user_to_face_list, tuple(["eperak.jpg", "detected_faces", "Ema Perak"]))

    saved_faces += 1
    saved = True


def process_image_with_azure(image_path: str, face_list: str):
    print("Processing Image")
    data = find_similar_face(image_path, face_list)

    print("Similar Faces Data:",data)

    results = process_similar_face_data(data)
    print(results)

    if results[3] == True:
        print("Welcome",USERS[results[2]])

    #CF.face_list.delete_face("detected_faces", "15b83ffe-6244-424f-808f-1779d018c5da")
    #print(CF.face_list.add_face('face_0.jpg', 'detected_faces'))
    #CF.face_list.create("detected_faces", "Detected Faces")


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


def find_similar_face(image_path: str, face_list: str) -> list:
    print("Detecting Similar Faces Using Microsoft Azure")

    return_data = CF.face.detect(image_path)
    face_id = return_data[0]['faceId']
    print("Face Detected. Face ID: "+str(face_id))

    similar_faces = CF.face.find_similars(face_id, face_list)
    print("Similar Faces Found")

    return similar_faces


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
    update_users_dictionary()
    print("Dictionary Updated")

    return perm_id

while True:
    global frame
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    drawn_frame = frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(drawn_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(drawn_frame, "Welcome "+FACE_USER, (20, 400), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

    if len(faces) == 1:
        if not running:
            saved = False
            print("Saving Image in 3 Seconds")
            running = True
            t = Timer(3.0, save_face)
            t.start()

    if len(faces) != 1:
        if running:
            print("Timer Cancelled. Face Saved: "+str(saved))
            t.cancel()
            running = False

    # Display the resulting frame
    cv2.imshow('Webcam Authentication System', drawn_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()