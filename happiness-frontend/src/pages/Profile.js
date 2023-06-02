import Stat from "../components/statGraphs/Stat";
import Graph from "../components/statGraphs/Graph";
import Histories from "../components/happinessHistory/Histories";
import DayPreview from "../components/statGraphs/DayPreview";
import { useState } from "react";
import { useQuery } from "react-query";
import { useUser } from "../contexts/UserProvider";
import { Spinner, Button } from "react-bootstrap";
import {
  PrevWeekData,
  GetCountHappiness,
} from "../components/happinessHistory/GetHappinessData";
import { useApi } from "../contexts/ApiProvider";
import { Link } from "react-router-dom";

export default function Profile() {
  const { user: userState } = useUser();
  const me = userState.user;
  const today = new Date();
  const todayString = today.toISOString().substring(0, 10);
  const api = useApi();

  const {
    isLoading: isLoadingUG,
    data: dataUG,
    error: errorUG,
  } = useQuery("get user groups", () =>
    api.get("/user/groups").then((res) => res.data)
  );
  const [isLoadingH, dataH, errorH] = PrevWeekData(true, me.id);
  const [isLoadingC, dataC, errorC] = GetCountHappiness(4, me);

  let userCreated = "";
  if (me.created !== null) {
    // formatted date into array
    let forDa = new Date(me.created)
      .toLocaleDateString("sv")
      .substring(0, 10)
      .split("-");
    userCreated =
      "Member since " + forDa[1] + "/" + forDa[2] + "/" + forDa[0].substring(2);
  }
  const [dShow, setDShow] = useState(false);
  return (
    <>
      <div className="flex flex-wrap justify-center">
        <div className="lg:w-3/4 sm:w-full">
          <div>
            <p className="text-center text-4xl font-medium m-2 text-raisin-600">
              Profile
            </p>
          </div>
          <div className="flex flex-wrap justify-center items-center">
            <div className="flex flex-wrap justify-center min-w-[330px] max-w-[600px] min-h-[200px] mx-4 my-2 bg-cultured-50 rounded-xl shadow-lg space-y-2">
              <div className="relative flex flex-wrap justify-center w-full bg-buff-300 rounded-t-xl">
                <div className="absolute -sm:absolute sm:relative left-4 top-4 sm:flex items-center md:px-4 md:w-1/3 sm:mx-4">
                  <img
                    className="mb-4 justify-center max-w-[65px] max-h-[65px] md:min-h-[125px] md:max-h-[125px] md:min-w-[125px] md:max-w-[125px] block mx-auto rounded-full sm:mx-0 sm:shrink-0"
                    src={me.profile_picture}
                    alt="profile"
                  />
                </div>
                <div className="w-full justify-end sm:w-1/2 py-2 px-4">
                  <p className="text-center text-2xl font-medium m-2 text-raisin-600">
                    {me.username}
                  </p>
                  <p className="text-center text-raisin-600">{userCreated}</p>
                  <div className="flex flex-wrap justify-center items-center @container">
                    <div className="justify-center">
                      {isLoadingUG ? (
                        <Spinner animation="border" />
                      ) : (
                        <>
                          {errorUG ? (
                            <p className="text-md font-medium text-raisin-600 m-3">
                              Error: Could not load groups.
                            </p>
                          ) : (
                            <>
                              <Link to="/groups" className="no-underline">
                                <p className="text-center text-raisin-600 text-md font-medium m-2 sm:w-full">
                                  Groups: {dataUG.length}
                                </p>
                              </Link>
                            </>
                          )}
                        </>
                      )}
                      {/* <p className="text-lg text-center text-raisin-600 m-2">
                        3
                      </p> */}
                    </div>
                    {/* <div className="w-3/8">
                      <p className="text-md text-raisin-600 font-medium text-center m-2">
                        Weekly Average
                      </p>
                      <p className="text-lg text-raisin-600 text-center m-2">
                        {5.75}
                      </p>
                    </div> */}
                  </div>
                </div>
              </div>
              <div className="flex m-4">
                {isLoadingC ? (
                  <Spinner animation="border" />
                ) : (
                  <>
                    {errorC ? (
                      <p className="text-md font-medium text-raisin-600 m-3">
                        Error: Could not load happiness.
                      </p>
                    ) : (
                      <>
                        {dataC.length === 0 ? (
                          <p className="text-md font-medium text-raisin-600 m-3">
                            No happiness data available.
                          </p>
                        ) : (
                          <>
                            <div className="space-y-2 px-2 md:px-4">
                              {todayString.substring(0, 10) ===
                              dataC[0].timestamp ? (
                                <p className="text-md text-raisin-600 font-semibold text-center">
                                  Today's Happiness
                                </p>
                              ) : (
                                <p className="text-md text-raisin-600 font-semibold text-center">
                                  Recent Happiness
                                </p>
                              )}
                              <p className="text-2xl text-rhythm-500 font-medium text-center">
                                {dataC[0].value.toFixed(1)}
                              </p>
                            </div>
                            {dataC[0].comment ? (
                              <>
                                <DayPreview
                                  open={dShow}
                                  setOpen={setDShow}
                                  data={[dataC[0]]}
                                  users={[me]}
                                />
                                <div
                                  className="space-y-2 px-2 md:px-4 md:mx-4"
                                  onClick={() => setDShow(true)}
                                >
                                  <p className="text-md text-raisin-600 font-semibold text-center">
                                    Comment
                                  </p>
                                  <p className="line-clamp-3 -md:line-clamp-3 text-md text-rhythm-500 font-medium text-center">
                                    {dataC[0].comment}
                                  </p>
                                </div>
                              </>
                            ) : (
                              <></>
                            )}
                          </>
                        )}
                      </>
                    )}
                  </>
                )}
              </div>
            </div>
            <div className="flex flex-wrap justify-center items-center">
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
                          <div className="flex flex-wrap justify-center items-center m-4 md:ml-4 max-w-[400px] max-h-[400px]">
                            <Graph data={dataH} users={[me]} time="Weekly" />
                          </div>
                          <div className="flex flex-wrap justify-center items-center md:max-w-[205px] sm:max-w-[400px] mr-2">
                            <Stat
                              data={dataH.map((f) => f.value)}
                              key={0}
                              val={0}
                            />
                            <Stat
                              data={dataH.map((f) => f.value)}
                              key={1}
                              val={1}
                            />
                          </div>
                        </>
                      )}
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
        <div className="justify-center lg:w-1/4 w-full max-w-[550px]">
          <div>
            <p className="text-center text-4xl font-medium m-2 text-raisin-600">
              History
            </p>
          </div>
          {isLoadingC ? (
            <Spinner animation="border" />
          ) : (
            <>
              {errorC ? (
                <p className="text-md font-medium text-raisin-600 m-3">
                  Error: Could not load happiness.
                </p>
              ) : (
                <>
                  {dataC.length === 0 ? (
                    <p className="text-md font-medium text-raisin-600 m-3">
                      Data not available for selected period.
                    </p>
                  ) : (
                    <>
                      <Histories dataList={dataC} userList={[me]} />
                      <div className="m-3 flex justify-center">
                        <Link to="/history">
                          <Button variant="outline-secondary">show all</Button>
                        </Link>
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
