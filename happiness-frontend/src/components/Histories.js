import OldHistoryCard from "./OldHistoryCard";
import HistoryCard from "./HistoryCard";
import Users from "./Users";
import { Link } from "react-router-dom";
import { Button } from "react-bootstrap";

/* 
Returns: Multiple HistoryCard elements, ordered backwards, starting from most recent happiness
Requires: max # of cards; id of current user
*/

export default function Histories({ id, max, division }) {
  const tiles = [];
  const button = [];
  const userData = Users(id).data;
  const len = userData.length;
  let i = 1;
  let count = 0;
  let divideby = 7;
  while (count < max) {
    if (len - i < 0) {
      break;
    }
    if ((len - i) % 7 == 0 && division) {
      if (len - i == len - 1) {
        tiles.push(
          <div className="w-full text-center pt-2">
            <h3>This Week</h3>
          </div>
        );
      } else {
        tiles.push(
          <div className="w-full text-center pt-5">
            <h3>Week of 1/2</h3>
          </div>
        );
      }
    }
    if (userData[len - i].level !== null && !division) {
      tiles.push(<HistoryCard key={i} id={id} data={userData[len - i]} />);
      count++;
    } else {
      tiles.push(<HistoryCard key={i} id={id} data={userData[len - i]} />);
    }
    i++;
  }
  if (i <= len) {
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
