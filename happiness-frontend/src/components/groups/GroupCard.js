import { Card, Image } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

export default function GroupCard({ data }) {
  const navigate = useNavigate();

  return (
    <Card
      onClick={() => navigate("/groups/" + data.id)}
      style={{ cursor: "pointer" }}
      className="m-2 group min-w-[200px]"
    >
      <Card.Body>
        <Card.Title>{data.name}</Card.Title>
        <div className="grid">
          <div className="grid-cols-4">
            {data.users.slice(0, 4).map((user) => (
              <Image
                key={user.id}
                src={user.profile_picture}
                title={user.username}
                roundedCircle
                className="m-2 max-w-[40px]"
              />
            ))}
            {data.users.length > 4 && (
              <p className="ml-2 my-2">
                {"+ " + (data.users.length - 4) + " users(s)"}
              </p>
            )}
          </div>
        </div>
      </Card.Body>
    </Card>
  );
}
