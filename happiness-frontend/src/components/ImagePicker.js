import React from 'react'
import ConfirmModal from './ConfirmModal'

export default function ImagePicker() {
  const [showing, setShowing] = useState(false);
  setTimeout(() => {
    setShowing(true)
  }, 1000)
  return (
    <>
      <ConfirmModal
        heading={"Select an image from your files."}

      ></ConfirmModal>

      <input type='file'></input>
    </>

  )
}
