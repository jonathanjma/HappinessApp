import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Statistics from "./pages/Statistics";
import Profile from "./pages/Profile";
import Header from "./components/Header";
import Welcome from "./pages/Welcome";
import Container from "react-bootstrap/Container";
import Settings from "./pages/Settings";
import History from "./pages/History";
import UserGroups from "./pages/UserGroups";
import GroupCopy from "./pages/GroupCopy";
import "./App.css";
import ApiProvider from "./contexts/ApiProvider";
import UserProvider from "./contexts/UserProvider";
import PrivateRoute from "./components/PrivateRoute";
import PublicRoute from "./components/PublicRoute";
import SubmitHappiness from "./pages/SubmitHappiness";

// change id number to id of user in Users.js (temporary until backend + login set up)
export default function App() {
  const id = 1;
  const bgStyle = "max-w-7xl mx-auto min-h-screen px-3 py-2";

  return (
    <Container fluid className="App bg-buff-50">
      <BrowserRouter>
        <ApiProvider>
          <UserProvider>
            <Routes>
              <Route
                path="/"
                element={
                  <PublicRoute>
                    <Welcome />
                  </PublicRoute>
                }
              />
              <Route
                path="*"
                element={
                  <PrivateRoute>
                    <Header user_id={id} />
                    <Routes>
                      <Route path="/home" element={<SubmitHappiness />} />
                      <Route
                        path="/statistics"
                        element={
                          <div className={bgStyle}>
                            <Statistics />{" "}
                          </div>
                        }
                      />
                      <Route
                        path="/profile"
                        element={
                          <div className={bgStyle}>
                            <Profile />
                          </div>
                        }
                      />
                      <Route
                        path="/groups"
                        element={
                          <div className={bgStyle}>
                            <UserGroups />{" "}
                          </div>
                        }
                      />
                      <Route
                        path="/groups/:groupID"
                        element={
                          <div className={bgStyle}>
                            <GroupCopy />
                          </div>
                        }
                      />
                      <Route
                        path="/settings"
                        element={
                          <div className={bgStyle}>
                            <Settings />
                          </div>
                        }
                      />
                      <Route
                        path="/history"
                        element={
                          <div className={bgStyle}>
                            <History />
                          </div>
                        }
                      />

                      <Route path="*" element={<Navigate to="/" />} />
                    </Routes>
                  </PrivateRoute>
                }
              />
            </Routes>
          </UserProvider>
        </ApiProvider>
      </BrowserRouter>
    </Container>
  );
}
