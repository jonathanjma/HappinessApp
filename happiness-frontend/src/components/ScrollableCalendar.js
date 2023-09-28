import * as React from "react";

import { useMemo, useRef } from "react";
import { useInfiniteQuery } from "react-query";
import { useApi } from "../contexts/ApiProvider";
import HappinessCard from "./HappinessCard";
import InfiniteScroll from "react-infinite-scroll-component";
import { CircularProgress } from "@mui/material";
import {formatDate} from "../util/Formatting";

export default function ScrollableCalendar({isLoading, error, allEntries, fetchNextPage, hasNextPage, onEntrySelected, selectedEntry}) {
  const loadingSpinner = (
    <div className="m-3">
      <CircularProgress sx={{ color: "black" }} />
      <p className="mt-2">Loading entries...</p>
    </div>
  );

  return (
    <div className="h-full w-[130px] overflow-auto ms-2" id="scrollableDiv">
      {isLoading ? (
        <CircularProgress className="m-3" sx={{ color: "black" }} />
      ) : (
        <>
          {error ? (
            <p className="text-xl font-medium text-raisin-600 m-3">
              Error: Could not load happiness data.
            </p>
          ) : (
            <InfiniteScroll
              dataLength={allEntries ? allEntries.length : 0}
              next={fetchNextPage}
              hasMore={!!hasNextPage}
              loader={loadingSpinner}
              scrollableTarget={"scrollableDiv"}
            >
              {allEntries.map((entry, index) => (
                <HappinessCard
                  key={entry.id}
                  data={entry}
                  click={() => {
                      onEntrySelected(index)
                  }}
                  selected={index === selectedEntry}
                />
              ))}
            </InfiniteScroll>
          )}
        </>
      )}
    </div>
  );
}
