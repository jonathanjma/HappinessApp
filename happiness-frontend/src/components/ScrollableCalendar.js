import * as React from "react";

import { useMemo, useRef } from "react";
import { useInfiniteQuery } from "react-query";
import { useApi } from "../contexts/ApiProvider";
import HappinessCard from "./HappinessCard";
import { formatDate } from "../pages/SubmitHappiness";
import { Spinner } from "react-bootstrap";
import InfiniteScroll from "react-infinite-scroll-component";

export default function ScrollableCalendar({isLoading, error, allEntries, fetchNextPage, hasNextPage, onEntrySelected}) {
    /*
    const api = useApi();

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
  const { isLoading, data, error, fetchNextPage, hasNextPage } =
    useInfiniteQuery(
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
      data?.pages.reduce((acc, page) => {
        return [...acc, ...page.data];
      }, []),
    [data]
  );
     */

  const loadingSpinner = (
    <div className="m-3">
      <Spinner animation="border" />
      <p className="mt-2">Loading entries...</p>
    </div>
  );

  return (
    <div className="h-full w-[130px] overflow-auto ms-2">
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
            >
              {allEntries.map((entry, index) => (
                <HappinessCard
                  key={entry.id}
                  data={entry}
                  click={() => {
                      onEntrySelected(index)
                  }}
                />
              ))}
            </InfiniteScroll>
          )}
        </>
      )}
    </div>
  );
}
