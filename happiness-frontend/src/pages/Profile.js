import Stat from "../components/Stat";
import Users from "../components/Users";
import Graph from "../components/Graph";
import Histories from "../components/Histories";
import DayPreview from "../components/DayPreview";
import { useState } from "react";

export default function Profile(props) {
  const [dShow, setDShow] = useState(false);
  const dayPreview = (
    <DayPreview
      open={dShow}
      setOpen={setDShow}
      ids_list={[props.id]}
      data={Users(props.id).data[Users(props.id).data.length - 1]}
    />
  );
  return (
    <>
      <div className="flex flex-wrap justify-center">
        <div className="lg:w-3/4 sm:w-full">
          <div>
            <p className="text-center text-5xl font-medium m-3 text-raisin-600">
              Profile
            </p>
          </div>
          <div className="flex flex-wrap justify-center items-center">
            <div className="flex flex-wrap justify-center min-w-[330px] max-w-[600px] min-h-[200px] m-4 bg-cultured-50 rounded-xl shadow-lg space-y-2">
              <div className="relative flex flex-wrap justify-center w-full bg-buff-300 rounded-t-xl">
                <div className="absolute -sm:absolute sm:relative left-4 top-4 sm:flex items-center md:px-4 md:w-1/3 sm:mx-4">
                  <img
                    className="mb-4 justify-center max-w-[65px] max-h-[65px] sm:min-h-[125px] sm:max-h-[125px] sm:min-w-[125px] sm:max-w-[125px] block mx-auto rounded-full sm:mx-0 sm:shrink-0"
                    src={Users(props.id).img}
                    alt="profile"
                  />
                </div>
                <div className="w-full justify-end sm:w-1/2 py-2 px-4">
                  <p className="text-center text-2xl font-medium m-2 text-raisin-600">
                    {Users(props.id).name}
                  </p>
                  <p className="text-center text-raisin-600">
                    Member since 1/5/22
                  </p>
                  <div className="flex flex-wrap justify-center items-center @container">
                    <div className="justify-center">
                      <p className="text-center text-raisin-600 text-md font-medium m-2 sm:w-1/3">
                        Friends
                      </p>
                      <p className="text-lg text-center text-raisin-600 m-2">
                        {Users(props.id).friends.length}
                      </p>
                    </div>
                    <div className="w-3/8">
                      <p className="text-md text-raisin-600 font-medium text-center m-2">
                        Weekly Average
                      </p>
                      <p className="text-lg text-raisin-600 text-center m-2">
                        {5.75}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex m-4">
                {Users(props.id).data[Users(props.id).data.length - 1].level ? (
                  <div className="space-y-2 px-2 md:px-4">
                    <p className="text-md md:text-lg text-raisin-600 font-semibold text-center">
                      Today's Happiness
                    </p>
                    <p className="text-2xl md:text-3xl text-rhythm-500 font-medium text-center">
                      {
                        Users(props.id).data[Users(props.id).data.length - 1]
                          .level
                      }
                    </p>
                  </div>
                ) : (
                  <></>
                )}
                {Users(props.id).data[Users(props.id).data.length - 1]
                  .pubComment ? (
                  <div
                    className="space-y-2 px-2 md:px-4 md:mx-4"
                    onClick={() => setDShow(true)}
                  >
                    <p className="text-md md:text-lg text-raisin-600 font-semibold text-center">
                      Comment
                    </p>
                    <p className="line-clamp-3 -md:line-clamp-3 text-md md:text-lg text-rhythm-500 font-medium text-center">
                      {
                        Users(props.id).data[Users(props.id).data.length - 1]
                          .pubComment
                      }
                    </p>
                    {dayPreview}
                  </div>
                ) : (
                  <></>
                )}
              </div>
            </div>
            <div className="flex flex-wrap justify-center items-center">
              <div className="flex flex-wrap justify-center items-center m-4 md:ml-4 max-w-[400px] max-h-[400px]">
                <Graph index={[props.id]} time="My Weekly" id={props.id} />
              </div>
              <div className="flex flex-wrap justify-center items-center md:max-w-[205px] sm:max-w-[400px] mr-2">
                <Stat val={0} id={props.id} />
                <Stat val={1} id={props.id} />
              </div>
            </div>
          </div>
        </div>
        <div className="justify-center lg:w-1/4 w-full max-w-[550px]">
          <div>
            <p className="text-center text-5xl font-medium m-3 text-raisin-600">
              History
            </p>
          </div>
          <Histories id={props.id} max={4} division={false} />
        </div>
      </div>
    </>
  );
}
