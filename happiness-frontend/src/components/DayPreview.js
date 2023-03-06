import OldHistoryCard from "./OldHistoryCard";
import { Fragment, useRef, useState } from "react";
import { Dialog, Transition } from "@headlessui/react";
import Users from "./Users";

/* 
Things to implement:
- Arrows on either side of comment to show previous/next day's comment and happiness
*/

export default function DayPreview({
  open,
  setOpen,
  ids_list,
  day = 0,
  data = undefined,
}) {
  const cancelButtonRef = useRef(null);
  const handleShow = () => setOpen(true);

  const tiles = [];
  if (ids_list !== undefined) {
    for (let i = 0; i < ids_list.length; i++) {
      tiles.push(
        ids_list[i] === 0 ? (
          <OldHistoryCard id={1} data={Users(1).data[day]} shown={false} />
        ) : (
          <OldHistoryCard
            id={ids_list[i]}
            data={data === undefined ? Users(ids_list[i]).data[day] : data}
            shown={true}
          />
        )
      );
    }
  }

  return (
    <>
      <Transition.Root show={open} as={Fragment}>
        <Dialog
          as="div"
          className="relative z-10"
          initialFocus={cancelButtonRef}
          onClose={() => setOpen(false)}
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
            <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center md:p-0">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                enterTo="opacity-100 translate-y-0 sm:scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 translate-y-0 sm:scale-100"
                leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              >
                <Dialog.Panel className="sm:w-full sm:max-w-xl">
                  <>
                    {tiles}
                    <div className="mx-3 max-w-[576px]">
                      <button
                        type="button"
                        className="mt-3 inline-flex w-full justify-center text-raisin-600 rounded-md border border-gray-300 bg-cultured-50 px-4 py-2 text-base font-medium shadow-sm hover:bg-tangerine-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                        onClick={() => setOpen(false)}
                        ref={cancelButtonRef}
                      >
                        Close
                      </button>
                    </div>
                  </>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition.Root>
    </>
  );
}
