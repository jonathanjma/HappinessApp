import {Tab} from "@headlessui/react";
import {Fragment} from "react";

export function TabButton({text}) {
    return (
        <Tab as={Fragment}>
            {({selected}) => (
                <button
                    className={
                        "inline-block px-2 py-2.5 m-1.5 w-[140px] rounded-lg " +
                        (selected
                            ? "text-cultured-50 bg-raisin-600"
                            : "hover:text-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 dark:hover:text-white")
                    }
                >
                    {text}
                </button>
            )}
        </Tab>
    );
}