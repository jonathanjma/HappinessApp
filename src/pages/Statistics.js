import Graph from "../components/Graph";
import Stat from "../components/Stat";
import Users from "../components/Users";

function Statistics(props) {
  /*
  0 = mean
  1 = median
  2 = mode
  3 = range
  4 = standard deviation
  5 = minimum
  6 = q1
  7 = q3
  8 = maximum 
  */
  // future conversion to boolean array
  console.log(Users(props.id).friends.concat([props.id]));
  const datavals = [
    { value: true, key: 0 },
    { value: true, key: 1 },
    { value: false, key: 2 },
    { value: false, key: 3 },
    { value: false, key: 4 },
    { value: true, key: 5 },
    { value: false, key: 6 },
    { value: false, key: 7 },
    { value: true, key: 8 },
  ];
  return (
    <>
      <p className="text-center text-5xl font-medium m-4 text-raisin-600">
        Statistics
      </p>
      <div className="flex flex-wrap justify-center items-center">
        <Graph
          index={Users(props.id).friends.concat([props.id])}
          time="Weekly"
          id={props.id}
        />
        <Graph
          index={Users(props.id).friends.concat([props.id])}
          time="Monthly"
          id={props.id}
        />
      </div>
      <div className="flex flex-wrap justify-center items-center">
        {datavals.map((e) => {
          if (e.value) {
            return <Stat id={props.id} key={e.key} val={e.key} />;
          }
          return null;
        })}
      </div>
    </>
  );
}
export default Statistics;
