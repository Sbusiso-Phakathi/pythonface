import React, { useState } from 'react';
import Home from './components/Home';
import Permissions from './components/Permissions';
import FaceRecognition from './components/FaceRecognition';
import './App.css';

function App() {
  const [screen, setScreen] = useState('home');

  const goToScreen = (screenName) => {
    setScreen(screenName);
  };

  return (
    <div className="App">
      {screen === 'home' && <Home goToPermissions={() => goToScreen('permissions')} />}
      {screen === 'permissions' && <Permissions goToFaceRecognition={() => goToScreen('faceRecognition')} />}
      {screen === 'faceRecognition' && <FaceRecognition />}
    </div>
  );
}

export default App;
