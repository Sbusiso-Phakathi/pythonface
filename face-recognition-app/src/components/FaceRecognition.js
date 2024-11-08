import React from 'react';
import '../Permissions.css';
import placeholderImage from '../assets/face.png';
import cameraIcon from '../assets/camera.png';

function FaceRecognition() {
  const handleCapture = () => {
    // Add logic to handle image capture if connected to a real camera or API
    console.log('Capture button clicked');
  };

  return (
    <div className="face-recognition-container">
      <h2>Face Recognition</h2>
      <div className="image-container">
        <img src={placeholderImage} alt="Face Recognition" />
        <div className="face-frame"></div>
      </div>
      <p>Hold your head still for at least 10 seconds to get accurate face recognition.</p>
      <button className="capture-button" onClick={handleCapture}>
        <img src={cameraIcon} alt="Capture Icon"  height={30}/>
        Capture
      </button>
    </div>
  );
}

export default FaceRecognition;
