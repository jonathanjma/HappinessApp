// month value represents month (0-based index, Jan = 0, Feb = 1, etc)

export default function MonthView({
  happinessData,
  startDay,
  endDay,
  setCard,
}) {
  function ReturnColor(level) {
    let happiness = level * 10;
    if (happiness < 10) {
      return "bg-red-700";
    } else if (happiness < 20) {
      return "bg-red-600";
    } else if (happiness < 30) {
      return "bg-yellow-500";
    } else if (happiness < 40) {
      return "bg-yellow-400";
    } else if (happiness < 60) {
      return "bg-yellow-300";
    } else if (happiness < 70) {
      return "bg-yellow-300";
    } else if (happiness < 80) {
      return "bg-green-400";
    } else if (happiness < 100) {
      return "bg-green-500";
    } else {
      return "bg-green-600";
    }
  }

  function MonthItem({ day, data }) {
    return (
      <>
        <div className="w-full flex flex-wrap justify-center h-[60px] md:h-[100px] bg-cultured-50 rounded-sm">
          <div className="hidden md:block w-full md:h-1/4 justify-center">
            <p className="text-center text-sm sm:text-md md:text-lg font-medium lg:text-raisin-600">
              {day}
            </p>
          </div>
          {/* The color for the box below can change depending on happiness value */}
          {data !== undefined ? (
            <>
              <div
                className={
                  ReturnColor(data.value) +
                  " flex w-full justify-center items-center h-full md:h-3/4"
                }
                onClick={() => setCard(data)}
              >
                <p className="md:hidden text-center text-lg sm:text-xl md:text-2xl font-medium text-raisin-600 pt-3">
                  {day}
                </p>
                <p className="hidden md:block text-center text-lg sm:text-xl md:text-2xl font-medium text-raisin-600 pt-2.5">
                  {data.value < 10 ? data.value.toFixed(1) : data.value}
                </p>
              </div>
            </>
          ) : (
            <div className="bg-buff-50 flex w-full justify-center items-center h-full md:h-3/4">
              <p className="md:hidden text-center text-lg sm:text-xl md:text-2xl font-medium text-raisin-600 pt-3">
                {day}
              </p>
            </div>
          )}
        </div>
      </>
    );
  }
  function findData(begin, end, data, ind) {
    let t = [];
    // console.log(end);
    for (let i = begin; i < end; i++) {
      if (ind === data.length) break;
      // console.log(i);
      // console.log(data[ind]);
      let parts = data[ind].timestamp.split("-");
      let a = new Date(parts[0], parts[1] - 1, parts[2]);
      // console.log(a);
      // console.log(a.getDate());
      if (a.getDate() === i) {
        t.push(data[ind]);
        ind++;
      } else t.push(undefined);
    }
    return [t, ind];
  }
  function WeekItem({ start, day, data }) {
    // console.log(data);
    // console.log(start);
    const tiles = [];
    let i = start;
    let t = 0;
    let limit = Math.min(i + 7, endDay.getDate() + 1);
    for (let b = 0; b < day; b++) {
      tiles.push(<th></th>);
    }
    for (i; i + day < limit; i++) {
      if (data[t] !== undefined) {
        tiles.push(
          <>
            <th className="border border-raisin-600 border-collapse">
              <MonthItem day={i} data={data[t]} />
            </th>
          </>
        );
      } else
        tiles.push(
          <>
            <th className="border border-raisin-600 border-collapse">
              <MonthItem day={i} value={undefined} />
            </th>
          </>
        );
      t++;
    }
    return <>{tiles}</>;
  }
  let tiles = [];
  // console.log(happinessData);
  // console.log(startDay);
  happinessData.sort((a, b) => a.timestamp - b.timestamp);
  // console.log(findData(1, 8 - startDay.getDay(), happinessData, 0));
  let [wkData, indx] = findData(1, 8 - startDay.getDay(), happinessData, 0);
  tiles.push(
    <>
      <tr>
        <WeekItem start={1} day={startDay.getDay()} data={wkData} />
      </tr>
    </>
  );
  for (let d = 8 - startDay.getDay(); d < 32; d += 7) {
    [wkData, indx] = findData(d, d + 7, happinessData, indx);
    tiles.push(
      <>
        <tr>
          <WeekItem start={d} day={0} data={wkData} />
        </tr>
      </>
    );
  }
  return (
    <table className="table-fixed w-full rounded-sm border-collapse border border-raisin-600">
      <tbody>{tiles}</tbody>
    </table>
  );
}
