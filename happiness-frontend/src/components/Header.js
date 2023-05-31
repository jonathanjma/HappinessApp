import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import Nav from "react-bootstrap/Nav";
import NavDropdown from "react-bootstrap/NavDropdown";
import { NavLink } from "react-router-dom";
import Image from "react-bootstrap/Image";
import { useUser } from "../contexts/UserProvider";
import { Spinner } from "react-bootstrap";
import favicon from "../media/smiley-icon.webp";

export default function Header() {
  const { user: userState, Logout } = useUser();
  const me = userState.user;

  return (
    <Navbar bg="light" sticky="top" className="header">
      <Container fluid="md">
        <Navbar.Brand>
          <Nav.Link as={NavLink} to="/">
            <Image src={favicon} className="max-w-[32px] mr-2" />
            Happiness App
          </Nav.Link>
        </Navbar.Brand>
        <Nav className="flex items-center">
          <Nav.Link as={NavLink} to="/statistics">
            Stats
          </Nav.Link>
          <Nav.Link as={NavLink} to="/groups">
            Groups
          </Nav.Link>
          {me ? (
            <NavDropdown
              title={
                <Image
                  src={me.profile_picture}
                  roundedCircle
                  className="max-w-[30px] max-h-[30px]"
                  style={{ display: "inline" }}
                />
              }
              align="end"
            >
              <NavDropdown.Item as={NavLink} to={"/profile/" + me.id}>
                Profile
              </NavDropdown.Item>
              <NavDropdown.Item as={NavLink} to="/history">
                History
              </NavDropdown.Item>
              <NavDropdown.Divider />
              <NavDropdown.Item as={NavLink} to="/settings">
                Settings
              </NavDropdown.Item>
              <NavDropdown.Divider />
              <NavDropdown.Item
                as={NavLink}
                to="/"
                onClick={() => {
                  Logout();
                }}
              >
                Logout
              </NavDropdown.Item>
            </NavDropdown>
          ) : (
            <Spinner animation="border" />
          )}
        </Nav>
      </Container>
    </Navbar>
  );
}
