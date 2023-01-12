import Stat from "../components/Stat";
import Users from "../components/Users";
import Graph from "../components/Graph";

export default function Profile(props) {
  return (
    <>
      <p className="text-center text-4xl font-medium m-4 text-raisin-600">
        Profile
      </p>
      <div className="flex flex-wrap justify-center m-4">
        <div className="flex flex-wrap w-full justify-center min-w-[330px] max-w-[600px] min-h-[200px] m-4 py-8 px-8 bg-cultured-50 rounded-xl shadow-lg space-y-2">
          <div className="py-2 px-4">
            <img
              className="justify-center rounded-full min-h-[150px] min-w-[150px] max-w-[150px] block mx-auto h-24 rounded-full sm:mx-0 sm:shrink-0"
              src={Users(props.id).img}
              alt="profile"
            />
          </div>
          <div className="py-2 px-4">
            <p className="text-center text-2xl font-medium m-2 text-raisin-600">
              {Users(props.id).name}
            </p>
            <p className="text-center text-raisin-600">Member since 1/5/22</p>
            <p className="text-center text-lg font-medium m-2 text-raisin-600">
              Friends
            </p>
            <p className="text-lg text-center text-raisin-600">
              {Users(props.id).friends.length}
            </p>
          </div>
          <div className="flex">
            <div className="space-y-2 px-4">
              <p className="text-xl text-raisin-600 font-semibold text-center">
                Today's Happiness
              </p>
              <p className="text-3xl text-rhythm-500 font-medium text-center">
                {7.5}
              </p>
            </div>
            <div className="space-y-2 px-4">
              <p className="text-xl text-raisin-600 font-semibold text-center">
                Weekly Average
              </p>
              <p className="text-3xl text-rhythm-500 font-medium text-center">
                {5.75}
              </p>
            </div>
            <div className="space-y-2 px-4">
              <p className="text-xl text-raisin-600 font-semibold text-center">
                Days Tracked
              </p>
              <p className="text-3xl text-rhythm-500 font-medium text-center">
                {8}
              </p>
            </div>
          </div>
        </div>
      </div>
      <div className="flex flex-wrap justify-center items-center">
        <div className="flex flex-wrap justify-center items-center max-w-[400px]">
          <Graph index={[props.id]} time="My Weekly" id={props.id} />
        </div>
        <div className="flex flex-wrap justify-center items-center md:max-w-[250px] sm:max-w-[400px] -mx-2">
          <Stat val={0} id={props.id} />
          <Stat val={1} id={props.id} />
        </div>
      </div>
    </>
  );
}
