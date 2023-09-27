import Stat from "../components/statGraphs/Stat";
import Graph from "../components/statGraphs/Graph";
import { useState, useEffect } from "react";
import { Spinner } from "react-bootstrap";
import { useUser } from "../contexts/UserProvider";
import { GetRangeHappiness } from "../components/happinessHistory/GetHappinessData";
import { Box, Input, Button, Typography } from "@mui/material";
import ChevronRightSharpIcon from "@mui/icons-material/ChevronRightSharp";

import SearchBar from "../components/SearchBar";

export default function NewStatistics() {
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
      <Box className="mt-16 mx-8">
        <Box className="px-8 mb-6">
          <SearchBar />
        </Box>
        <Box className="px-8 w-2/3">
          <Box className="w-full flex">
            <Box className="px-2 flex flex-1 items-center">
              <Box className="mr-4">
                {start.toISOString().substring(0, 10) +
                  "-" +
                  end.toISOString().substring(0, 10)}
              </Box>
              <Button
                className="bg-raisin-600 p-1 border rounded-lg max-w-[40px] min-w-[40px] h-[40px] mx-0.5"
                onClick={() => {
                  setStart((start) => {
                    if (radioValue === 1) {
                      start.setDate(start.getDate() - 7);
                    } else {
                      start.setMonth(start.getMonth() - 1);
                    }
                    return new Date(start);
                  });
                  setEnd((end) => {
                    if (radioValue === 1) {
                      end.setDate(end.getDate() - 7);
                    } else {
                      end.setMonth(end.getMonth() - 1);
                    }
                    return new Date(end);
                  });
                }}
              >
                <ChevronRightSharpIcon className="-rotate-90" />
              </Button>
              <Button
                className="bg-raisin-600 p-1 border rounded-lg max-w-[40px] min-w-[40px] h-[40px] mx-0.5"
                onClick={() => {
                  setStart((start) => {
                    if (radioValue === 1) {
                      start.setDate(start.getDate() + 7);
                    } else {
                      start.setMonth(start.getMonth() + 1);
                    }
                    return new Date(start);
                  });
                  setEnd((end) => {
                    if (radioValue === 1) {
                      end.setDate(end.getDate() + 7);
                    } else {
                      end.setMonth(end.getMonth() + 1);
                    }
                    return new Date(end);
                  });
                }}
              >
                <ChevronRightSharpIcon className="rotate-90" />
              </Button>
            </Box>
            <Box className="">
              <Button
                className={
                  "inline-block p-3 border mb-1 w-[100px] md:h-[50px] rounded-l-lg text-xs sm:text-sm text-center" +
                  (radioValue === 1
                    ? " text-cultured-50 bg-raisin-600"
                    : " hover:text-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 dark:hover:text-white")
                }
                onClick={() => setRadioValue(1)}
              >
                Weekly
              </Button>
              <Button
                className={
                  "inline-block p-3 border mb-1 w-[100px] md:h-[50px] rounded-r-lg text-xs sm:text-sm text-center" +
                  (radioValue === 2
                    ? " text-cultured-50 bg-raisin-600"
                    : " hover:text-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 dark:hover:text-white")
                }
                onClick={() => setRadioValue(2)}
              >
                Monthly
              </Button>
            </Box>
          </Box>
          {isLoadingH ? (
            <Spinner animation="border" />
          ) : (
            <>
              {errorH ? (
                <Typography className="text-xl font-medium text-raisin-600 m-3">
                  Error: Could not load happiness.
                </Typography>
              ) : (
                <>
                  {dataH.length === 0 ? (
                    <Typography className="text-xl font-medium text-raisin-600 m-3">
                      Data not available for selected period.
                    </Typography>
                  ) : (
                    <>
                      <Box className="my-3">
                        <Graph
                          data={dataH}
                          users={users}
                          time={radioValue === 1 ? "Weekly" : "Monthly"}
                        />
                      </Box>
                      <Box className="flex flex-wrap justify-center items-start">
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
                      </Box>
                    </>
                  )}
                </>
              )}
            </>
          )}
        </Box>
      </Box>
    </>
  );
}
