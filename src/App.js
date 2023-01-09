import "./index.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Statistics from "./pages/Statistics";
import Profile from "./pages/Profile";
import { useState } from "react";

function App() {
  return (
    <BrowserRouter>
      <div className="bg-blue-200">
        <div className="max-w-4xl mx-auto min-h-screen px-3 py-2">
          <Routes>
            <Route path="/statistics" element={<Statistics />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
