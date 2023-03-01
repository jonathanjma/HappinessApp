import { Card, Image } from "react-bootstrap";
import Users from "./Users";
import { useNavigate } from "react-router-dom";
import gravatarUrl from "gravatar-url";

export default function GroupCard({ id, data }) {
  let groupUsers = data.users.map((user) => Users(user));
  const navigate = useNavigate();

  const onClick = (ev) => {
    ev.preventDefault();
    navigate("/groups/" + id);
  };

  return (
    <Card onClick={onClick} style={{ cursor: "pointer" }} className="m-2">
      <Card.Body>
        <Card.Title>{data.name}</Card.Title>
        <div className="grid">
          <div className="grid-cols-4">
            {groupUsers.slice(0, 4).map((user) => (
              <Image
                key={user.id}
                src={gravatarUrl(user.email, {
                  size: 40,
                  default: "identicon",
                })}
                roundedCircle
                className="m-2"
              />
            ))}
            {groupUsers.length > 4 && (
              <p className="ml-2 my-2">
                {"+ " + (groupUsers.length - 4) + " users(s)"}
              </p>
            )}
          </div>
        </div>
        {/*<Button onClick={onClick}>Open Group</Button>*/}
      </Card.Body>
    </Card>
  );
}
