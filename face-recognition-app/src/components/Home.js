import React from 'react';
import '../Home.css';

function Home({ goToPermissions }) {
  return (
    <div className="home-container">
      <div className="logo">Shaper</div>
      <div className="subtitle">POWERED BY THE DIGITAL ACADEMY</div>
      <button className="start-button" onClick={goToPermissions}>Get Started</button>
    </div>
  );
}

export default Home;
