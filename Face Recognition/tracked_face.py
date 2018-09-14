class TrackedFace:
    currently_tracked = True
    tracker_id = 0
    captured = False

    current_mean_pos = 0

    face_id = ""
    face_name = ""

    face_attribute_data = None

    identified_at = None

    def __init__(self, mean_pos, tracker_id, identified):
        self.current_mean_pos = mean_pos
        self.tracker_id = tracker_id
        self.identified_at = identified