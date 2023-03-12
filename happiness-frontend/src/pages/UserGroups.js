import GroupCard from "../components/GroupCard";
import NewGroupModal from "../components/NewGroupModal";
import { useQuery } from "react-query";
import { useApi } from "../components/ApiProvider";
import { Spinner } from "react-bootstrap";

// User Groups Page: view all the groups the user is in
export default function UserGroups({ id }) {
  const api = useApi();
  const { isLoading, isError, data, error } = useQuery("user_groups", () =>
    api.get("/user/groups").then((res) => res.body)
  );

  // if (!isLoading && data.length === 1) {
  //   data.push(data[0]);
  // }

  return (
    <div className="flex flex-col items-center">
      <div className="flex flex-wrap w-full justify-center">
        <p className="text-center w-full text-4xl font-medium text-raisin-600 m-3">
          Your Groups
        </p>
        <div className="flex md:absolute right-32 self-center">
          <NewGroupModal />
        </div>
      </div>
      {isLoading ? (
        <Spinner animation="border" />
      ) : (
        <>
          {data.length === 0 ? (
            <p className="text-xl font-medium text-raisin-600 m-3">
              You are not a member of any groups.
            </p>
          ) : (
            <div className={"grid md:grid-cols-" + Math.min(data.length, 3)}>
              {data.map((group) => (
                <GroupCard key={group.id} data={group} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
