import {useParams} from "react-router-dom";
import GroupData from "../components/GroupData";
import Graph from "../components/Graph";
import Stat from "../components/Stat";
import Users from "../components/Users";
import {Card, Stack} from "react-bootstrap";

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

  function comp(a, b) {
    return Number(b.date.split("/")[1]) - Number(a.date.split("/")[1]);
  }

  allHappiness.sort(comp);

  let tiles = [];
  let cur_date = "";
  for (let datapoint of allHappiness) {
    if (datapoint.date !== cur_date) {
      tiles.push(<p>{datapoint.date}</p>);
      cur_date = datapoint.date;
    }
    if (datapoint.level !== null) {
      tiles.push(
        <>
          <Card>
            <Stack direction="horizontal" gap={3}>
              <img
                className="justify-center rounded-full max-h-[50px] max-w-[50px] @xl:max-w-[60px] @xl:max-h-[60px] block mx-auto h-24 rounded-full sm:mx-0 sm:shrink-0"
                src={Users(datapoint.user).img}
                alt="profile"
              />
              <p>Happiness: {datapoint.level}</p>
            </Stack>
          </Card>
        </>
      );
    }
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
      <p className="text-center text-xl font-medium m-3 text-raisin-600">
        Happiness Log
      </p>
      <div className="flex flex-wrap justify-center items-center">
        {tiles.map((e) => e)}
      </div>
    </>
  );
}
