import BigHistoryCard from "./BigHistoryCard";
import HistoryCard from "./HistoryCard";
import Users from "./Users";

/* 
Returns: Multiple HistoryCard elements
Requires: each name must correspond to the element at the same index of dataList
If names is empty, useDate is true.
*/
export default function Histories({ dataList, names = [], useDate = true }) {
  const tiles = [];
  for (let i = 0; i < dataList.length; i++) {
    if (names.length !== 0) {
      tiles.push(
        <HistoryCard
          data={dataList[i]}
          name={names[i]}
          useDate={useDate}
          key={i}
        />
      );
    } else {
      tiles.push(<HistoryCard data={dataList[i]} useDate={true} key={i} />);
    }
  }

  return (
    <>
      <div className="@container flex flex-wrap justify-center">{tiles}</div>
    </>
  );
}
