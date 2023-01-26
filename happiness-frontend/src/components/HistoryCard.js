import Users from "./Users";

function CommentShow(props) {
  if (Users(props.id).data[props.index].pubComment) {
    return (
      <>
        <div className="items-center justify-center px-4 pb-3">
          <p className="text-center text-xl font-medium m-2 text-raisin-600">
            Comment
          </p>
          <p className="text-center text-rhythm-500 font-medium text-center">
            {/* Current placeholder - will eventually put happy face/sad face depending on happiness level*/}
            {Users(props.id).data[props.index].pubComment}
          </p>
        </div>
      </>
    );
  }
}

export default function HistoryCard(props) {
  console.log(props);
  return (
    <>
      <div className="w-full justify-center items-center min-h-[175px] max-w-[295px] mx-2 mt-4 bg-cultured-50 rounded-xl shadow-lg space-y-2">
        <div className="flex w-full justify-center items-center bg-buff-300 py-3 rounded-t-xl">
          <p className="text-center text-2xl font-medium text-raisin-600 w-2/3">
            Friday, {Users(props.id).data[props.index].date}
          </p>
          <div className="justify-center">
            <img
              className="justify-center rounded-full max-h-[50px] max-w-[50px] block mx-auto h-24 rounded-full sm:mx-0 sm:shrink-0"
              src={Users(props.id).img}
              alt="face based on happiness level, implement later"
            />
          </div>
        </div>
        <div className="w-full items-center justify-center bg-cultured-50 rounded-xl">
          <div className="flex justify-center px-4">
            <p className="text-center text-2xl font-medium m-2 text-raisin-600 mt-3">
              Happiness: {Users(props.id).data[props.index].level}
            </p>
          </div>
          <CommentShow id={props.id} index={props.index} />
        </div>
      </div>
    </>
  );
}
