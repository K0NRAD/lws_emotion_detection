import cv2
from cvzone.FaceMeshModule import FaceMeshDetector

cap=cv2.VideoCapture(0)
detector =FaceMeshDetector(maxFaces=2)
while True:
    success, frame = cap.read()
    if not success:
        continue
    #frame = cv2.resize(frame, (800, 600))

    frame, faces = detector.findFaceMesh(frame)
    for face in faces:
        (cx, cy) = face[159]
        cv2.circle(frame, (int(cx), int(cy)), 50, (0, 255, 0), -1)
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
