import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Statistics from "./pages/Statistics";
import Profile from "./pages/Profile";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
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
import { createTheme, ThemeProvider } from "@mui/material/styles";


export default function App() {
  const USE_NEW_UI = process.env.REACT_APP_USE_NEW_UI;
  const bgStyle = "mx-auto px-3 py-2" + (!USE_NEW_UI ? " max-w-7xl" : "");
  const theme = createTheme({
    typography: {
      fontFamily: ["Inter", "cursive"].join(","),
    },
  });



  const privateRoutes = (
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
  );

  return (
    <Container fluid className="App bg-buff-50 min-h-screen">
      <ThemeProvider theme={theme}>
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
                      {USE_NEW_UI ? (
                        <Sidebar element={privateRoutes} />
                      ) : (
                        <>
                          <Header />
                          {privateRoutes}
                        </>
                      )}
                    </PrivateRoute>
                  }
                />
              </Routes>
            </UserProvider>
          </ApiProvider>
        </BrowserRouter>
      </ThemeProvider>

    </Container>
  );
}
