import Stat from "../statGraphs/Stat";
import Graph from "../statGraphs/Graph";

export default function GroupStats({ groupData, happinessData, selected }) {
  const users = groupData.users.sort((u1, u2) => u1.id - u2.id);

  /*
      0 = mean
      1 = median
      2 = mode
      3 = standard deviation
      4 = minimum
      5 = maximum
      */
  // future conversion to boolean array
  const datavals = [
    { value: true, key: 0 },
    { value: true, key: 1 },
    { value: true, key: 2 },
    { value: true, key: 3 },
    { value: true, key: 4 },
    { value: true, key: 5 },
  ];

  return (
    <div className="w-full lg:flex lg:flex-wrap justify-center">
      <div className="mt-4 -lg:mt-4 w-full lg:flex lg:flex-wrap justify-center items-start @container">
        {happinessData.length === 0 ? (
          <p className="text-xl font-medium text-raisin-600 m-3">
            Data not available for selected period.
          </p>
        ) : (
          <>
            <div className="lg:w-1/2 lg:mt-4">
              {/* TODO: doesn't rerender when week/month changed */}
              <Graph
                data={happinessData}
                users={users}
                time={selected === 1 ? "Weekly" : "Monthly"}
              />
            </div>
            <div className="flex flex-wrap justify-center items-start lg:w-1/2 xl:w-1/2">
              {datavals.map((e) => {
                if (e.value) {
                  return (
                    <Stat
                      data={happinessData.map((e) => e.value)}
                      key={e.key}
                      val={e.key}
                    />
                  );
                }
                return null;
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
