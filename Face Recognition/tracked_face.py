class TrackedFace:
    currently_tracked = True
    tracker_id = 0

    current_mean_pos = 0

    face_id = ""
    face_name = ""

    def __init__(self, mean_pos, tracker_id):
        self.current_mean_pos = mean_pos