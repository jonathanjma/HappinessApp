import {useParams} from "react-router-dom";
import {Fragment, useEffect, useState} from "react";
import {Tab} from "@headlessui/react";
import GroupManage from "../../components/groups/GroupManage";
import {useApi} from "../../contexts/ApiProvider";
import {useQuery} from "react-query";
import TableView from "../../components/groups/TableView";
import GroupStats from "../../components/groups/GroupStats";
import {GetRangeHappiness} from "../../components/happinessHistory/GetHappinessData";
import {Spinner} from "react-bootstrap";
import {TabButton} from "./TabButton";
import {TimeButtonTitle} from "./TimeButtonTitle";

export default function Group() {
  const { groupID } = useParams();
  const api = useApi();
  const tabs = [/*"At a Glance", */ "All Data", "Stats", "Settings"];
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [radioValue, setRadioValue] = useState(1);

  const [start, setStart] = useState(new Date());
  const [end, setEnd] = useState(new Date());

  // when page is initially loaded or when week/month selector is changed, set start and end dates
  useEffect(() => {
    setStart(() => {
      if (radioValue === 1) {
        return new Date(
          new Date().getFullYear(),
          new Date().getMonth(),
          new Date().getDate() - 6
        );
      } else {
        return new Date(
          new Date().getFullYear(),
          new Date().getMonth() - 1,
          new Date().getDate() + 1
        );
      }
    });
    setEnd(() => {
      return new Date();
    });
  }, [radioValue]);

  // get group info: group names and users
  const {
    isLoading: isLoadingGI,
    data: dataGI,
    error: errorGI,
  } = useQuery("get group " + groupID, () =>
    api.get("/group/" + groupID).then((res) => res.data)
  );

  // get happiness data for currently viewed time range
  const [isLoadingD, dataD, errorD] = GetRangeHappiness(
    false,
    groupID,
    start.toLocaleDateString("sv").substring(0, 10),
    end.toLocaleDateString("sv").substring(0, 10)
  );

  return (
    <div className="flex flex-col items-center">
      {isLoadingGI || isLoadingD ? (
        <Spinner animation="border" />
      ) : (
        <>
          {errorGI || errorD ? (
            <p className="text-xl font-medium text-raisin-600 m-3">
              Error: Could not load group.
            </p>
          ) : (
            <>
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
              <Tab.Group
                selectedIndex={selectedIndex}
                onChange={setSelectedIndex}
              >
                {/* Tab view buttons */}
                <Tab.List className="flex flex-wrap justify-center mb-3">
                  {tabs.map((name, i) => (
                    <TabButton key={i} text={name} />
                  ))}
                </Tab.List>
                <Tab.Panels className="w-full">
                  {/* At A Glance (happiness trends) */}
                  {/*<Tab.Panel>*/}
                  {/*  <p className="text-center text-3xl font-medium m-3 text-raisin-600">*/}
                  {/*    Weekly/Monthly View*/}
                  {/*  </p>*/}
                  {/*</Tab.Panel>*/}
                  {/* Happiness Log (table view) */}
                  <Tab.Panel>
                    <TimeButtonTitle
                      text="Happiness Log"
                      radioValue={radioValue}
                      setStart={setStart}
                      setEnd={setEnd}
                    />
                    <TableView
                      groupData={dataGI}
                      happinessData={dataD}
                      start={start}
                      end={end}
                    />
                  </Tab.Panel>
                  {/* Statistics (graphs) */}
                  <Tab.Panel>
                    <TimeButtonTitle
                      text="Statistics"
                      radioValue={radioValue}
                      setStart={setStart}
                      setEnd={setEnd}
                    />
                    <GroupStats
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
            </>
          )}
        </>
      )}
    </div>
  );
}
