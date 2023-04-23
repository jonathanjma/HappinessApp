import Stat from "../components/Stat";
import Graph from "../components/Graph";
import { Tab } from "@headlessui/react";
import { useState, Fragment } from "react";
import { Spinner } from "react-bootstrap";
import { useUser } from "../contexts/UserProvider";
import { PrevWeekData, PrevMonthData } from "../components/GetHappinessData";

export default function Statistics() {
  const { user: userState } = useUser();
  const me = userState.user;
  const settings = me.settings;
  const settingsNames = settings.map((e) => e.key);

  const [isLoadingH, dataH, errorH] = PrevWeekData(true, me.id);
  const [isLoadingHM, dataHM, errorHM] = PrevMonthData(true, me.id);

  const users = [me];

  /*
      0 = mean
      1 = median
      2 = mode
      3 = standard deviation
      4 = minimum
      5 = maximum
      */
  // future conversion to boolean array
  const setNames = [
    "Show Average",
    "Show Median",
    "Show Mode",
    "Show Standard Deviation",
    "Show Minimum Value",
    "Show Maximum Value",
  ];
  const datavals = setNames.map((name) => {
    if (settingsNames.includes(name)) {
      for (const e of settings) {
        if (name === e.key) {
          return e.value;
        }
      }
    } else return false;
  });
  // console.log(datavals);
  const [selectedIndex, setSelectedIndex] = useState(0);

  return (
    <>
      <p className="w-full text-center text-5xl font-medium my-4 text-raisin-600">
        Statistics
      </p>
      <Tab.Group selectedIndex={selectedIndex} onChange={setSelectedIndex}>
        <Tab.List className="lg:absolute lg:top-20 lg:right-10 flex sm-lg:w-full justify-center">
          <Tab as={Fragment}>
            {({ selected }) => (
              <button
                className={
                  selected
                    ? "inline-block sm:px-4 py-2 sm:py-4 mb-1 md:m-1.5 w-[110px] md:h-[60px] rounded-l-lg md:rounded-lg text-cultured-50 bg-raisin-600 text-xs sm:text-sm md:text-md text-center"
                    : "inline-block sm:px-4 py-2 sm:py-4 mb-1 md:m-1.5 w-[110px] md:h-[60px] rounded-l-lg md:rounded-lg hover:text-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 dark:hover:text-white text-xs sm:text-sm md:text-md text-center"
                }
              >
                Weekly
              </button>
            )}
          </Tab>
          <Tab as={Fragment}>
            {({ selected }) => (
              <button
                className={
                  selected
                    ? "inline-block sm:px-4 py-2 sm:py-3 mb-1 md:m-1.5 w-[110px] md:h-[60px] rounded-r-lg md:rounded-lg text-cultured-50 bg-raisin-600 text-xs sm:text-sm md:text-md text-center"
                    : "inline-block sm:px-4 py-2 sm:py-3 mb-1 md:m-1.5 w-[110px] md:h-[60px] rounded-r-lg md:rounded-lg hover:text-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 dark:hover:text-white text-xs sm:text-sm md:text-md text-center"
                }
              >
                Monthly
              </button>
            )}
          </Tab>
        </Tab.List>
        <Tab.Panels>
          <Tab.Panel className="w-full lg:flex lg:flex-wrap justify-center">
            <div className="mt-4 -lg:mt-4 w-full lg:flex lg:flex-wrap justify-center items-start @container">
              {isLoadingH ? (
                <Spinner animation="border" />
              ) : (
                <>
                  {errorH ? (
                    <p className="text-xl font-medium text-raisin-600 m-3">
                      Error: Could not load happiness.
                    </p>
                  ) : (
                    <>
                      {dataH.length === 0 ? (
                        <p className="text-xl font-medium text-raisin-600 m-3">
                          Data not available for selected period.
                        </p>
                      ) : (
                        <>
                          <div className="lg:w-1/2 lg:mt-4">
                            <Graph data={dataH} users={users} time="Weekly" />
                          </div>
                          <div className="flex flex-wrap justify-center items-start lg:w-1/2 xl:w-1/2">
                            {datavals.map((e) => {
                              if (e.value) {
                                return (
                                  <Stat
                                    data={dataH.map((e) => e.value)}
                                    key={e.key}
                                    val={e.key}
                                  />
                                );
                              }
                              return null;
                            })}
                          </div>
                        </>
                      )}
                    </>
                  )}
                </>
              )}
            </div>
          </Tab.Panel>
          <Tab.Panel className="w-full lg:flex lg:flex-wrap justify-center">
            <div className="mt-4 -lg:mt-4 w-full lg:flex lg:flex-wrap justify-center items-start @container">
              {isLoadingHM ? (
                <Spinner animation="border" />
              ) : (
                <>
                  {errorHM ? (
                    <p className="text-xl font-medium text-raisin-600 m-3">
                      Error: Could not load happiness.
                    </p>
                  ) : (
                    <>
                      {dataHM.length === 0 ? (
                        <p className="text-xl font-medium text-raisin-600 m-3">
                          Data not available for selected period.
                        </p>
                      ) : (
                        <>
                          <div className="lg:w-1/2 lg:mt-4">
                            <Graph data={dataHM} users={users} time="Monthly" />
                          </div>
                          <div className="flex flex-wrap justify-center items-start lg:w-1/2 xl:w-1/2">
                            {datavals.map((val, t) => {
                              if (val) {
                                return (
                                  <Stat
                                    data={dataHM.map((e) => e.value)}
                                    key={t}
                                    val={t}
                                  />
                                );
                              }
                              return null;
                            })}
                          </div>
                        </>
                      )}
                    </>
                  )}
                </>
              )}
            </div>
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </>
  );
}
