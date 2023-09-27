import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Statistics from "./pages/Statistics";
import Profile from "./pages/Profile";
import Sidebar from "./components/Sidebar";
import Welcome from "./pages/authentication/Welcome";
import Container from "react-bootstrap/Container";
import Settings from "./pages/Settings";
import History from "./pages/History";
import Group from "./pages/groups";
import "./App.css";
import ApiProvider from "./contexts/ApiProvider";
import UserProvider from "./contexts/UserProvider";
import PrivateRoute from "./components/PrivateRoute";
import PublicRoute from "./components/PublicRoute";
import RequestResetPassword from "./pages/authentication/RequestResetPassword";
import ResetPassword from "./pages/authentication/ResetPassword";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import NewUserGroups from "./pages/NewUserGroups";
import { StyledEngineProvider } from "@mui/material";
import Entries from "./pages/happiness/CommentHeader";

export default function App() {
  const bgStyle =
    "mx-auto mt-5 mb-3 ms-4 me-4  max-w-7xl";
  const theme = createTheme({
    typography: {
      fontFamily: ["Inter", "cursive"].join(","),
    },
  });

  const privateRoutes = (
    <Routes>
      <Route
        path="/home"
        element={<Entries /> }
      />
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
            {<NewUserGroups />}
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
    <StyledEngineProvider injectFirst>
      <Container fluid className="App bg-[#FAFAFA] min-h-screen">
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
                          <Sidebar element={privateRoutes} />
                      </PrivateRoute>
                    }
                  />
                </Routes>
              </UserProvider>
            </ApiProvider>
          </BrowserRouter>
        </ThemeProvider>
      </Container>
    </StyledEngineProvider>
  );
}
