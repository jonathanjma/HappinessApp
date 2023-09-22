import EditIcon from "@mui/icons-material/Edit";
import { Box, Button, Typography } from "@mui/material";
import { useEffect, useMemo, useRef, useState } from "react";
import { Spinner } from "react-bootstrap";
import { useInfiniteQuery, useQuery } from "react-query";
import CommentCard from "../components/CommentCard";
import ScrollableCalendar from "../components/ScrollableCalendar";
import { useApi } from "../contexts/ApiProvider";
import { formatDate } from "./SubmitHappiness";

export default function Entries() {
  const options = { year: "numeric", month: "long", day: "numeric" };
  const readableDateFormat = (d) => d.toLocaleDateString("en-US", options);
  const api = useApi();
  const [selectedEntry, setSelectedEntry] = useState(0);
  const [currentHappinessId, setCurrentHappinessId] = useState(-1);
  // use negative ids for days with no happiness entry
  let counter = useRef(-1);

  // happiness data fetch function
  // where every page represents one week of happiness data
  //  (where days with missing entries are filled of blank entries)
  const fetcher = async (page) => {
    const start = new Date(
      new Date().getFullYear(),
      new Date().getMonth(),
      new Date().getDate() - 7 * page
    );
    const end = new Date(
      new Date().getFullYear(),
      new Date().getMonth(),
      new Date().getDate() - 7 * (page - 1) - (page > 1 ? 1 : 0)
    );

    const res = await api.get("/happiness/", {
      start: formatDate(start),
      end: formatDate(end),
    });

    console.log("Data from " + formatDate(start) + " fetched");

    let itr = new Date(start);
    while (itr <= end) {
      // create empty happiness entry for submitted days
      if (res.data.findIndex((x) => x.timestamp === formatDate(itr)) === -1) {
        res.data.push({
          id: counter.current,
          timestamp: formatDate(itr),
        });
        counter.current--;
      }
      itr.setDate(itr.getDate() + 1);
    }
    // reverse sort days
    res.data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    // add page attribute so page number is remembered
    return {
      data: res.data,
      page: page,
    };
  };

  // infinite query for fetching happiness
  const happinessResult = useInfiniteQuery(
    ["happiness calendar"],
    ({ pageParam = 1 }) => fetcher(pageParam),
    {
      getNextPageParam: (lastPage) => {
        // return false if last page
        return lastPage.page + 1; // increment page number to fetch
      },
    }
  );

  // combine all entries in React Query pages object
  const allEntries = useMemo(
    () =>
      happinessResult.data?.pages.reduce((acc, page) => {
        return [...acc, ...page.data];
      }, []),
    [happinessResult.data]
  );

  const onEntrySelected = (i) => {
    setSelectedEntry(i);
  };

  useEffect(() => {
    setCurrentHappinessId(allEntries ? allEntries[selectedEntry]?.id : -1);
  }, [selectedEntry]);
  useEffect(() => {
    if (currentHappinessId >= 0) {
      commentsResult.refetch();
    }
  }, [currentHappinessId]);
  const commentsResult = useQuery(
    [`happinessComments ${currentHappinessId}`],
    () => {
      if (currentHappinessId >= 0) {
        return api
          .get(`/happiness/${currentHappinessId}/comments`)
          .then((res) => res.data);
      }
    }
  );
  useEffect(() => {
    console.log("COMMENTS DATA \n\n");
    console.log(`${commentsResult.data}\n\n`);
  }, [commentsResult.data]);

  const Comments = () => {
    if (
      commentsResult.isLoading ||
      commentsResult.isError ||
      commentsResult.data == null
    ) {
      return (
        <>
          <Spinner />
        </>
      );
    }

    return (
      <Box className="overflow-auto h-full">
        {commentsResult.data.map((item) => (
          <CommentCard
            comment={item.text}
            commenter={item.author.username}
            commenterAvatar={item.author.profile_picture}
            groupName={"Cornell"} // TODO get the actual group
            commentDate={item.timestamp}
            key={item.id}
          />
        ))}
      </Box>
    );
  };

  const CommentHeader = () => {
    if (
      commentsResult.isLoading ||
      commentsResult.isError ||
      commentsResult.data == null
    ) {
      return (
        <>
          <h5 className="h5 border-solid border-[#E4E0E0] border-b-2 border-x-0 border-t-0 py-0.5">
            Comments
          </h5>
        </>
      );
    }
    return (
      <h5 className="h5 border-solid border-[#E4E0E0] border-b-2 border-x-0 border-t-0 py-0.5">
        {`Comments (${commentsResult.data.length})`}
      </h5>
    );
  };

  return (
    <Box className="flex flex-row h-screen overflow-hidden ">
      {/* Scrollable date view goes here */}
      <Box className="flex flex-col w-1/6 flex-1 mt-8 pb-8" id="scrollableDiv2">
        <ScrollableCalendar
          isLoading={happinessResult.isLoading}
          allEntries={allEntries}
          error={happinessResult.error}
          fetchNextPage={happinessResult.fetchNextPage}
          hasNextPage={happinessResult.hasNextPage}
          onEntrySelected={onEntrySelected}
          selectedEntry={selectedEntry}
          scrollableTarget={"scrollableDiv"}
        />
      </Box>
      <Box></Box>

      {happinessResult.isLoading ? (
        <Spinner />
      ) : (
        <Box
          className={
            "flex flex-col w-full items-stretch bg-white rounded-2xl mt-8 mx-8 shadow-heavy"
          }
        >
          {/* date, public entry, score, comment, and edit button are here */}
          <Box className="flex flex-col mt-8 mx-8 h-1/12 flex-1">
            {/* Date */}

            {/* Public entry and edit button */}
            <Box className="flex flex-row">
              <Typography className="body1">
                You don't have a private entry
              </Typography>
              <Box width={12} />
              <Box>
                <p
                  className="clickable-text underline leading-4 hover:cursor-pointer"
                  onClick={() => {
                    console.log("navigate to journal");
                  }}
                >
                  Create a private entry
                </p>
              </Box>
            </Box>
            <Box className="flex flex-row pt-4">
              <Box className="flex flex-col">
                <Typography variant="h5" className=" font-medium ">
                  Public Entry
                </Typography>
                <Typography className="subheader">
                  {readableDateFormat(
                    new Date(allEntries[selectedEntry].timestamp)
                  )}
                </Typography>
              </Box>
              <Box className="flex-1" />
              <Button
                className="bg-[#F7EFD7] py-3 pl-3 normal-case clickable-text rounded-xl shadow-medium text-sm"
                startIcon={<EditIcon />}
              >
                Edit Entry
              </Button>
            </Box>
            {/* Happiness score and entry box */}
            <Box className="mt-6 flex flex-row w-full">
              <Box className="w-20 h-20 items-center justify-center flex flex-col ">
                <h1 className="score-text">
                  {allEntries[selectedEntry].value}
                </h1>
              </Box>
              <Box className="ml-6 flex-1 ">
                <h4 className="body1">{allEntries[selectedEntry].comment}</h4>
              </Box>
            </Box>
          </Box>
          {/* Comments */}
          <Box className="flex flex-col mx-8 mt-8 h-[58%]">
            <CommentHeader />
            <Box
              className="w-full h-[calc(100vh-200px)] border-1 overflow-auto"
              height={500}
            >
              <Comments />
            </Box>
          </Box>
        </Box>
      )}
    </Box>
  );
}
