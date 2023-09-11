import {Box, Button, unstable_ClassNameGenerator} from "@mui/material";
import ScrollableCalendar from "../components/ScrollableCalendar";
import EditIcon from "@mui/icons-material/Edit";
import CommentCard from "../components/CommentCard";
import {useEffect, useMemo, useRef, useState} from "react";
import {useApi} from "../contexts/ApiProvider";
import {formatDate} from "./SubmitHappiness";
import {useInfiniteQuery} from "react-query";
import {Spinner} from "react-bootstrap";

export default function Entries() {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const readableDateFormat = (d: Date) => d.toLocaleDateString('en-US', options);
    const api = useApi();
    const [selectedEntry, setSelectedEntry] = useState(0);
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

    const onEntrySelected = (i) => {
        setSelectedEntry(i);
    }

    useEffect(() => {
        if (!isLoading) {
            console.log(`HELLO \n\n\n${allEntries[selectedEntry]}\n\n\n`)
        }

    }, [isLoading])
    return (
        <Box className="flex flex-row overflow-hidden">
            {/* Scrollable date view goes here */}
            <Box className="flex flex-col w-1/6  h-screen mt-8">
                <Box className={"flex-1 flex overflow-auto pb-20"}>
                    <ScrollableCalendar
                        isLoading={isLoading}
                        allEntries={allEntries}
                        error={error}
                        fetchNextPage={fetchNextPage}
                        hasNextPage={hasNextPage}
                        onEntrySelected={onEntrySelected}
                    />

                </Box>
            </Box>
            {isLoading ? <Spinner /> : <Box className={"flex flex-col overflow-x-auto w-full border-solid border-blue-500 items-stretch "}>
                {/* date, public entry, score, comment, and edit button are here */}
                <Box className="flex flex-col mt-8 mx-8 border-red-500 border-solid h-1/12" >
                    {/* Date */}
                    <h3 className="subheader">{readableDateFormat(allEntries[selectedEntry].timestamp)}</h3>
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
                            <h1 className="header1">7.5</h1>
                        </Box>
                        <Box className="w-1/12" />
                        <Box className="w-7/12 p-4">
                            <h4 className="body1">Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibu
                            </h4>
                        </Box>
                    </Box>
                </Box>
                {/* Comments */}
                <Box className="flex flex-row pt-6 pb-1 overflow-x-auto ps-8">
                    {Array(10).fill(0).map((_, i) =>
                        <CommentCard
                            comment={"This is such a good story haha!"}
                            commenterAvatar={"https://happinessapp.s3.us-east-2.amazonaws.com/20230712144115_30c8c858-32f1-40a2-b9b1-8f20945e24c6.jpg"}
                            groupName={"Cornell"}
                            commentDate={"12/31"}
                            commenter={"Fiddle01"}
                            key={i}
                        />)
                    }
                </Box>
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