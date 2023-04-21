import { Button } from "react-bootstrap";
import Form from "react-bootstrap/Form";
import InputField from "../components/InputField";
import React, { useRef, useState } from "react";
import Modal from "react-bootstrap/Modal";
import { useApi } from "../contexts/ApiProvider";

export default function NewGroupModal() {
  const [show, setShow] = useState(false);
  const [nameError, setNameError] = useState("");
  const nameField = useRef();
  const api = useApi();

  const onSubmit = (ev) => {
    ev.preventDefault();
    const groupName = nameField.current.value;

    if (!groupName) {
      setNameError("Group Name must not be empty.");
      return;
    }

    api
      .post("/group/", {
        name: groupName,
      })
      .then(() => {
        // setShow(false);
        window.location.reload();
      });
  };

  return (
    <>
      <Button onClick={() => setShow(true)}>Create Group</Button>
      <Modal show={show} onHide={() => setShow(false)}>
        <Modal.Header>
          <p className="text-xl font-medium text-raisin-600 mb-0">
            Create a Group
          </p>
        </Modal.Header>

        <Modal.Body>
          <Form onSubmit={onSubmit} className="p-2 pt-0">
            <InputField
              name="text"
              label="Group Name"
              placeholder="Enter a group name"
              error={nameError}
              fieldRef={nameField}
            />
            <Button type="submit" className="mt-3">
              Create Group
            </Button>
          </Form>
        </Modal.Body>
      </Modal>
    </>
  );
}
