import { useParams } from "react-router-dom";
import { Fragment, useEffect, useState } from "react";
import { Tab } from "@headlessui/react";
import GroupManage from "../components/GroupManage";
import { useApi } from "../contexts/ApiProvider";
import { useQuery } from "react-query";
import TableView from "../components/TableView";
import GroupStats from "../components/GroupStats";
import { GetRangeHappiness } from "../components/GetHappinessData";
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
  const { groupID } = useParams();
  const api = useApi();
  const tabs = ["At a Glance", "Stats", "All Data", "Settings"];
  const [selectedIndex, setSelectedIndex] = useState(2);
  const [radioValue, setRadioValue] = useState(1);
  console.log("rerender--------------------");

  const [start, setStart] = useState(new Date());
  const [end, setEnd] = useState(new Date());
  useEffect(
    () => {
      console.log("useEffect start *****");
      setStart((start) => {
        // if (radioValue === 1) {
        start.setDate(start.getDate() - start.getDay());
        // } else {
        //   start.setDate(1);
        // }
        return new Date(start);
      });
      setEnd((end) => {
        // if (radioValue === 1) {
        end.setDate(end.getDate() + 7 - end.getDay());
        // } else {
        //   end.setDate(
        //     new Date(end.getFullYear(), end.getMonth() + 1, 0).getDate()
        //   );
        // }
        return new Date(end);
      });
    },
    [
      /*radioValue*/
    ]
  );
  console.log("start: " + start);
  console.log("end: " + end);

  // const {
  //   isLoading: isLoadingGI,
  //   data: dataGI,
  //   error: errorGI,
  // } = useQuery(
  //   "get group " + groupID,
  //   () => api.get("/group/" + groupID).then((res) => res.data),
  //   { refetchOnWindowFocus: false }
  // );

  const [isLoadingD, dataD, errorD, refetch] = GetRangeHappiness(
    false,
    groupID,
    start.toLocaleDateString("sv").substring(0, 10),
    end.toLocaleDateString("sv").substring(0, 10)
  );
  useEffect(() => {
    console.log("useEffect refetch");
    refetch();
  }, [refetch, start, end]);

  console.log(dataD);

  // Future: implement lazy loading of tabs
  return (
    <div className="flex flex-col items-center">
      {
        /*isLoadingGI ||*/ isLoadingD ? (
          <Spinner animation="border" />
        ) : (
          <>
            {
              /*errorGI ||*/ errorD ? (
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
                    {/*{dataGI.name}*/}Hello world 🌎
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
                        {/*<GroupStats*/}
                        {/*  groupData={dataGI}*/}
                        {/*  happinessData={dataD}*/}
                        {/*  selected={radioValue}*/}
                        {/*/>*/}
                      </Tab.Panel>
                      {/* Happiness Log (table view) */}
                      <Tab.Panel>
                        <div className="flex items-center justify-center">
                          <button
                            type="button"
                            className="px-3 me-3 w-[50px] h-[40px] rounded-lg text-cultured-50 bg-raisin-600 text-xl"
                            onClick={() => {
                              // setStart((start) => {
                              //   if (radioValue === 1) {
                              //     start.setDate(start.getDate() - 7);
                              //   } else {
                              //     start.setMonth(start.getMonth() - 1);
                              //   }
                              //   return new Date(start);
                              // });
                              // setEnd((end) => {
                              //   if (radioValue === 1) {
                              //     end.setDate(end.getDate() - 7);
                              //   } else {
                              //     end.setMonth(end.getMonth() - 1);
                              //   }
                              //   return new Date(end);
                              // });
                            }}
                          >
                            &lt;
                          </button>
                          <p className="text-3xl font-medium m-3  text-raisin-600">
                            Happiness Log
                          </p>
                          <button
                            type="button"
                            className="px-3 ms-3 w-[50px] h-[40px] rounded-lg text-cultured-50 bg-raisin-600 text-xl"
                            onClick={() => {
                              console.log("rad: " + radioValue);
                              console.log("s: " + start);
                              console.log("e: " + end);
                              setStart((start) => {
                                // if (radioValue === 1) {
                                start.setDate(start.getDate() + 7);
                                // } else {
                                //   start.setMonth(start.getMonth() + 1);
                                // }
                                console.log("s': " + new Date(start));
                                return new Date(start);
                              });
                              setEnd((end) => {
                                // if (radioValue === 1) {
                                end.setDate(end.getDate() + 7);
                                // } else {
                                //   end.setDate(1);
                                //   end.setMonth(end.getMonth() + 1);
                                //   end.setDate(
                                //     new Date(
                                //       end.getFullYear(),
                                //       end.getMonth() + 1,
                                //       0
                                //     ).getDate()
                                //   );
                                // }
                                console.log("e': " + new Date(end));
                                return new Date(end);
                              });
                            }}
                          >
                            &gt;
                          </button>
                        </div>
                        <TableView
                          // groupData={dataGI}
                          happinessData={dataD}
                          start={start}
                          end={end}
                        />
                      </Tab.Panel>
                      {/* Group Management */}
                      <Tab.Panel>
                        <p className="text-center text-3xl font-medium m-3 text-raisin-600">
                          Manage Group
                        </p>
                        {/*<GroupManage groupID={groupID} groupData={dataGI} />*/}
                      </Tab.Panel>
                    </Tab.Panels>
                  </Tab.Group>
                </>
              )
            }
          </>
        )
      }
    </div>
  );
}
