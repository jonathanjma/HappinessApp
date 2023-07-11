import Stat from "../components/statGraphs/Stat";
import Graph from "../components/statGraphs/Graph";
import { TimeButtonTitle } from "./Group";
import { useState, useEffect } from "react";
import { Spinner } from "react-bootstrap";
import { useUser } from "../contexts/UserProvider";
import { GetRangeHappiness } from "../components/happinessHistory/GetHappinessData";

export default function Statistics() {
  const { user: userState } = useUser();
  const me = userState.user;
  const settings = me.settings;
  const settingsNames = settings.map((e) => e.key);

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

  // get happiness data for currently viewed time range
  const [isLoadingH, dataH, errorH] = GetRangeHappiness(
    true,
    me.id,
    start.toLocaleDateString("sv").substring(0, 10),
    end.toLocaleDateString("sv").substring(0, 10)
  );

  const users = [me];

  /*
      0 = mean
      1 = median
      2 = mode
      3 = standard deviation
      4 = minimum
      5 = maximum
  */

  // integration of settings with values shown
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
          return e.enabled;
        }
      }
    } else return false;
  });
  // console.log(datavals);

  return (
    <>
      <TimeButtonTitle
        text="Statistics"
        radioValue={radioValue}
        setStart={setStart}
        setEnd={setEnd}
        size="text-4xl sm:text-5xl"
      />
      {/* buttons to activate weekly/monthly view */}
      <div className="lg:absolute lg:top-20 lg:right-10 flex sm-lg:w-full justify-center">
        <button
          className={
            "inline-block sm:px-4 py-2 sm:py-4 mb-1 md:m-1.5 w-[110px] md:h-[60px] rounded-l-lg md:rounded-lg text-xs sm:text-sm md:text-md text-center" +
            (radioValue === 1
              ? " text-cultured-50 bg-raisin-600"
              : " hover:text-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 dark:hover:text-white")
          }
          onClick={() => setRadioValue(1)}
        >
          Weekly
        </button>
        <button
          className={
            "inline-block sm:px-4 py-2 sm:py-4 mb-1 md:m-1.5 w-[110px] md:h-[60px] rounded-r-lg md:rounded-lg text-xs sm:text-sm md:text-md text-center" +
            (radioValue === 2
              ? " text-cultured-50 bg-raisin-600"
              : " hover:text-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 dark:hover:text-white")
          }
          onClick={() => setRadioValue(2)}
        >
          Monthly
        </button>
      </div>
      <div className="w-full lg:flex lg:flex-wrap justify-center">
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
                        <Graph
                          data={dataH}
                          users={users}
                          time={radioValue === 1 ? "Weekly" : "Monthly"}
                        />
                      </div>
                      <div className="flex flex-wrap justify-center items-start lg:w-1/2 xl:w-1/2">
                        {datavals.map((val, t) => {
                          if (val) {
                            return (
                              <Stat
                                data={dataH.map((e) => e.value)}
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
      </div>
    </>
  );
}
