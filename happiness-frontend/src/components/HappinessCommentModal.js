import React, { useState } from "react";
import Modal from "react-bootstrap/Modal";
import LSUForm from "./LSUForm";
import Journal from "../media/journal-icon.svg";
import JournalQuestion from "../media/journal-question-icon.svg";

export default function HappinessCommentModal(props) {
  const [show, setShow] = useState(false);
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  return (
    <>
      <button
        type="button"
        onClick={handleShow}
        className="text-white bg-raisin-300 hover:bg-raisin-400 focus:ring-4 focus:outline-none font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center mr-2 mt-3"
      >
        <img
          src={
            props.comment
              ? Journal
              : JournalQuestion /* TODO probably doesn't actually work */
          }
          aria-hidden="true"
          className="w-5 h-5 mr-2 -ml-1"
          viewBox="0 0 20 20"
        />
        Add journal entry
      </button>

      <Modal
        show={show}
        onHide={handleClose}
        backdrop="static"
        keyboard={false}
      >
        <Modal.Header>
          <p className="font-semibold font-sans text-2xl">
            Submit a journal entry for today:
          </p>
        </Modal.Header>

        <Modal.Body>
          <div className="mb-6">
            <label
              htmlFor="large-input"
              className="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
            >
              Large input
            </label>
            <textarea
              id="large-input"
              value={props.comment}
              className="block w-full p-4 bg-gray-100 rounded focus:border-blue-500 outline-none focus:border-raisin-200 border-2 focus:border-4"
              onChange={(e) => {
                props.setComment(e.target.value);
              }}
            />
          </div>
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
