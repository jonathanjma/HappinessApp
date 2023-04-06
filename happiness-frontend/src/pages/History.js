import Histories from "../components/Histories";
import Users from "../components/Users";
import { Tab } from "@headlessui/react";
import { useState, Fragment, useEffect } from "react";
import MonthView from "../components/MonthView";
import { GetRangeHappiness } from "../components/GetHappinessData";
import { useUser } from "../contexts/UserProvider";
import { Spinner } from "react-bootstrap";
import { useQuery } from "react-query";
import { useApi } from "../contexts/ApiProvider";

export default function History(props) {
  const { user: userState } = useUser();
  const me = userState.user;

  const [start, setStart] = useState(new Date());
  const [end, setEnd] = useState(new Date());
  console.log(start);
  console.log(end);
  useEffect(
    () =>
      setStart((start) => {
        start.setDate(start.getDate() - start.getDay());
        return new Date(start);
      }),
    []
  );
  useEffect(
    () =>
      setEnd((end) => {
        end.setDate(end.getDate() + 7 - end.getDay());
        return new Date(end);
      }),
    []
  );
  console.log(start);
  console.log(end);

  const api = useApi();
  const [isLoading, data, error, refetch] = GetRangeHappiness(
    me,
    start.toISOString().substring(0, 10),
    end.toISOString().substring(0, 10)
  );
  useEffect(() => {
    refetch();
  }, [start, end]);

  const [selectedIndex, setSelectedIndex] = useState(0);

  return (
    <>
      <div>
        <p className="text-center text-5xl font-medium m-3 lg:my-4 text-raisin-600">
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
        <Tab.Panels className="flex w-full justify-center">
          <Tab.Panel className="w-full justify-center">
            <div className="relative flex flex-wrap items-center justify-center w-full text-center pt-2">
              <button
                className="absolute px-3 py-2 my-2 left-2 w-[50px] rounded-lg text-cultured-50 bg-raisin-600 text-2xl"
                onClick={() => {
                  setEnd((end) => {
                    end.setDate(end.getDate() - 7);
                    return new Date(end);
                  });
                  setStart((start) => {
                    start.setDate(start.getDate() - 7);
                    return new Date(start);
                  });
                }}
              >
                &lt;
              </button>
              <h3 className="w-full">
                Week of {start.toISOString().slice(0, 10)}
              </h3>
              <button
                className="absolute px-3 py-2 my-2 right-2 w-[50px] rounded-lg text-cultured-50 bg-raisin-600 text-2xl"
                onClick={(_) => {
                  setEnd((end) => {
                    end.setDate(end.getDate() + 7);
                    return new Date(end);
                  });
                  setStart((start) => {
                    start.setDate(start.getDate() + 7);
                    return new Date(start);
                  });
                }}
              >
                &gt;
              </button>
            </div>
            {isLoading ? (
              <Spinner animation="border" />
            ) : (
              <>
                {error ? (
                  <p className="text-xl font-medium text-raisin-600 m-3 text-center">
                    Error: Could not load happiness.
                  </p>
                ) : (
                  <>
                    {data.length === 0 ? (
                      <p className="text-xl font-medium text-raisin-600 m-3 text-center">
                        Data not available for selected period.
                      </p>
                    ) : (
                      <>
                        <Histories dataList={data} />
                      </>
                    )}
                  </>
                )}
              </>
            )}
          </Tab.Panel>
          <Tab.Panel className="w-full justify-center">
            <MonthView month="February" year={2023} startday={2} />
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </>
  );
}
