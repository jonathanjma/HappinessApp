import { useState } from "react";
function CommentShow({ data }) {
  if (data.comment) {
    return (
      <>
        <div className="items-center justify-center px-4 pb-3">
          <p className="text-center text-rhythm-500 font-medium">
            {data.comment}
          </p>
        </div>
      </>
    );
  }
}

export default function BigHistoryCard({ data, user }) {
  const parts = data.timestamp.split("-");
  const dayString = new Date(parts[0], parts[1] - 1, parts[2]);
  const [clicked, setClick] = useState(true);
  // console.log(dayString);
  return (
    <>
      <div className="@xl:flex w-full justify-center min-h-[175px] max-w-[700px] min-w-[285px] mt-4 bg-cultured-50 rounded-xl shadow-lg space-y-2">
        <div className="flex w-full flex-wrap justify-center items-center bg-buff-300 @xl:h-full @xl:w-1/2 px-2 py-3 min-w-[215px] @xl:rounded-none @xl:rounded-l-xl rounded-t-xl">
          <div
            className="relative w-full text-center @xl:h-[135px] @xl:flex @xl:flex-wrap @xl:items-center @xl:justify-center text-2xl font-medium text-raisin-600 py-2"
            onClick={() => setClick(!clicked)}
          >
            {clicked
              ? dayString.toDateString().slice(0, 3) +
                ", " +
                data.timestamp.slice(5).split("-").join("/")
              : user.username}
            <div className="absolute @xl:relative @xl:w-full @xl:mt-4 right-2 top-0">
              <img
                className="rounded-full max-h-[50px] max-w-[50px] @xl:max-w-[60px] @xl:max-h-[60px] block mx-auto sm:mx-0 sm:shrink-0"
                title={user.username}
                src={user.profile_picture}
                alt="pfp"
              />
            </div>
          </div>
        </div>
        <div className="w-full justify-center">
          <div className="flex justify-center px-4">
            <p className="text-center text-2xl font-medium m-2 text-raisin-600 mt-3">
              Happiness: {data.value}
            </p>
          </div>
          <CommentShow data={data} />
        </div>
      </div>
    </>
  );
}
