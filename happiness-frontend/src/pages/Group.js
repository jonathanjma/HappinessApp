import { useParams } from "react-router-dom";
import GroupData from "../components/GroupData";
import Graph from "../components/Graph";
import Stat from "../components/Stat";
import Users from "../components/Users";
import BigHistoryCard from "../components/BigHistoryCard";
import HistoryCard from "../components/HistoryCard";
import { Fragment, useState } from "react";
import { Tab } from "@headlessui/react";
import GroupManage from "../components/GroupManage";

function TabButton({ text }) {
  return (
    <Tab as={Fragment}>
      {({ selected }) => (
        <button
          className={
            "inline-block px-2 py-2.5 m-1.5 w-[140px] rounded-lg " +
            (selected
              ? "text-cultured-50 bg-raisin-600"
              : "hover:text-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 dark:hover:text-white")
          }
        >
          {text}
        </button>
      )}
    </Tab>
  );
}

export default function Group({ id }) {
  const { groupID } = useParams();
  const groupData = GroupData(groupID);
  const [selectedIndex, setSelectedIndex] = useState(1);

  const stats = [0, 1, 5, 8];
  const tabs = ["At a Glance", "Stats", "Log", "Settings"];

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
        <BigHistoryCard
          key={i}
          id={datapoint.user}
          data={datapoint}
          shown={true}
          useDate={false}
        />
      );
    }
    i++;
  }

  return (
    <>
      <div className="flex flex-col items-center">
        <p className="text-4xl font-medium m-3 text-raisin-600">
          {groupData.name}
        </p>
        <Tab.Group selectedIndex={selectedIndex} onChange={setSelectedIndex}>
          <Tab.List className="flex flex-wrap justify-center mb-3">
            {tabs.map((name, i) => (
              <TabButton key={i} text={name} />
            ))}
          </Tab.List>
          <Tab.Panels className="w-full">
            <Tab.Panel>
              <p className="text-center text-3xl font-medium m-3 text-raisin-600">
                Weekly/Monthly View
              </p>
            </Tab.Panel>
            <Tab.Panel>
              <div className="flex justify-center">
                <Graph index={groupData.users} time="Weekly" id={id} />
              </div>
              <div className="flex flex-wrap justify-center items-center">
                {stats.map((e) => (
                  <Stat id={id} key={e} val={e} />
                ))}
              </div>
            </Tab.Panel>
            <Tab.Panel>
              <p className="text-center text-3xl font-medium m-3 text-raisin-600">
                Happiness Log
              </p>
              <div className="@container flex flex-wrap justify-center">
                {tiles.map((e) => e)}
              </div>
            </Tab.Panel>
            <Tab.Panel>
              <p className="text-center text-3xl font-medium m-3 text-raisin-600">
                Manage Group
              </p>
              <GroupManage id={id} />
            </Tab.Panel>
          </Tab.Panels>
        </Tab.Group>
      </div>
    </>
  );
}
