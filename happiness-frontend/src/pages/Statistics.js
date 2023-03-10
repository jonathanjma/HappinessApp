import Stat from "../components/Stat";
import Graph from "../components/Graph";
import Users from "../components/Users";
import { Tab } from "@headlessui/react";
import { useState, Fragment } from "react";

export default function Statistics(props) {
  /*
      0 = mean
      1 = median
      2 = mode
      3 = range
      4 = standard deviation
      5 = minimum
      6 = q1
      7 = q3
      8 = maximum
      */
  // future conversion to boolean array
  const datavals = [
    { value: true, key: 0 },
    { value: true, key: 1 },
    { value: false, key: 2 },
    { value: false, key: 3 },
    { value: false, key: 4 },
    { value: true, key: 5 },
    { value: false, key: 6 },
    { value: false, key: 7 },
    { value: true, key: 8 },
  ];
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
          <Tab.Panel className="w-full justify-center">
            <div className="mt-4 -md:mt-4 md:flex md:flex-wrap justify-center items-center @container">
              <Graph
                index={[props.id].concat(Users(props.id).friends)}
                time="Weekly"
                id={props.id}
              />
              <div className="flex flex-wrap w-full justify-center items-center">
                {datavals.map((e) => {
                  if (e.value) {
                    return <Stat id={props.id} key={e.key} val={e.key} />;
                  }
                  return null;
                })}
              </div>
            </div>
          </Tab.Panel>
          <Tab.Panel className="w-full justify-center">
            <div className="mt-4 -md:mt-4 md:flex md:flex-wrap justify-center items-center @container">
              <Graph
                index={[props.id].concat(Users(props.id).friends)}
                time="Monthly"
                id={props.id}
              />
            </div>
            <div className="flex flex-wrap justify-center items-center">
              {datavals.map((e) => {
                if (e.value) {
                  return <Stat id={props.id} key={e.key} val={e.key} />;
                }
                return null;
              })}
            </div>
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </>
  );
}
