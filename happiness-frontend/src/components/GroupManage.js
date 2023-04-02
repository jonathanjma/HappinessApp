import InputField from "./InputField";
import { Button, Card, CloseButton, Image } from "react-bootstrap";
import Form from "react-bootstrap/Form";
import React, { useRef, useState } from "react";
import { useApi } from "../contexts/ApiProvider";

// Group Management: changing group name, adding and deleting group users
export default function GroupManage({ groupID, groupData }) {
  const api = useApi();
  const originalUsers = groupData.users.map((u) => u.username);
  const [groupUsers, setGroupUsers] = useState(groupData.users);

  const [nameError, setNameError] = useState();
  const [userAddError, setUserAddError] = useState();

  const nameField = useRef();
  const addUserField = useRef();

  // Input validation + API request to change group name
  const submitName = (ev) => {
    ev.preventDefault();
    const groupName = nameField.current.value;

    // Check that name input is non-empty
    if (!groupName) {
      setNameError("Name cannot be empty.");
      return;
    }

    api
      .put("/group/" + groupID, { new_name: groupName })
      .then(() => window.location.reload());
    // .error()
  };

  // Input validation for adding users (user is added locally only)
  const addUser = (ev) => {
    ev.preventDefault();
    const newUser = addUserField.current.value;

    // Check that user input is non-empty, user is not already in group, and user is valid
    if (!newUser) {
      setUserAddError("Username cannot be empty.");
    } else if (groupUsers.find((u) => u.username === newUser) !== undefined) {
      setUserAddError("User is already a member.");
    } else {
      api
        .get("/user/username/" + newUser)
        .then((res) => {
          setGroupUsers([...groupUsers, res.data]);

          setUserAddError();
          addUserField.current.value = "";
        })
        .catch((e) =>
          e.response.status === 404
            ? setUserAddError("User does not exist.")
            : ""
        );
    }
  };

  // Removes user (user is removed locally only)
  const removeUser = (username) => {
    setGroupUsers(groupUsers.filter((user) => user.username !== username));
  };

  // API request to update group users
  // TODO: show warning if user removes themselves or everyone in the group
  const submitUsers = (ev) => {
    let addedUsers = [];
    let removedUsers = [];

    let curUsers = groupUsers.map((u) => u.username);
    for (let username of curUsers) {
      if (!originalUsers.includes(username)) addedUsers.push(username);
    }
    for (let username of originalUsers) {
      if (!curUsers.includes(username)) removedUsers.push(username);
    }

    api
      .put("/group/" + groupID, {
        add_users: addedUsers,
        remove_users: removedUsers,
      })
      .then(() => window.location.reload());
    // .error()
  };

  return (
    <div className="flex flex-col items-center">
      {/* Change group name input */}
      <Form onSubmit={submitName} className="max-w-[500px]">
        <div className="flex">
          <p className="m-0 me-3 text-xl">Edit Group Name</p>
          <InputField
            name="text"
            placeholder="Enter a new name"
            error={nameError}
            fieldRef={nameField}
          />
          <Button type="submit" className="ms-3 align-self-start">
            Update
          </Button>
        </div>
      </Form>
      <p className="text-2xl font-medium m-3 text-raisin-600">Edit Users</p>
      <div className="grid md:grid-cols-3">
        {/* List current group members */}
        {groupUsers.map((user) => (
          <Card body key={user.id} className="m-1.5 p-1">
            <div className="flex">
              <Image
                src={user.profile_picture}
                roundedCircle
                className="max-w-[30px] max-h-[30px] me-3"
              />
              <p className="grow m-0 text-xl">{user.username}</p>
              <CloseButton
                className="justify-content-end align-self-center ms-2"
                onClick={() => removeUser(user.username)}
              />
            </div>
          </Card>
        ))}

        {/* Add new user input */}
        <Card body className="m-1.5">
          <Form onSubmit={addUser} className="max-w-[200px]">
            <div className="flex">
              <InputField
                name="text"
                placeholder="User to add"
                error={userAddError}
                fieldRef={addUserField}
              />
              <Button type="submit" className="ms-2 align-self-start">
                +
              </Button>
            </div>
          </Form>
        </Card>
      </div>
      <Button onClick={submitUsers} className="mt-3">
        Save Changes
      </Button>
    </div>
  );
}
