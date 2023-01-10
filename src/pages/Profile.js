import Stat from "../components/Stat";
import Users from "../components/Users";
import Graph from "../components/Graph";

function Profile(props) {
  return (
    <>
      <p className="text-center text-4xl font-medium m-4 text-raisin-600">
        Profile
      </p>
      <div className="flex flex-wrap justify-center m-4">
        <div className="py-2 px-4">
          <p className="text-center text-2xl font-medium m-2 text-raisin-600">
            {Users()[props.id].name}
          </p>
          <p> Member since 1/5/22</p>
          <div>
            <p className="text-center text-lg font-medium m-2 text-raisin-600">
              Friends
            </p>
          </div>
        </div>
        <div className="py-2 px-4">
          <img
            className="justify-center rounded-full min-h-[200px] min-w-[200px] max-w-[200px] block mx-auto h-24 rounded-full sm:mx-0 sm:shrink-0"
            src={Users()[props.id].img}
            alt="profile"
          />
        </div>
      </div>
      <div className="flex justify-center">
        <div className=" flex min-w-[375px] max-w-[375px] min-h-[178px] justify-center items-center m-2 p-2 max-w-sm bg-white rounded-xl shadow-lg">
          <div className="space-y-2">
            <p className="text-xl text-raisin-600 font-semibold text-center">
              Today's Happiness
            </p>
            <p className="text-3xl text-rhythm-500 font-medium text-center">
              {7.5}
            </p>
          </div>
        </div>
      </div>
      <div className="flex flex-wrap justify-center items-center">
        <Graph index={[props.id]} time="Weekly" />
        <Stat val={0} />
        <Stat val={1} />
      </div>
    </>
  );
}

export default Profile;
