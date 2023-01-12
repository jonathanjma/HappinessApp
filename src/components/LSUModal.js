import React, {useState} from "react";
import Modal from "react-bootstrap/Modal";
import LSUForm from "./LSUForm";

export default function LSUModel() {
  const [show, setShow] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(true); //TODO use this
  const isLoggedIn = false;

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);
  const goToHomePage = () => {}; //TODO implement function
  const updateLogin = () => {
    setIsLoggingIn(!isLoggingIn);
  };

  return (
    <>
      <button
        onClick={isLoggedIn ? goToHomePage : handleShow}
        className="flex-1 scale-150 text-white bg-gradient-to-r from-raisin-500 via-raisin-600 to-raisin-700 shadow-lg
        font-roboto font-semibold rounded-lg text-sm px-5 outline-none
        py-2.5 text-center mr-2 mb-2 mt-9"
      >
        Submit
      </button>

      <Modal
        show={show}
        onHide={handleClose}
        backdrop="static"
        keyboard={false}
      >
        <Modal.Header>
          <p className="font-semibold font-sans text-2xl">
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
            className="bg-raisin-500 hover:bg-raisin-400 text-white font-semibold py-2 px-4 rounded duration-500"
            onClick={handleClose}
          >
            Close
          </button>
        </Modal.Footer>
      </Modal>
    </>
  );
}
