import { useParams } from "react-router-dom";
import { Fragment, useState } from "react";
import { Tab } from "@headlessui/react";
import GroupManage from "../components/GroupManage";
import { useApi } from "../contexts/ApiProvider";
import { useQuery } from "react-query";
import TableView from "../components/TableView";
import GroupStats from "../components/GroupStats";
import { PrevMonthData, PrevWeekData } from "../components/GetHappinessData";
import { Spinner } from "react-bootstrap";

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

export default function Group() {
  const tabs = ["At a Glance", "Stats", "All Data", "Settings"];
  const [selectedIndex, setSelectedIndex] = useState(2);
  const [radioValue, setRadioValue] = useState(2);

  const { groupID } = useParams();
  const api = useApi();
  const {
    isLoading: isLoadingGI,
    data: dataGI,
    error: errorGI,
  } = useQuery("get group " + groupID, () =>
    api.get("/group/" + groupID).then((res) => res.data)
  );

  const [isLoadingD, dataD, errorD] =
    radioValue === 1
      ? PrevWeekData(false, groupID)
      : PrevMonthData(false, groupID);

  // Future:
  // implement lazy loading of tabs
  // implement useQuery error case
  return (
    <>
      {isLoadingGI || isLoadingD ? (
        <Spinner animation="border" />
      ) : (
        <div className="flex flex-col items-center">
          {/* Week + Month view toggle buttons */}
          <div
            className="lg:absolute lg:top-20 lg:right-10 flex sm-lg:w-full justify-center"
            role="group"
          >
            <button
              type="button"
              className={
                "p-1.5 w-[75px] rounded-l-lg " +
                (radioValue === 1
                  ? "text-cultured-50 bg-raisin-600"
                  : "hover:text-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 dark:hover:text-white")
              }
              onClick={() => setRadioValue(1)}
            >
              Week
            </button>
            <button
              type="button"
              className={
                "p-1.5 w-[75px] rounded-r-lg " +
                (radioValue === 2
                  ? "text-cultured-50 bg-raisin-600"
                  : "hover:text-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 dark:hover:text-white")
              }
              onClick={() => setRadioValue(2)}
            >
              Month
            </button>
          </div>

          {/* Group name */}
          <p className="text-4xl font-medium m-3 text-raisin-600">
            {dataGI.name}
          </p>
          <Tab.Group selectedIndex={selectedIndex} onChange={setSelectedIndex}>
            {/* Tab view buttons */}
            <Tab.List className="flex flex-wrap justify-center mb-3">
              {tabs.map((name, i) => (
                <TabButton key={i} text={name} />
              ))}
            </Tab.List>
            <Tab.Panels className="w-full">
              {/* At A Glance (happiness trends) */}
              <Tab.Panel>
                <p className="text-center text-3xl font-medium m-3 text-raisin-600">
                  Weekly/Monthly View
                </p>
              </Tab.Panel>
              {/* Statistics (graphs) */}
              <Tab.Panel>
                <p className="text-center text-3xl font-medium m-3 text-raisin-600">
                  Statistics
                </p>
                <GroupStats
                  groupData={dataGI}
                  happinessData={dataD}
                  selected={radioValue}
                />
              </Tab.Panel>
              {/* Happiness Log (table view) */}
              <Tab.Panel>
                <p className="text-center text-3xl font-medium m-3 text-raisin-600">
                  Happiness Log
                </p>
                <TableView
                  groupData={dataGI}
                  happinessData={dataD}
                  selected={radioValue}
                />
              </Tab.Panel>
              {/* Group Management */}
              <Tab.Panel>
                <p className="text-center text-3xl font-medium m-3 text-raisin-600">
                  Manage Group
                </p>
                <GroupManage groupID={groupID} groupData={dataGI} />
              </Tab.Panel>
            </Tab.Panels>
          </Tab.Group>
        </div>
      )}
    </>
  );
}
