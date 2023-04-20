import LineChart from "./LineChart";
import DayPreview from "./DayPreview";
import { Fragment, useRef, useState } from "react";
import { Dialog, Transition } from "@headlessui/react";

export default function ChartPreview({
  chartData,
  open,
  setOpen,
  names,
  formatted,
}) {
  console.log(chartData);
  const cancelButtonRef = useRef(null);
  const handleShow = () => setOpen(true);
  const [dShow, setDShow] = useState(false);
  const [pointData, setPointData] = useState([[], 0]);

  const dayPreview = (
    <DayPreview
      open={dShow}
      setOpen={setDShow}
      data={pointData[0].map((e) => formatted[e][pointData[1]])}
      name={pointData[0].map((e) => names[e])}
    />
  );

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
            <div className="flex min-h-full items-end sm:items-center justify-center pb-4 -sm:pb-4 min-[400px]:p-2 text-center md:p-0">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                enterTo="opacity-100 translate-y-0 sm:scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 translate-y-0 sm:scale-100"
                leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              >
                <Dialog.Panel className="relative transform overflow-hidden rounded-xl bg-cultured-50 text-left sm:m-4 shadow-xl transition-all my-8 w-full sm:max-w-6xl">
                  <div className="flex w-full justify-center bg-cultured-50 px-2 sm:px-4 pt-3 pb-2 sm:p-6 sm:pb-4">
                    <div className="flex w-full sm:items-start justify-center">
                      <div className="w-full mt-3 sm:mt-0 sm:ml-4 sm:text-left">
                        <Dialog.Title
                          as="h3"
                          className="flex w-full justify-center font-medium text-xl leading-6 text-raisin-600"
                        >
                          Graph
                        </Dialog.Title>
                        <div className="flex w-full justify-center min-h-[400px] md:min-h-[450px] mt-2">
                          <LineChart
                            chartData={chartData}
                            dayShow={setDShow}
                            setPointData={setPointData}
                          />
                          {dayPreview}
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
                      Close
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
