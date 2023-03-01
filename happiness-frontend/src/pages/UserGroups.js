// Groups system - group creation, invites, view your group's happiness + graph
import Users from "../components/Users";
import GroupCard from "../components/GroupCard";
import GroupData from "../components/GroupData";
import NewGroupModal from "../components/NewGroupModal";

export default function UserGroups({ id }) {
  const userGroups = Users(id).group;

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
      {userGroups.length === 0 ? (
        <p className="text-xl font-medium text-raisin-600 m-3">
          You are not a member of any groups.
        </p>
      ) : (
        <div className="grid md:grid-cols-3">
          {userGroups.map((group) => (
            <GroupCard key={group} id={group} data={GroupData(group)} />
          ))}
        </div>
      )}
    </div>
  );
}
