import LineChart from "./LineChart";
// export default function Preview({ chartData }) {
//   console.log(chartData);
//   return (
//     <>
//       <div
//         className="relative z-10"
//         aria-labelledby="modal-title"
//         role="dialog"
//         aria-modal="true"
//       >
//         <div className="fixed inset-0 z-10 overflow-y-auto">
//           <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
//             <div className="flex relative transform overflow-hidden justify-center rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-4xl">
//               <div className="flex bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4 max-w-fit">
//                 <div className="flex sm:flex sm:items-start">
//                   <div className="justify-center mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left max-w">
//                     <p className="flex w-full justify-center font-medium text-xl leading-6 text-raisin-600">
//                       Preview
//                     </p>
//                     <div className="flex w-full justfy-center min-h-[500px] min-w-[800px] mt-2">
//                       <LineChart chartData={chartData} />
//                     </div>
//                   </div>
//                 </div>
//               </div>
//             </div>
//           </div>
//         </div>
//       </div>
//       ;
//     </>
//   );
// }
import { Fragment, useRef, useState } from "react";
import { Dialog, Transition } from "@headlessui/react";

export default function Preview({ chartData }) {
  const [open, setOpen] = useState(false);
  const cancelButtonRef = useRef(null);
  const handleShow = () => setOpen(true);

  return (
    <>
      <div className="flex w-full justify-center" onClick={handleShow}>
        <LineChart chartData={chartData} />
      </div>
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
            <div className="fixed inset-0 bg-rhythm-400 bg-opacity-75 transition-opacity" />
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
                <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white text-left m-4 shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-6xl">
                  <div className="flex w-full justify-center bg-cultured-50 px-4 pt-3 pb-2 sm:p-6 sm:pb-4">
                    <div className="flex w-full sm:items-start justify-center">
                      <div className="w-full mt-3 sm:mt-0 sm:ml-4 sm:text-left">
                        <Dialog.Title
                          as="h3"
                          className="flex w-full justify-center font-medium text-xl leading-6 text-raisin-600"
                        >
                          Preview
                        </Dialog.Title>
                        <div className="flex w-full justify-center min-h-[550px] mt-2">
                          <LineChart chartData={chartData} />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
                    <button
                      type="button"
                      className="mt-3 inline-flex w-full justify-center text-raisin-600 rounded-md border border-gray-300 bg-cultured-50 px-4 py-2 text-base font-medium shadow-sm hover:bg-tangerine-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                      onClick={() => setOpen(false)}
                      ref={cancelButtonRef}
                    >
                      Cancel
                    </button>
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
