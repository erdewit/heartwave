from heartwave.person import Person


class SceneAnalyzer:
    """
    Analyze persons in a scene.
    """
    def __init__(self):
        self.persons = []

    def analyze(self, frame, faces):
        present = set()
        for face in faces:
            x, y, w, h = face
            cx = x + w / 2
            cy = y + h / 2
            person = next(
                (p for p in self.persons if p.contains(cx, cy)), None)
            if person:
                person.setFace(face)
            else:
                person = Person(face)
                self.persons.append(person)
            present.add(person)
        self.persons = [p for p in self.persons if p in present]

        greenIm = frame.image[:, :, 1]
        for person in self.persons:
            person.analyze(frame.time, greenIm)
        return self.persons
