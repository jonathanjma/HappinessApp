import React, { useEffect } from 'react'
import ConfirmModal from './ConfirmModal'
import { useState } from 'react';
import { useMutation } from 'react-query';
import { Modal, Spinner, Button } from 'react-bootstrap';
import { useApi } from '../contexts/ApiProvider';

export default function ImagePicker() {
  const [showing, setShowing] = useState(false);
  const [imgFile, setImgFile] = useState(null);
  const api = useApi();

  const sendImageMutation = useMutation({
    mutationFn: (value) => {
      const formData = new FormData();
      formData.append("file", value)

      return api.post("/user/pfp/", formData)
    },
  })
  const ModalBody = () => {
    if (sendImageMutation.isLoading) {
      return <Spinner />
    } else {
      return (
        <div className='flex flex-col'>
          <input type='file' onChange={(e) => { setImgFile(e.target.files[0]) }} />
          <p>{sendImageMutation.isError ? "Error submitting file" : ""}</p>
          {/* TODO might not need this since modal will hide after confirming a success */}
          <p>{sendImageMutation.isSuccess ? "Successfully sent request" : ""}</p>
        </div>
      )
    }
  }

  const handleClose = () => {
    setShowing(false);
  }
  const handleConfirm = () => {
    sendImageMutation.mutate(imgFile);
  }
  useEffect(() => {
    if (sendImageMutation.isSuccess) {
      setShowing(false);
    }
  }, [sendImageMutation])

  setTimeout(() => {
    setShowing(true)
  }, 1000)
  return (
    <>
      <Modal show={showing} onHide={handleClose}>
        <Modal.Header>
          <Modal.Title>Select an image from your files.</Modal.Title>
        </Modal.Header>
        <Modal.Body><ModalBody /></Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Cancel
          </Button>
          <Button variant="outline-danger" onClick={handleConfirm}>
            Continue
          </Button>
        </Modal.Footer>
      </Modal>
    </>

  )
}
