import * as React from "react";

import { useMemo, useRef } from "react";
import { useInfiniteQuery } from "react-query";
import { useApi } from "../contexts/ApiProvider";
import HappinessCard from "./HappinessCard";
import { formatDate } from "../pages/SubmitHappiness";
import { Spinner } from "react-bootstrap";
import InfiniteScroll from "react-infinite-scroll-component";

export default function ScrollableCalendar({isLoading, error, allEntries, fetchNextPage, hasNextPage, onEntrySelected, selectedEntry, scrollableTarget}) {
  const loadingSpinner = (
    <div className="m-3">
      <Spinner animation="border" />
      <p className="mt-2">Loading entries...</p>
    </div>
  );

  return (
    <div className="h-full w-[130px] overflow-auto ms-2" id="scrollableDiv">
      {isLoading ? (
        <Spinner className="m-3" animation="border" />
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
