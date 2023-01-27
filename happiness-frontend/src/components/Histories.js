import HistoryCard from "./HistoryCard";
import Users from "./Users";
import {Link} from "react-router-dom";

/* 
Returns: Multiple HistoryCard elements, ordered backwards, starting from most recent happiness
Requires: max # of cards; id of current user
*/

export default function Histories({ id, max }) {
  const tiles = [];
  const button = [];
  const userData = Users(id).data;
  const len = userData.length;
  let i = 1;
  let count = 0;
  while (count < max) {
    if (len - i < 0) {
      break;
    }
    if (userData[len - i].level !== null) {
      tiles.push(<HistoryCard key={i} id={id} data={userData[len - i]} />);
      count++;
    }
    i++;
  }
  if (i <= len) {
    button.push(
      <>
        <div className="m-2.5">
          <Link to="/history">
            <button>show all</button>
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
