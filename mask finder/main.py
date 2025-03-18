import cv2
import numpy as np

def nothing(x):
    pass

# Create a window
cv2.namedWindow('Trackbars')

# Create trackbars for color change
cv2.createTrackbar('LowerH', 'Trackbars', 0, 179, nothing)
cv2.createTrackbar('LowerS', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('LowerV', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('UpperH', 'Trackbars', 179, 179, nothing)
cv2.createTrackbar('UpperS', 'Trackbars', 255, 255, nothing)
cv2.createTrackbar('UpperV', 'Trackbars', 255, 255, nothing)

# Capture video from the default camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

while True:
    # Read the frame
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get the current positions of the trackbars
    lower_h = cv2.getTrackbarPos('LowerH', 'Trackbars')
    lower_s = cv2.getTrackbarPos('LowerS', 'Trackbars')
    lower_v = cv2.getTrackbarPos('LowerV', 'Trackbars')
    upper_h = cv2.getTrackbarPos('UpperH', 'Trackbars')
    upper_s = cv2.getTrackbarPos('UpperS', 'Trackbars')
    upper_v = cv2.getTrackbarPos('UpperV', 'Trackbars')

    # Define the lower and upper HSV range
    lower_color = np.array([lower_h, lower_s, lower_v])
    upper_color = np.array([upper_h, upper_s, upper_v])

    # Create a mask
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Apply the mask to the frame
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Display the original frame, mask, and result
    cv2.imshow('Frame', frame)
    cv2.imshow('Mask', mask)
    cv2.imshow('Result', result)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close the windows
cap.release()
cv2.destroyAllWindows()