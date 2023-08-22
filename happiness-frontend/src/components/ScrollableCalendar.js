import * as React from "react";

import { useUser } from "../contexts/UserProvider";
import { useMemo } from "react";
import { useInfiniteQuery } from "react-query";
import { useApi } from "../contexts/ApiProvider";
import HappinessCard from "./HappinessCard";
import { formatDate } from "../pages/SubmitHappiness";
import { Spinner } from "react-bootstrap";
import InfiniteScroll from "react-infinite-scroll-component";

export default function ScrollableCalendar() {
  const { user: userState } = useUser();
  const api = useApi();

  // let oldestDate = new Date();

  // ***use date instead of count***
  const fetcher = ({ page = 1 }) =>
    api.get("/happiness/count", { page: page }).then((res) => {
      res.data.page = page;
      return res.data;
    });

  const { isLoading, data, error, fetchNextPage, hasNextPage } =
    useInfiniteQuery(["happiness calendar"], fetcher, {
      getNextPageParam: (lastPage) => {
        if (lastPage.length === 0) return false; // detect if last page is reached (no more entries)
        return lastPage.page + 1; // increment page number to fetch
      },
    });

  const allEntries = useMemo(
    () =>
      data?.pages.reduce((acc, page) => {
        return [...acc, ...page];
      }),
    [data]
  );

  const loadingSpinner = (
    <div className="m-3">
      <Spinner animation="border" />
      <p className="mt-2">Loading entries...</p>
    </div>
  );

  console.log(data);
  console.log(!!hasNextPage);

  return (
    <div className="h-full max-w-[175px] overflow-auto">
      {isLoading ? (
        <Spinner animation="border" />
      ) : (
        <>
          {error ? (
            <p className="text-xl font-medium text-raisin-600 m-3">
              Error: Could not load happiness data.
            </p>
          ) : (
            <InfiniteScroll
              dataLength={allEntries ? allEntries.length : 0}
              next={() => fetchNextPage()}
              hasMore={!!hasNextPage}
              loader={loadingSpinner}
            >
              {allEntries.map((entry) => (
                <HappinessCard
                  key={entry.id}
                  data={entry}
                  click={() => console.log(entry.id)}
                />
              ))}
            </InfiniteScroll>
          )}
        </>
      )}
    </div>
  );
}
