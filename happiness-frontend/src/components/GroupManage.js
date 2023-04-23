import InputField from "./InputField";
import { Button, Card, CloseButton, Image, Stack } from "react-bootstrap";
import Form from "react-bootstrap/Form";
import React, { useRef, useState } from "react";
import { useApi } from "../contexts/ApiProvider";
import { useUser } from "../contexts/UserProvider";
import ConfirmModal from "./ConfirmModal";
import { useNavigate } from "react-router-dom";

// Group Management: changing group name, adding and deleting group users, deleting group
export default function GroupManage({ groupID, groupData }) {
  const api = useApi();
  const { user: userState } = useUser();
  const navigate = useNavigate();
  const cur_user = userState.user;
  const originalUsers = groupData.users.map((u) => u.username);
  const [groupUsers, setGroupUsers] = useState(groupData.users);

  const [nameError, setNameError] = useState("");
  const [userAddError, setUserAddError] = useState("");
  const [otherError, setOtherError] = useState("");
  const [leaveShow, setLeaveShow] = useState(false);
  const [deleteShow, setDeleteShow] = useState(false);

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
      .then(() => window.location.reload())
      .catch(() => setNameError("Error updating name."));
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

          setUserAddError("");
          addUserField.current.value = "";
        })
        .catch(() => setUserAddError("User does not exist."));
    }
  };

  // Removes user (user is removed locally only)
  const removeUser = (username) => {
    setGroupUsers(groupUsers.filter((user) => user.username !== username));
  };

  // API request to update group users
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
      .then(() => window.location.reload())
      .catch(() => setOtherError("Error updating users."));
  };

  // API request to remove logged-in user from the group
  const leaveGroup = () => {
    api
      .put("/group/" + groupID, {
        remove_users: [cur_user.username],
      })
      .then(() => navigate("/groups"))
      .catch(() => setOtherError("Error leaving group."));
  };

  // API request to delete the group
  const deleteGroup = () => {
    api
      .delete("/group/" + groupID)
      .then(() => navigate("/groups"))
      .catch(() => setOtherError("Error deleting group."));
  };

  return (
    <div className="flex flex-col items-center">
      {otherError.length > 0 && (
        <p className="text-xl font-medium text-red-500">**{otherError}</p>
      )}
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
      <Stack
        direction="horizontal"
        gap={3}
        className="flex justify-content-center mt-3"
      >
        {/* Leave + Delete group buttons and confirmation dialogs */}
        <Button variant="danger" onClick={() => setLeaveShow(true)}>
          Leave Group
        </Button>
        <ConfirmModal
          heading="Leave Group"
          body="Are you sure you want to leave the group?"
          show={leaveShow}
          setShow={setLeaveShow}
          onConfirm={leaveGroup}
        />
        <Button variant="danger" onClick={() => setDeleteShow(true)}>
          Delete Group
        </Button>
        <ConfirmModal
          heading="Delete Group"
          body="Are you sure you want to delete the group? (No happiness data will be deleted.)"
          show={deleteShow}
          setShow={setDeleteShow}
          onConfirm={deleteGroup}
        />
      </Stack>
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
              {user.id !== cur_user.id && (
                <CloseButton
                  className="justify-content-end align-self-center ms-2"
                  onClick={() => removeUser(user.username)}
                  title="Remove user"
                />
              )}
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
