import React, { useState } from 'react';
import '../Permissions.css';

function Permissions({ goToFaceRecognition }) {
  const [cameraAccess, setCameraAccess] = useState(true);
  const [locationAccess, setLocationAccess] = useState(true);

  return (<div>
        <div class="title">Face Recognition</div>
  
  <div class="image-container">
    <div class="viewfinder"></div>
    <div class="success-icon">✓</div>
  </div>
  
  <div class="recognition-text">Face Recognised</div>
  <div class="sub-text">You Have Successfully Signed in as <br/> Bonolo PWD</div>
  
  <a href="#" class="home-button">Home</a>
</div>
  );
}

export default Permissions;