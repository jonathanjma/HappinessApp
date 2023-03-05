// TODO: Rewrite with date code once backend integrated

function MonthItem(props) {
  return (
    <>
      <div className="w-full flex flex-wrap justify-center h-[60px] max-w-[40px] bg-cultured-50 rounded-sm">
        <div className="w-full h-[18px]">
          <p className="text-center text-sm font-medium text-raisin-600">
            {props.day}
          </p>
        </div>
        {/* The color for the box below can change depending on happiness value */}
        <div className="w-full bg-buff-200 h-[35px]">
          <p className="text-center text-lg font-medium text-raisin-600">
            {props.value}
          </p>
        </div>
      </div>
    </>
  );
}

function WeekItem(props) {
  const tiles = [];
  let i = props.start;
  let limit = Math.min(i + 7, 31);
  for (let b = 0; b < props.day; b++) {
    tiles.push(<div></div>);
  }
  for (i; i + props.day < limit; i++) {
    tiles.push(<MonthItem day={i} value={7.5} />);
  }
  return (
    <>
      <div className=" w-[305px] grid grid-cols-7 divide-x-2 divide-y-2">
        {tiles}
      </div>
    </>
  );
}

export default function MonthView(props) {
  return (
    <>
      <div className="flex w-full justify-center">
        <div className="flex flex-wrap justify-center border-solid w-[307px]">
          <p className="w-full text-center text-2xl py-2 my-0 bg-buff-200">
            {props.month} {props.year}
          </p>
          <div className="border-solid w-[307px] rounded-sm">
            <WeekItem start={1} day={props.startday} />
            <WeekItem start={8 - props.startday} day={0} />
            <WeekItem start={15 - props.startday} day={0} />
            <WeekItem start={22 - props.startday} day={0} />
            <WeekItem start={29 - props.startday} day={0} />
            {36 - props.startday < 32 ? (
              <WeekItem start={36 - props.startday} day={0} />
            ) : (
              <></>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
