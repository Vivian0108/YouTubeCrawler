/*
 * http://docs.opencv.org/3.3.0/db/d28/tutorial_cascade_classifier.html
 * http://docs.opencv.org/3.3.0/d5/dc4/tutorial_video_input_psnr_ssim.html
 */

#include <iostream>
#include <string>
#include <sstream>

#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/objdetect.hpp>
#include <opencv2/imgproc.hpp>

using namespace std;
using namespace cv;

int detect(
    Mat frame, 
    CascadeClassifier frontalCascade, 
    CascadeClassifier profileCascade
) {
  vector<Rect> faces;
  int width = frame.cols;
  int height = frame.rows;
  int targetWidth = 1000;
  int modHeight = (int)((double) targetWidth / width * height);
  int numFaces = 0;
  Mat resizedFrame;
  Mat flippedFrame;
  resize(frame, resizedFrame, Size(targetWidth, modHeight));
  flip(resizedFrame, flippedFrame, 1);
  profileCascade.detectMultiScale(
    resizedFrame,
    faces,
    1.2,
    4,
    0|CASCADE_SCALE_IMAGE,
    Size(30, 30)
  );
  numFaces += faces.size();
  profileCascade.detectMultiScale(
    flippedFrame,
    faces,
    1.2,
    4,
    0|CASCADE_SCALE_IMAGE,
    Size(30, 30)
  );
  numFaces += faces.size();
  frontalCascade.detectMultiScale(
    resizedFrame,
    faces,
    1.2,
    4,
    0|CASCADE_SCALE_IMAGE,
    Size(30, 30)
  );
  numFaces += faces.size();
  return numFaces;
}

int main(int argc, char *argv[]) {
  if (!(argc >= 2)) {
    cout << "filename is required, all other params are optional\n"
         << "<filename> [mosi/sqa] [percent] [early] [perNFrames]\n" 
         << "Defaults:   sqa        0         0       1" << endl;
    return -1;
  }

  const string videoSource = argv[1];
  string type = "sqa";
  if (argc >= 3) {
    type = argv[2];
  }
  int percent = 0;
  if (argc >= 4) {
    percent = stoi(argv[3]);
  }
  int early = 0;
  if (argc >= 5) {
    early = stoi(argv[4]);
  }
  int perNFrames = 1;
  if (argc >= 6) {
    perNFrames = stoi(argv[5]);
  }
  const string frontalXML = "/home/edmundtemp/sqa/crawler/haarcascade_frontalface_alt.xml";
  const string profileXML = "/home/edmundtemp/sqa/crawler/lbpcascade_profileface.xml";

  CascadeClassifier frontalCascade;
  if (!frontalCascade.load(frontalXML)) {
    cout << "Error loading frontal cascade file" << endl;
    return -1;
  }
  CascadeClassifier profileCascade;
  if (!profileCascade.load(profileXML)) {
    cout << "Error loading profile cascade file" << endl;
    return -1;
  }

  cv::VideoCapture cap(videoSource);
  if (!cap.isOpened()) {
    cout << "Could not open " << videoSource << endl;
    return -1;
  }

  Mat frame;

  int totalFrames = (int) cap.get(CV_CAP_PROP_FRAME_COUNT) / perNFrames;
  int framesWFaces = 0;
  int framesSeen = 0;

  if (early) {
    // Adding one to ensure that truncating does not stop the detection
    // too early
    int framesToStop = int((1 - (double) percent / 100) * framesToStop) + 1;
    while (cap.read(frame)) {
      if (framesSeen % perNFrames == 0) {
        framesWFaces += detect(frame, frontalCascade, profileCascade) > 0;
      }
      if (framesSeen - framesWFaces >= framesToStop) {
        cout << "-1" << endl;
        return 0;
      }
    }
  } else {
    while (cap.read(frame)) {
      framesSeen++;
      if (framesSeen % perNFrames == 0) {
        framesWFaces += detect(frame, frontalCascade, profileCascade) > 0;
      }
    }
  }
  int truePercentage = (int)(framesWFaces / (double) totalFrames * 100);
  cout << truePercentage << endl;
  return 0;
}
