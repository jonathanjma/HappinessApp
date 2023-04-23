import HistoryCard from "./HistoryCard";

/* 
Returns: Multiple HistoryCard elements
Requires: each user must correspond to the element at the same index of dataList
*/
export default function Histories({ dataList, userList }) {
  const tiles = [];
  for (let i = 0; i < dataList.length; i++) {
    tiles.push(<HistoryCard data={dataList[i]} user={userList} key={i} />);
  }

  return (
    <>
      <div className="@container flex flex-wrap justify-center">{tiles}</div>
    </>
  );
}
