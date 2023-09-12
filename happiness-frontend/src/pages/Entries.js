import {Box, Button, unstable_ClassNameGenerator} from "@mui/material";
import ScrollableCalendar from "../components/ScrollableCalendar";
import EditIcon from "@mui/icons-material/Edit";
import CommentCard from "../components/CommentCard";
import {useEffect, useMemo, useRef, useState} from "react";
import {useApi} from "../contexts/ApiProvider";
import {formatDate} from "./SubmitHappiness";
import {useInfiniteQuery, useQueries, useQuery} from "react-query";
import {Spinner} from "react-bootstrap";
import SideScrollingComments from "../components/SideScrollingComments";

export default function Entries() {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const readableDateFormat = (d) => d.toLocaleDateString('en-US', options);
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
    const happinessResult =
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
            happinessResult.data?.pages.reduce((acc, page) => {
                return [...acc, ...page.data];
            }, []),
        [happinessResult.data]
    );

    const onEntrySelected = (i) => {
        setSelectedEntry(i);
    }

    useEffect(() => {
        setCurrentHappinessId(allEntries ? allEntries[selectedEntry]?.id : -1)
    }, [selectedEntry])
    useEffect(() => {
        if (currentHappinessId >= 0) {
            commentsResult.refetch();
        }
    }, [currentHappinessId])
    const commentsResult = useQuery( 
        [`happinessComments ${currentHappinessId}`],
        () => {
            if (currentHappinessId >= 0) {
                return api.get(`/happiness/${currentHappinessId}/comments`).then((res) => res.data)
            }
        },
    )
    useEffect(() => {
        console.log("COMMENTS DATA \n\n")
        console.log(`${commentsResult.data}\n\n`) 
    }, [commentsResult.data]) 

    // useEffect(() => {
    //     if (!happinessResult.isLoading) {
    //         console.log(`HELLO \n\n\n${allEntries[selectedEntry]}\n\n\n`)
    //     }

    // }, [happinessResult.isLoading])
    
    return (
        <Box className="flex flex-row h-screen overflow-hidden">
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
            {happinessResult.isLoading ? <Spinner /> : <Box className={"flex flex-col overflow-x-auto w-full items-stretch "}>
                {/* date, public entry, score, comment, and edit button are here */}
                <Box className="flex flex-col mt-8 mx-8 h-1/12" >
                    {/* Date */}
                    <h3 className="subheader">{readableDateFormat(new Date(allEntries[selectedEntry].timestamp))}</h3>
                    {/* Public entry and edit button */}
                    <Box className="flex flex-row pt-8">
                        <h1 className="header1">Your Public Entry</h1>
                        <Box className="flex-1" />
                        <Button startIcon={<EditIcon />}>Edit Entry</Button>
                    </Box>
                    {/* Happiness score and entry box */}
                    <Box className="mt-6 flex flex-row ">
                        <Box className="flex flex-col items-center w-4/12">
                            <h4 className="body1 mb-4">Happiness Score</h4>
                            <h1 className="header1">{allEntries[selectedEntry].value}</h1>
                        </Box>
                        <Box className="w-1/12" />
                        <Box className="w-7/12 p-4">
                            <h4 className="body1">
                                {allEntries[selectedEntry].comment}
                            </h4>
                        </Box>
                    </Box> 
                </Box>
                {/* Comments */}
                <SideScrollingComments className="ps-8 pt-6" commentsResult={commentsResult} />
                {/* Journal title and button */}
                <Box className="flex flex-row mx-8 pt-8">
                    <h3 className="header1" >Journal</h3>
                    <Box className="flex flex-1" />
                    <Button>Lock</Button>
                </Box>
            </Box>}
        </Box>
    )
}