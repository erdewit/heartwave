from heartwave.person import Person

from eventkit import Op


class SceneAnalyzer(Op):
    """
    Analyze heartrate for persons in a scene::

        (frame, faces) -> (frame, persons)

    """
    def __init__(self, source=None):
        Op.__init__(self, source)
        self.persons = []

    def on_source(self, frame, faces):
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
        self.emit(frame, self.persons)
