import "./index.css";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Statistics from "./pages/Statistics";
import Profile from "./pages/Profile";
import Home from "./pages/Home";
import Header from "./components/Header";
import Container from "react-bootstrap/Container";

// change id number to id of user in Users.js (temporary until backend + login set up)
function App() {
  const id = 20;
  return (
    <Container fluid className="App bg-rhythm-200">
      <BrowserRouter>
        <Header user_id={id} />
        <div className="max-w-7xl mx-auto min-h-screen px-3 py-2">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/statistics" element={<Statistics id={id} />} />
            <Route path="/profile" element={<Profile id={id} />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </BrowserRouter>
    </Container>
  );
}

export default App;
