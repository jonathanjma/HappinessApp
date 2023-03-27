import OldHistoryCard from "./OldHistoryCard";
import HistoryCard from "./HistoryCard";
import Users from "./Users";
import { Link } from "react-router-dom";
import { Button } from "react-bootstrap";

/* 
Returns: Multiple HistoryCard elements, ordered backwards, starting from most recent happiness
Requires: max # of cards; id of current user
*/

// TODO: Integrate backend and COMPLETELY REWRITE WITH BETTER CODE!!

export default function Histories({ id, max, byCount }) {
  const tiles = [];
  const button = [];
  const userData = Users(id).data;
  const len = userData.length;
  let i = 1;
  let count = 0;
  while (count < max) {
    if (len - i < 1) {
      break;
    }
    if (userData[len - i].level !== null && byCount) {
      tiles.push(<HistoryCard key={i} id={id} data={userData[len - i]} />);
      count++;
    } else {
      tiles.push(<HistoryCard key={i} id={id} data={userData[len - i]} />);
    }
    i++;
  }
  if (byCount) {
    button.push(
      <>
        <div className="m-3">
          <Link to="/history">
            <Button variant="outline-secondary">show all</Button>
          </Link>
        </div>
      </>
    );
  }

  return (
    <>
      <div className="@container flex flex-wrap justify-center">{tiles}</div>
      <div className="flex justify-center">{button}</div>
    </>
  );
}
