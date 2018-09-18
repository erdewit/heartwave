from heartwave.person import Person
from heartwave.runner import Runner


class SceneAnalyzer(Runner):
    """
    Processing stage to locate and analyze persons in a scene.

    Input: (frame, faces)
    Output: (frame, faces, persons)
    """
    def run(self):
        persons = []
        while self.running:
            tup = self.getInput()
            if tup is Runner.Stop:
                break
            frame, faces = tup

            present = set()
            for face in faces:
                x, y, w, h = face
                cx = x + w / 2
                cy = y + h / 2
                person = next(
                    (p for p in persons if p.contains(cx, cy)), None)
                if person:
                    person.setFace(face)
                else:
                    person = Person(face)
                    persons.append(person)
                present.add(person)
            persons = [p for p in persons if p in present]

            greenIm = frame.image[:, :, 1]
            for person in persons:
                person.analyze(frame.time, greenIm)

            self.output((frame, faces, persons))
