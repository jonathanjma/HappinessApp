import { useState } from "react";
import Stat from "../components/Stat";
import Users from "../components/Users";

function Profile(props) {
  return (
    <>
      <p className="text-center text-4xl font-medium m-4">Profile</p>
      <div className="flex flex-wrap justify-center items-center m-4">
        <img
          className="justify-center rounded-full min-h-[300px] min-w-[300px] max-w-[300px] block mx-auto h-24 rounded-full sm:mx-0 sm:shrink-0"
          src={Users()[props.id].img}
        />
      </div>
      <p className="text-center text-2xl font-medium m-2">
        {Users()[props.id].name}
      </p>
      <div className="flex justify-center">
        <div className="min-w-[375px] max-w-[375px] min-h-[178px] flex justify-center items-center m-2 p-2 max-w-sm bg-white rounded-xl shadow-lg">
          <div className="space-y-2">
            <p className="text-xl text-black font-semibold text-center">
              Today's Happiness
            </p>
            <p className="text-3xl text-slate-500 font-medium text-center">
              {7.5}
            </p>
          </div>
        </div>
      </div>
      <div className="flex flex-wrap justify-center items-center">
        <Stat val={0} />
        <Stat val={1} />
      </div>
    </>
  );
}

export default Profile;
