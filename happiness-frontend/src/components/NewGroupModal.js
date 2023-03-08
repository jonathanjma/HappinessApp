import { Button } from "react-bootstrap";
import Form from "react-bootstrap/Form";
import InputField from "../components/InputField";
import React, { useRef, useState } from "react";
import Modal from "react-bootstrap/Modal";

export default function NewGroupModal() {
  const [show, setShow] = useState(false);
  const [formErrors, setFormErrors] = useState({});
  const nameField = useRef();

  const onSubmit = (ev) => {
    ev.preventDefault();
    const groupName = nameField.current.value;

    const errors = {};
    if (!groupName) {
      errors.name = "Group Name must not be empty.";
    }
    setFormErrors(errors);
    if (Object.keys(errors).length > 0) return;

    // do an api call

    setShow(false);
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
              error={formErrors.name}
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
