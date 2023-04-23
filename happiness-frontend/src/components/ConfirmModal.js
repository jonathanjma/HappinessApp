import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";

// A reusable confirmation modal component
export default function ConfirmModal({
  heading,
  body,
  show,
  setShow,
  onConfirm,
}) {
  const handleClose = () => setShow(false);

  const handleConfirm = () => {
    setShow(false);
    onConfirm();
  };

  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header>
        <Modal.Title>{heading}</Modal.Title>
      </Modal.Header>
      <Modal.Body>{body}</Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Cancel
        </Button>
        <Button variant="outline-danger" onClick={handleConfirm}>
          Continue
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
