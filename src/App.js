import "./index.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Statistics from "./pages/Statistics";
import Profile from "./pages/Profile";

// change id number to index of user in Users.js (temporary until backend + login set up)
function App() {
  const id = 1;
  return (
    <BrowserRouter>
      <div className="bg-rhythm-200">
        <div className="max-w-7xl mx-auto min-h-screen px-3 py-2">
          <Routes>
            <Route path="/statistics" element={<Statistics id={id} />} />
            <Route path="/profile" element={<Profile id={id} />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
