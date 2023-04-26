import React, { useState } from "react";
import Modal from "react-bootstrap/Modal";
import LSUForm from "./LSUForm";

export default function LSUModal() {
  const [show, setShow] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(true); //TODO use this

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  return (
    <>
      <button
        className=" bg-gradient-to-br from-tangerine-50 to-raisin-50 hover:scale-110 hover:drop-shadow-xl hover:bg-raisin-400 drop-shadow-md duration-200 rounded-md mb-15"
        onClick={handleShow}
      >
        <div className="m-2 text-3xl hover:anime-gradient hover:font-bold font-semibold">
          Show Me More
        </div>
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
            onClick={() => {
              setIsLoggingIn(!isLoggingIn);
            }}
          >
            {isLoggingIn ? "or sign up" : "or login"}
          </a>
        </Modal.Header>

        <Modal.Body>
          <LSUForm isLoggingIn={isLoggingIn} />
        </Modal.Body>
        <Modal.Footer>
          <a className="mr-auto underline" onClick={() => {}} href={"/reset-pass"}>
            Forgot your password?
          </a>
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
