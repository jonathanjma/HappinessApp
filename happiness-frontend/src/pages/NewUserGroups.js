import NewGroupCard from "../components/groups/NewGroupCard";
import { useQuery } from "react-query";
import { useApi } from "../contexts/ApiProvider";
import { Button, CircularProgress } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import React from "react";

// User Groups Page: view all the groups the user is in
export default function NewUserGroups() {
  const api = useApi();
  const { isLoading, data, error } = useQuery("user_groups", () =>
    api.get("/user/groups").then((res) => res.data)
  );

  return (
    <div className="flex flex-col items-center">
      <div className="flex w-full justify-content-between mb-4">
        <p className="text-4xl font-medium m-0">Your Groups</p>
        <div className="self-center">
          <Button
            variant="outlined"
            className="border-slate-400 text-black normal-case gap-2.5 px-2"
          >
            <AddIcon />
            Create Group
          </Button>
        </div>
      </div>
      {isLoading ? (
        <CircularProgress sx={{ color: "black" }} />
      ) : (
        <>
          {error ? (
            <p className="text-xl font-medium m-3">
              Error: Could not load groups.
            </p>
          ) : (
            <>
              {data.length === 0 ? (
                <p className="text-xl font-medium m-3">
                  You are not a member of any groups.
                </p>
              ) : (
                <div className="grid md:grid-cols-2 gap-6 w-full">
                  {data.map((group) => (
                    <NewGroupCard key={group.id} data={group} />
                  ))}
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}
