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

export default function Histories({ id, max, division }) {
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
    if ((len - i) % 7 === 0 && division) {
      if (len - i === len - 1) {
        tiles.push(
          <>
            <div className="relative flex flex-wrap items-center justify-center w-full text-center pt-2">
              <button className="absolute px-3 py-2 my-2 left-2 w-[50px] rounded-lg text-cultured-50 bg-raisin-600 text-2xl">&lt;</button>
              <h3 className="w-full">Week of 12/29</h3>
              <button className="absolute px-3 py-2 my-2 right-2 w-[50px] rounded-lg text-cultured-50 bg-raisin-600 text-2xl">&gt;</button>
            </div>
          </>
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
  if (!division) {
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
