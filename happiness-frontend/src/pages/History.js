import { Tab } from "@headlessui/react";
import { Fragment, useEffect, useState } from "react";
import { Spinner } from "react-bootstrap";
import { useQuery } from "react-query";
import { useParams } from "react-router-dom";
import BigHistoryCard from "../components/happinessHistory/BigHistoryCard";
import { GetRangeHappiness } from "../components/happinessHistory/GetHappinessData";
import Histories from "../components/happinessHistory/Histories";
import MonthView from "../components/happinessHistory/MonthView";
import Stat from "../components/statGraphs/Stat";
import { useApi } from "../contexts/ApiProvider";
import { Box, Button, Typography } from "@mui/material";
import EditIcon from '@mui/icons-material/Edit';
import CommentCard from "../components/CommentCard";

export default function History() {
  // const { user: userState } = useUser();
  // const me = userState.user;
  const userID = useParams().userID;
  const api = useApi();
  const USE_NEW_UI = process.env.REACT_APP_USE_NEW_UI;
  const {
    isLoading: isLoadingU,
    data: user,
    error: errorU,
    refetch: refetchU,
  } = useQuery("get user from user id", () =>
    api.get("/user/" + userID).then((res) => res.data)
  );

  const [pageLoading, setPageLoading] = useState(true);
  useEffect(() => {
    const refetchAll = async () => {
      setPageLoading(true);
      console.log("refetching!!");
      await refetchU();
      setPageLoading(false);
      // setPageLoading(false);
    };
    refetchAll();
  }, [userID]);

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
        end.setDate(end.getDate() + 6 - end.getDay());
        return new Date(end);
      }),
    []
  );
  // console.log(start);
  // console.log(end);

  // fetches data for weekly view
  const [isLoading, data, error, refetch] = GetRangeHappiness(
    true,
    userID,
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
  // console.log(stMonth);
  // console.log(endMonth);

  // fetches data for monthly view
  const [isLoadingM, dataM, errorM, refetchM] = GetRangeHappiness(
    true,
    userID,
    stMonth.toLocaleDateString("sv").substring(0, 10),
    endMonth.toLocaleDateString("sv").substring(0, 10)
  );
  useEffect(() => {
    refetchM();
  }, [stMonth, endMonth]);

  const [card, setCard] = useState();
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  const formattedDate = new Date().toLocaleDateString('en-US', options);


  const [selectedIndex, setSelectedIndex] = useState(0);

  if (USE_NEW_UI) {
    return (
      <Box>
        <Box className="flex flex-row">
          {/* Scrollabe date view would go here */}
          <Box className="flex flex-col w-32  h-screen mt-8 border-red-500 border-solid" />
          {/* Entry and comments box */}
          <Box className="flex flex-col">

          </Box>
          <Box className="flex flex-col mt-16 w-full mx-8" >
            {/* Date */}
            <h3 className="subheader">{formattedDate}</h3>
            {/* Public entry and edit button */}
            <Box className="flex flex-row   pt-8">
              <h1 className="header1">Your Public Entry</h1>
              <Box className="flex-1" />
              <Button startIcon={<EditIcon />}>Edit Entry</Button>
            </Box>
            {/* Happiness score and entry box */}
            <Box className="mt-6 flex flex-row">
              <Box className="flex flex-col items-center w-4/12">
                <h4 className="body1 mb-4">Happiness Score</h4>
                <h1 className="header1">7.5</h1>
              </Box>
              <Box className="w-1/12" />
              <Box className="w-7/12 p-4">
                <h4 className="body1">Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibu
                </h4>
              </Box>

            </Box>
            {/* Comments */}
            <Box className="flex flex-row max-w-[620px]">
              <Box className="flex flex-row overflow-x-auto py-1">
                {Array(10).fill(0).map((_, i) => <CommentCard
                  comment={"This is such a good story haha!"}
                  commenterAvatar={"https://happinessapp.s3.us-east-2.amazonaws.com/20230712144115_30c8c858-32f1-40a2-b9b1-8f20945e24c6.jpg"}
                  groupName={"Cornell"}
                  commentDate={"12/31"}
                  commenter={"Fiddle01"}
                  key={i}
                />)}
              </Box>
            </Box>
            {/* Journal title and button */}
            <Box className="flex flex-row ">
              <h3 className="header1" >Journal</h3>
              <Box className="flex flex-1" />
              <Button  > Lock</Button>
            </Box>
          </Box>

        </Box>

      </Box>

    )
  }
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
            {isLoading || isLoadingU ? (
              <Spinner animation="border" />
            ) : (
              <>
                {error || errorU ? (
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
                        <Histories dataList={data} userList={[user]} />
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
                <div className="flex-start justify-center  w-full max-w-[550px] shadow-xl">
                  <div className="font-medium relative w-full text-center text-2xl py-2 my-0 bg-buff-200 max-h-[60px]">
                    <button
                      type="button"
                      className="absolute top-3 left-4 w-[50px] h-[40px] rounded-lg text-cultured-50 bg-raisin-600 text-xl"
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
                      className="absolute top-3 right-4 w-[50px] h-[40px] rounded-lg text-cultured-50 bg-raisin-600 text-xl"
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
                  {isLoadingM || isLoadingU ? (
                    <Spinner animation="border" />
                  ) : (
                    <>
                      {errorM || errorU ? (
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
              {isLoadingM || isLoadingU ? (
                <Spinner animation="border" />
              ) : (
                <>
                  {errorM || errorU ? (
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
                            {card && <BigHistoryCard data={card} user={user} />}

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
