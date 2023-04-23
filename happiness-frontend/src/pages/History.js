import Histories from "../components/Histories";
import { Tab } from "@headlessui/react";
import { useState, Fragment, useEffect } from "react";
import MonthView from "../components/MonthView";
import { GetRangeHappiness } from "../components/GetHappinessData";
import { useUser } from "../contexts/UserProvider";
import { Spinner } from "react-bootstrap";
import Stat from "../components/Stat";
import BigHistoryCard from "../components/BigHistoryCard";

export default function History(props) {
  const { user: userState } = useUser();
  const me = userState.user;

  // initializes dates corresponding to start and end of current week
  const [start, setStart] = useState(new Date());
  const [end, setEnd] = useState(new Date());
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
  // console.log(start);
  // console.log(end);

  // fetches data for weekly view
  const [isLoading, data, error, refetch] = GetRangeHappiness(
    true,
    me.id,
    start.toLocaleDateString("sv").substring(0, 10),
    end.toLocaleDateString("sv").substring(0, 10)
  );
  useEffect(() => {
    refetch();
  }, [start]);

  // initializes dates corresponding to start + end of current month
  const [stMonth, setStMonth] = useState(new Date());
  const [endMonth, setEndMonth] = useState(new Date());
  useEffect(
    () =>
      setStMonth((start) => {
        start.setDate(1);
        return new Date(start);
      }),
    []
  );
  useEffect(
    () =>
      setEndMonth((end) => {
        end.setDate(
          new Date(end.getFullYear(), end.getMonth() + 1, 0).getDate()
        );
        return new Date(end);
      }),
    []
  );
  console.log(stMonth);
  console.log(endMonth);

  // fetches data for monthly view
  const [isLoadingM, dataM, errorM, refetchM] = GetRangeHappiness(
    true,
    me.id,
    stMonth.toLocaleDateString("sv").substring(0, 10),
    endMonth.toLocaleDateString("sv").substring(0, 10)
  );
  useEffect(() => {
    refetchM();
  }, [stMonth, endMonth]);
  console.log(dataM);

  const [card, setCard] = useState();

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
                onClick={refetch}
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
                onClick={refetchM}
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
                type="button"
                className="absolute px-3 left-2 w-[50px] h-[40px] md:h-[50px] rounded-lg text-cultured-50 bg-raisin-600 text-xl"
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
                Week of {start.toLocaleDateString("sv").substring(0, 10)}
              </h3>
              <button
                type="button"
                className="absolute px-3 right-2 w-[50px] h-[40px] md:h-[50px] rounded-lg text-cultured-50 bg-raisin-600 text-xl"
                onClick={() => {
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
                        <Histories dataList={data} userList={[me]} />
                      </>
                    )}
                  </>
                )}
              </>
            )}
          </Tab.Panel>
          <Tab.Panel className="w-full justify-center">
            <div className="flex flex-start flex-wrap w-full justify-center mt-3 h-full">
              <div>
                <div className="flex-start justify-center border-solid w-full max-w-[550px] shadow-xl">
                  <div className="font-medium relative w-full text-center text-2xl py-2 my-0 bg-buff-200 max-h-[60px]">
                    <button
                      type="button"
                      className="absolute top-3 left-4 w-[40px] md:w-[60px] h-[40px] rounded-lg text-cultured-50 bg-raisin-600 text-xl"
                      onClick={() => {
                        setStMonth((start) => {
                          start.setMonth(start.getMonth() - 1);
                          return new Date(start);
                        });
                        setEndMonth((end) => {
                          end.setDate(1);
                          end.setMonth(end.getMonth() - 1);
                          end.setDate(
                            new Date(
                              end.getFullYear(),
                              end.getMonth() + 1,
                              0
                            ).getDate()
                          );
                          return new Date(end);
                        });
                        setCard();
                      }}
                    >
                      &lt;
                    </button>
                    <p className="py-2">
                      {stMonth.toLocaleString("en-US", { month: "long" }) +
                        " " +
                        stMonth.getFullYear()}{" "}
                    </p>
                    <button
                      type="button"
                      className="absolute top-3 right-4 w-[40px] md:w-[60px] h-[40px] rounded-lg text-cultured-50 bg-raisin-600 text-xl"
                      onClick={() => {
                        setStMonth((st) => {
                          st.setMonth(st.getMonth() + 1);
                          return new Date(st);
                        });
                        setEndMonth((ed) => {
                          ed.setDate(1);
                          ed.setMonth(ed.getMonth() + 1);
                          ed.setDate(
                            new Date(
                              ed.getFullYear(),
                              ed.getMonth() + 1,
                              0
                            ).getDate()
                          );
                          return new Date(ed);
                        });
                        setCard();
                      }}
                    >
                      &gt;
                    </button>
                  </div>
                  {isLoadingM ? (
                    <Spinner animation="border" />
                  ) : (
                    <>
                      {errorM ? (
                        <p className="text-xl font-medium text-raisin-600 m-3 text-center">
                          Error: Could not load happiness.
                        </p>
                      ) : (
                        <>
                          <MonthView
                            happinessData={dataM}
                            startDay={stMonth}
                            endDay={endMonth}
                            setCard={setCard}
                          />
                        </>
                      )}
                    </>
                  )}
                </div>
              </div>
              {isLoadingM ? (
                <Spinner animation="border" />
              ) : (
                <>
                  {errorM ? (
                    <p className="text-xl font-medium text-raisin-600 m-3 text-center">
                      Error: Could not load happiness.
                    </p>
                  ) : (
                    <>
                      {dataM.length === 0 ? (
                        <p className="text-xl font-medium text-raisin-600 m-3 text-center hidden lg:flex">
                          Statistics not available for selected period.
                        </p>
                      ) : (
                        <>
                          <div className="w-full flex flex-wrap justify-center max-w-[550px] lg:w-1/3 lg:mx-6 -mt-4">
                            {card && <BigHistoryCard data={card} user={me} />}

                            <div className="w-full justify-center hidden lg:flex">
                              <Stat
                                data={dataM.map((e) => e.value)}
                                val={0}
                                key={0}
                              />
                              <Stat
                                data={dataM.map((e) => e.value)}
                                val={1}
                                key={1}
                              />
                            </div>
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
