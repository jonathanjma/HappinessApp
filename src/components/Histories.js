import HistoryCard from "./HistoryCard";
import Users from "./Users";

export default function Histories(props) {
  const tiles = [];
  const button = [];
  const len = Users(props.id).data.length;
  let i = props.min;
  while (i <= props.max) {
    if (len - i < 0) {
      break;
    }
    tiles.push(<HistoryCard id={props.id} index={len - i} />);
    i++;
  }
  if (i <= len) {
    button.push(
      <>
        <div className="m-2.5">
          <button>show more</button>
        </div>
      </>
    );
  }
  // button will link to NEW history page that shows full history (all happiness info)

  return (
    <>
      <div className="flex flex-wrap justify-center">{tiles}</div>
      <div className="flex justify-center">{button}</div>
    </>
  );
}
