import React, { useState } from "react";
import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";
import LSUForm from "./LSUForm";

export default function LSUModel() {
  const [show, setShow] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(true); //TODO use this
  const isLoggedIn = false;

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);
  const goToHomePage = () => {};
  const updateLogin = () => {
    setIsLoggingIn(!isLoggingIn);
  };

  return (
    <>
      <Button
        variant="primary"
        onClick={isLoggedIn ? goToHomePage : handleShow}
        className="flex-1 scale-150 text-white bg-gradient-to-r from-blue-500 via-blue-600 to-blue-700
        hover:bg-gradient-to-br focus:ring-4 focus:outline-none focus:ring-blue-300 dark:focus:ring-blue-800 shadow-lg
        shadow-blue-500/50 dark:shadow-lg dark:shadow-blue-800/80 font-roboto font-semibold rounded-lg text-sm px-5
        py-2.5 text-center mr-2 mb-2 mt-9"
      >
        Submit
      </Button>

      <Modal
        show={show}
        onHide={handleClose}
        backdrop="static"
        keyboard={false}
      >
        <Modal.Header>
          <p className="font-semibold font-roboto font-sans text-2xl">
            {isLoggingIn ? "Login" : "Sign Up"}
          </p>
          <a
            href="#"
            className="underline hover:text-gray-700"
            onClick={updateLogin}
          >
            {isLoggingIn ? "or sign up" : "or login"}
          </a>
        </Modal.Header>

        <Modal.Body>
          <LSUForm isLoggingIn={isLoggingIn} />
        </Modal.Body>
        <Modal.Footer>
          <button
            className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded duration-500"
            onClick={handleClose}
          >
            Close
          </button>
        </Modal.Footer>
      </Modal>
    </>
  );
}
