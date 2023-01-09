import { useState } from "react";
import Stat from "../components/Stat";
import Users from "../components/Users";

function Profile(props) {
  return (
    <>
      <div>
        <p></p>
      </div>
      <div>
        <img
          className="object-cover rounded-full h-[200px] w-[200px] block mx-auto h-24 rounded-full sm:mx-0 sm:shrink-0"
          src={Users()[props.id].img}
        />
      </div>
      <div>
        <Stat val={0} />
        <Stat val={1} />
      </div>
    </>
  );
}

export default Profile;
