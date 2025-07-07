import { useState } from 'react'
import './App.css'
import React from 'react';
import AuthForm from "./components/AuthForm";

function App() {
  const [userId, setUserId] = useState(localStorage.getItem("user_id"));

  if (!userId) {
    return <AuthForm onLogin={setUserId} />;
  }

  return (
    <div>
      {/* Main app when logged in */}
      <button onClick={() => { localStorage.removeItem("user_id"); setUserId(null); }}>
        Logout
      </button>
      {/* <BookList /> */}
    </div>
  );
}

export default App
