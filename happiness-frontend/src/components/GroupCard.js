import { Button, Card } from "react-bootstrap";
import Users from "./Users";
import { useNavigate } from "react-router-dom";

export default function GroupCard({ id, data }) {
  let groupUsers = data.users.map((user) => Users(user).name);
  const navigate = useNavigate();

  const onClick = (ev) => {
    ev.preventDefault();
    navigate("/groups/" + id);
  };

  return (
    <Card
      onClick={onClick}
      style={{ cursor: "pointer" }}
      className="flex w-full group my-2 p-3"
    >
      <Card.Body>
        <Card.Title>{data.name}</Card.Title>
        <Card.Text>Users: {groupUsers.join(", ")}</Card.Text>
        <Button onClick={onClick}>Open Group</Button>
      </Card.Body>
    </Card>
  );
}
