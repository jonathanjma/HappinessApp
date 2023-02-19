import {useParams} from "react-router-dom";
import GroupData from "../components/GroupData";
import Graph from "../components/Graph";
import Stat from "../components/Stat";
import Users from "../components/Users";
import OldHistoryCard from "../components/OldHistoryCard";

export default function Group({ id }) {
  const { groupID } = useParams();
  const groupData = GroupData(groupID);

  const stats = [
    { value: true, key: 0 },
    { value: true, key: 1 },
    { value: true, key: 5 },
    { value: true, key: 8 },
  ];

  let allHappiness = [];
  for (let user of groupData.users) {
    allHappiness = allHappiness.concat(
      Users(user).data.map((e) => Object.assign(e, { user: user }))
    );
  }

  allHappiness.sort(
    (a, b) => Number(b.date.split("/")[1]) - Number(a.date.split("/")[1])
  );

  let tiles = [];
  let cur_date = "";
  let i = 0;
  for (let datapoint of allHappiness) {
    if (datapoint.date !== cur_date) {
      tiles.push(
        <>
          <p className="flex w-full justify-center text-2xl font-medium mx-3 mt-4 text-raisin-600">
            {datapoint.date}
          </p>
        </>
      );
      cur_date = datapoint.date;
    }
    if (datapoint.level !== null) {
      tiles.push(
        <OldHistoryCard
          key={i}
          id={datapoint.user}
          data={datapoint}
          useDate={false}
        />
      );
    }
    i++;
  }

  return (
    <>
      <p className="text-center text-4xl font-medium m-3 text-raisin-600">
        {groupData.name}
      </p>
      <div className="flex flex-wrap justify-center items-center">
        <Graph index={groupData.users} time="Weekly" id={id} />
      </div>
      <div className="flex flex-wrap justify-center items-center">
        {stats.map((e) => {
          if (e.value) {
            return <Stat id={id} key={e.key} val={e.key} />;
          }
          return null;
        })}
      </div>
      <p className="text-center text-3xl font-medium m-3 text-raisin-600">
        Happiness Log
      </p>
      <div className="@container flex flex-wrap justify-center">
        {tiles.map((e) => e)}
      </div>
    </>
  );
}
