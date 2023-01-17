import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import Nav from "react-bootstrap/Nav";
import NavDropdown from "react-bootstrap/NavDropdown";
import {NavLink} from "react-router-dom";
import Image from "react-bootstrap/Image";
import Users from "./Users";

export default function Header({ user_id }) {
  return (
    <Navbar bg="light" sticky="top">
      <Container fluid="md">
        <Navbar.Brand>😀 Happiness App</Navbar.Brand>
        <Nav>
          <Nav.Link as={NavLink} to="/">
            Home
          </Nav.Link>
          <Nav.Link as={NavLink} to="/statistics">
            Statistics
          </Nav.Link>
          <NavDropdown
            title={
              <Image
                src={Users(user_id).img}
                roundedCircle
                className="max-w-[30px] max-h-[30px]"
                style={{ display: "inline" }}
              />
            }
            align="end"
          >
            <NavDropdown.Item as={NavLink} to="/profile">
              Profile
            </NavDropdown.Item>
            <NavDropdown.Item as={NavLink} to="/groups">
              Groups
            </NavDropdown.Item>
            <NavDropdown.Divider />
            <NavDropdown.Item as={NavLink} to="/">
              Logout
            </NavDropdown.Item>
          </NavDropdown>
        </Nav>
      </Container>
    </Navbar>
  );
}
