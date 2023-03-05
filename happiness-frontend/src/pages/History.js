import Histories from "../components/Histories";
import Users from "../components/Users";
import { Tab } from "@headlessui/react";
import { useState, Fragment } from "react";
import MonthView from "../components/MonthView";

export default function History(props) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  return (
    <>
      <div>
        <p className="text-center text-5xl font-medium m-3 text-raisin-600">
          History
        </p>
      </div>
      <Tab.Group selectedIndex={selectedIndex} onChange={setSelectedIndex}>
        <Tab.List className="lg:absolute lg:top-20 lg:right-10 flex sm-lg:w-full justify-center">
          <Tab as={Fragment}>
            {({ selected }) => (
              <button
                className={
                  selected
                    ? "inline-block px-4 py-3 m-1.5 w-[110px] rounded-lg text-cultured-50 bg-raisin-600"
                    : "inline-block px-4 py-3 m-1.5 w-[110px] rounded-lg hover:text-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 dark:hover:text-white"
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
                    ? "inline-block px-4 py-3 m-1.5 w-[110px] rounded-lg text-cultured-50 bg-raisin-600"
                    : "inline-block px-4 py-3 m-1.5 w-[110px] rounded-lg hover:text-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 dark:hover:text-white"
                }
              >
                Monthly
              </button>
            )}
          </Tab>
        </Tab.List>
        <Tab.Panels className="flex w-full justify-center">
          <Tab.Panel className="w-full justify-center">
            <Histories
              id={props.id}
              max={Users(props.id).data.length}
              division={true}
            />
          </Tab.Panel>
          <Tab.Panel className="w-full justify-center">
            <MonthView month="February" year={2023} startday={2} />
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </>
  );
}
