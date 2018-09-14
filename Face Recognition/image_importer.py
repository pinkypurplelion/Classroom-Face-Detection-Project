import cognitive_face as CF
import os
import time
# from functions import update_users_dictionary


KEY = '4b2ad21af4a146269f6386ef6fe0f644'  # Replace with a valid subscription key (keeping the quotes in place).
CF.Key.set(KEY)

BASE_URL = 'https://australiaeast.api.cognitive.microsoft.com/face/v1.0'  # Replace with your regional Base URL
CF.BaseUrl.set(BASE_URL)


def add_user_to_face_list(user_image_path: str, face_list: str, user_name: str) -> str:
    print("Adding New User to Detection List")

    perm_id = CF.face_list.add_face(user_image_path, face_list)
    perm_id = perm_id['persistedFaceId']

    print("New User Added to Detection List:",face_list,"User Permanent ID is:", perm_id)

    print("Adding User to USERS List")
    with open("faces.txt", "a") as f:
        print(perm_id+","+user_name, file=f)

    print("User Successfully Added to USERS List")

    # print("Updating Dictionary")
    # update_users_dictionary(USERS)
    # print("Dictionary Updated")

    return perm_id

add_user_to_face_list("faces/" + "langus1.jpg", "secstudents", "langus")

faces = os.listdir("faces")

# CF.face_list.create("secstudents", "St Eugene College Students")

# for face in faces:
#     u = face.split(".")
#     user_id = u[0]
#     print(face, user_id)
#     print(add_user_to_face_list("faces/" + face, "secstudents", user_id))
#     time.sleep(4)

