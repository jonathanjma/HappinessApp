import { useParams } from "react-router-dom";
import GroupData from "./GroupData";
import InputField from "./InputField";
import { Button, Card, CloseButton, Image } from "react-bootstrap";
import Form from "react-bootstrap/Form";
import React, { useRef, useState } from "react";
import Users from "./Users";

export default function GroupManage({ id }) {
  const { groupID } = useParams();
  const groupData = GroupData(groupID);
  const groupUsersI = groupData.users.map((user) => Users(user));
  const [groupUsers, setGroupUsers] = useState(groupUsersI);

  const [formErrors, setFormErrors] = useState({});
  const nameField = useRef();
  const addUserField = useRef();

  const submitName = (ev) => {
    ev.preventDefault();
    const groupName = nameField.current.value;

    const errors = {};
    if (!groupName) {
      errors.name = "Group Name must not be empty.";
    }
    setFormErrors(errors);
    if (Object.keys(errors).length > 0) return;

    // do an api call
  };

  const submitUser = (ev) => {
    ev.preventDefault();
    const newUser = addUserField.current.value;

    const errors = {};
    if (!newUser) {
      errors.user = true;
    }
    setFormErrors(errors);
    if (Object.keys(errors).length > 0) return;

    // do an api call
    for (let i = 1; i <= 6; i++) {
      if (Users(i).name === newUser) {
        setGroupUsers([...groupUsers, Users(i)]);
        break;
      }
    }
  };

  console.log(Users(0));

  const removeUser = (id) => {
    setGroupUsers(groupUsers.filter((user) => user.id !== id));
  };

  return (
    <div className="flex flex-col items-center">
      <Form onSubmit={submitName} className="max-w-[500px]">
        <div className="flex">
          <p className="m-0 me-3 text-xl">Edit Group Name</p>
          <InputField
            name="text"
            placeholder="Enter a new name"
            error={formErrors.name}
            fieldRef={nameField}
          />
          <Button type="submit" className="ms-3 align-self-start">
            Update
          </Button>
        </div>
      </Form>
      <p className="text-2xl font-medium m-3 text-raisin-600">Edit Users</p>
      <div className="grid md:grid-cols-4">
        {/* List current group members */}
        {groupUsers.map((user) => (
          <Card body className="m-1.5 p-1">
            <div className="flex">
              <Image
                src={user.img}
                roundedCircle
                className="max-w-[30px] max-h-[30px] me-3"
              />
              <p className="grow m-0 text-2xl">{user.name}</p>
              <CloseButton
                className="justify-content-end align-self-center ms-2"
                onClick={() => removeUser(user.id)}
              />
            </div>
          </Card>
        ))}

        {/* Add new user input */}
        <Card body className="m-1.5">
          <Form onSubmit={submitUser} className="max-w-[200px]">
            <div className="flex">
              <InputField
                name="text"
                placeholder="User to add"
                error={formErrors.user}
                fieldRef={addUserField}
              />
              <Button type="submit" className="ms-2 align-self-start">
                +
              </Button>
            </div>
          </Form>
        </Card>
      </div>
    </div>
  );
}
