import {BrowserRouter, Navigate, Route, Routes} from "react-router-dom";
import Statistics from "./pages/Statistics";
import Profile from "./pages/Profile";
import Header from "./components/Header";
import Welcome from "./pages/Welcome";
import Container from "react-bootstrap/Container";
import Settings from "./pages/Settings";
import Home from "./pages/Home";
import {useState} from "react";
import History from "./pages/History";
import UserGroups from "./pages/UserGroups";
import Group from "./pages/Group";
import "./App.css";

// change id number to id of user in Users.js (temporary until backend + login set up)
export default function App() {
  const id = 1;
  //TODO this is a placeholder with basic functionality, we will have to rewrite after backend implementation.
  const [isLoggedIn, setIsLoggedIn] = useState(true);

  return (
    <>
      {!isLoggedIn ? (
        <Welcome setIsLoggedIn={setIsLoggedIn} />
      ) : (
        <Container fluid className="App bg-buff-50">
          <BrowserRouter>
            <Header user_id={id} />
            <div className="max-w-7xl mx-auto min-h-screen px-3 py-2">
              <Routes>
                <Route path="/" element={<Home logged_in={isLoggedIn} />} />
                <Route path="/statistics" element={<Statistics id={id} />} />
                <Route path="/profile" element={<Profile id={id} />} />
                <Route path="/groups" element={<UserGroups id={id} />} />
                <Route path="/groups/:groupID" element={<Group id={id} />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/history" element={<History id={id} />} />
                <Route path="*" element={<Navigate to="/" />} />
              </Routes>
            </div>
          </BrowserRouter>
        </Container>
      )}
    </>
  );
}
