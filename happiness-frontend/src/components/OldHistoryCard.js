import Users from "./Users";

function CommentShow({ data }) {
  if (data.pubComment) {
    return (
      <>
        <div className="items-center justify-center px-4 pb-3">
          <p className="text-center text-xl font-medium mt-2 text-raisin-600">
            Comment
          </p>
          <p className="text-center text-rhythm-500 font-medium">
            {data.pubComment}
          </p>
        </div>
      </>
    );
  }
}

export default function OldHistoryCard({ id, data, shown = false, useDate = true }) {
  return (
    <>
      {shown ? <div className="@xl:flex w-full justify-center min-h-[175px] max-w-[650px] mx-3 mt-4 bg-cultured-50 rounded-xl shadow-lg space-y-2">
        <div className="flex w-full flex-wrap justify-center items-center bg-buff-300 @xl:h-full @xl:w-1/2 px-2 py-3 min-w-[215px] @xl:rounded-none @xl:rounded-l-xl rounded-t-xl">
          <p className="text-center text-xl md:text-2xl font-medium text-raisin-600 w-2/3 pt-3">
            {useDate ? <>Friday, {data.date}</> : <>{Users(id).name}</>}
          </p>
          <div className="justify-center @xl:w-full">
            <img
              className="justify-center rounded-full max-h-[50px] max-w-[50px] @xl:max-w-[60px] @xl:max-h-[60px] block mx-auto h-24 sm:mx-0 sm:shrink-0"
              src={Users(id).img}
              alt="face based on happiness level, implement later"
            />
          </div>
        </div>
        <div className="w-full justify-center">
          <div className="flex justify-center px-4">
            <p className="text-center text-2xl font-medium m-2 text-raisin-600 mt-3">
              Happiness: {data.level}
            </p>
          </div>
          <CommentShow data={data} />
        </div>
      </div> : <></>}
    </>
  );
}
