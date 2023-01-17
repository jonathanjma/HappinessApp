import HistoryCard from "./HistoryCard";
import LineChart from "./LineChart";
import { Fragment, useRef, useState } from "react";
import { Dialog, Transition } from "@headlessui/react";

/* 
Things to implement:
- Arrows on either side of comment to show previous/next day's comment and happiness
- allow DayPreview to show multiple HistoryCards (when multiple users have the same happiness on the same day)
*/

export default function DayPreview({ open, setOpen, id, index }) {
  const cancelButtonRef = useRef(null);
  const handleShow = () => setOpen(true);

  return (
    <>
      <Transition.Root show={open} as={Fragment}>
        <Dialog
          as="div"
          className="relative z-10"
          initialFocus={cancelButtonRef}
          onClose={setOpen}
        >
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-buff-100 bg-opacity-75 transition-opacity" />
          </Transition.Child>

          <div className="fixed inset-0 z-10 overflow-y-auto">
            <div className="flex min-h-full items-end justify-center p-4 text-center md:items-center md:p-0">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                enterTo="opacity-100 translate-y-0 sm:scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 translate-y-0 sm:scale-100"
                leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              >
                <Dialog.Panel className="relative transform overflow-hidden rounded-xl bg-white text-left m-4 shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-3xl">
                  <div className="flex justify-center mb-4">
                    <HistoryCard id={id} index={index} />
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition.Root>
    </>
  );
}
