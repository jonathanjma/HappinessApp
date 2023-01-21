import { useState } from "react";
import { useEffect } from "react";

export default function ToggleSettingCard(props) {
  /*
      props.id: setting id
      props.icon: setting icon
      props.name: setting name
      */
  const [isChecked, setIsChecked] = useState(false);
  useEffect(() => {
    //TODO update backend based on setting id
  }, [isChecked]);

  return (
    <div className="min-w-[300px] max-w-[350px] m-2 py-8 px-8 max-w-sm bg-white rounded-xl shadow-lg space-y-2 sm:py-4 sm:flex sm:items-center sm:space-y-0 sm:space-x-6 bg-white">
      <img
        className="h-[50px] w-[50px] block mx-auto sm:shrink-0 sm:mx-0"
        src={props.icon}
      />
      <p className="text-xl">{props.name}</p>

      <label className="relative inline-flex items-center cursor-pointer">
        <input
          type="checkbox"
          value={isChecked}
          className="sr-only peer"
          onClick={() => {
            setIsChecked(!isChecked);
          }}
        />
        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
      </label>
    </div>
  );
}
