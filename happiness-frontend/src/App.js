import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Statistics from "./pages/Statistics";
import Profile from "./pages/Profile";
import Header from "./components/Header";
import Welcome from "./pages/Welcome";
import Container from "react-bootstrap/Container";
import Settings from "./pages/Settings";
import History from "./pages/History";
import UserGroups from "./pages/UserGroups";
import Group from "./pages/Group";
import "./App.css";
import ApiProvider from "./contexts/ApiProvider";
import UserProvider from "./contexts/UserProvider";
import PrivateRoute from "./components/PrivateRoute";
import PublicRoute from "./components/PublicRoute";
import SubmitHappiness from "./pages/SubmitHappiness";
import RequestResetPassword from "./pages/authentication/RequestResetPassword";
import ResetPassword from "./pages/authentication/ResetPassword";
import ImagePicker from "./components/ImagePicker";

export default function App() {
  const bgStyle = "max-w-7xl mx-auto px-3 py-2";

  return (
    <Container fluid className="App bg-buff-50 min-h-screen">
      <BrowserRouter>
        <ApiProvider>
          <UserProvider>
            <Routes>
              <Route
                path="/"
                element={
                  <PublicRoute>
                    <ImagePicker />
                  </PublicRoute>
                }
              />
              <Route
                path="/reset-pass"
                element={
                  <PublicRoute>
                    <RequestResetPassword newPassword={false} />
                  </PublicRoute>
                }
              />
              <Route
                path="/reset-pass/change-pass/:token"
                element={
                  <PublicRoute>
                    <ResetPassword newPassword={true} />
                  </PublicRoute>
                }
              />
              <Route
                path="*"
                element={
                  <PrivateRoute>
                    <Header />
                    <Routes>
                      <Route path="/home" element={<SubmitHappiness />} />
                      <Route
                        path="/statistics"
                        element={
                          <div className={bgStyle}>
                            <Statistics />
                          </div>
                        }
                      />
                      <Route
                        path="/profile/:userID"
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
                            <UserGroups />
                          </div>
                        }
                      />
                      <Route
                        path="/groups/:groupID"
                        element={
                          <div className={bgStyle}>
                            <Group />
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
                        path="/history/:userID"
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
