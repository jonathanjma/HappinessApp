// Groups system - group creation, invites, view your group's happiness + graph
import Users from "../components/Users";
import {Button, Stack} from "react-bootstrap";
import Form from "react-bootstrap/Form";
import InputField from "../components/InputField";
import {useRef, useState} from "react";
import GroupCard from "../components/GroupCard";
import GroupData from "../components/GroupData";

export default function UserGroups({ id }) {
  const [formErrors, setFormErrors] = useState({});
  const nameField = useRef();
  const usersField = useRef();
  const userGroups = Users(id).group;

  const onSubmit = (ev) => {
    ev.preventDefault();
    const groupName = nameField.current.value;
    const groupUsers = usersField.current.value;

    const errors = {};
    if (!groupName) {
      errors.name = "Group Name must not be empty.";
    }
    if (!groupUsers) {
      errors.users = "Group Users must not be empty.";
    }
    setFormErrors(errors);
    if (Object.keys(errors).length > 0) {
      return;
    }
  };

  return (
    <>
      <p className="text-center text-4xl font-medium m-3 text-raisin-600">
        Groups Page
      </p>
      <p className="text-center text-xl font-medium m-3 text-raisin-600">
        Create a New Group
      </p>
      <Form onSubmit={onSubmit}>
        <Stack direction="horizontal" gap={3}>
          <InputField
            name="text"
            label="Group Name"
            error={formErrors.name}
            fieldRef={nameField}
          />
          <InputField
            name="text"
            label="User IDs (comma seperated)"
            error={formErrors.users}
            fieldRef={usersField}
          />
        </Stack>
        <Button variant="outline-primary" type="submit">
          + Create Group
        </Button>
      </Form>
      <p className="text-center text-xl font-medium m-3 text-raisin-600">
        Your Groups
      </p>
      {userGroups.length === 0 ? (
        <p>You are not a member of any groups. Create one above!</p>
      ) : (
        <>
          {userGroups.map((group) => (
            <GroupCard key={group} id={group} data={GroupData(group)} />
          ))}
        </>
      )}
    </>
  );
}
