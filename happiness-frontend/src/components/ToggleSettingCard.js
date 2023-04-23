import {useEffect, useState} from "react";
import { useMutation } from "react-query";
import {useApi} from "../contexts/ApiProvider";
import {useUser} from "../contexts/UserProvider";

export default function ToggleSettingCard(props) {
    /*
      props.id: setting id
      props.icon: setting icon
      props.name: setting name
      */
    // console.log("Default check: " +  Boolean(props.defaultCheck))
    const [isChecked, setIsChecked] = useState(Boolean(props.defaultCheck));
    const api = useApi();
    const { user } = useUser();
    console.log(user.user.settings)

    const toggleMutation = useMutation({
        mutationFn: (value) => {
            return api.post("/user/settings/", {
                "key": props.name,
                "value": !value,
            })
        },
    })

    const handleChange = () => {
        console.log("ACTIVATED CHANGE")
        let wasFound = false
        console.log(user.user.settings)


        setIsChecked(!isChecked)
        user.user.settings.forEach((s) => {
            if (s.key === props.name) {
                s.value = !isChecked
                wasFound = true;
                console.log(`User settings after change: ${user.user.settings}`)
            }
        })
        if (!wasFound) {
            user.user.settings.push({
                "key": props.name,
                "value": !isChecked
            })
        }
        toggleMutation.mutate(isChecked)
    }
  return (
    <div className="w-[300px] h-[170px] md:h-[100px] m-2 py-8 px-8 max-w-sm rounded-xl shadow-lg space-y-2 sm:py-4 sm:flex sm:items-center sm:space-y-0 sm:space-x-6 bg-white">
      <img
        className="h-[50px] w-[50px] block mx-auto sm:shrink-0 sm:mx-0"
        src={props.icon}
      />
      <p className="text-xl">{props.name}</p>

      <label className="relative inline-flex items-center cursor-pointer">
        <input
          type="checkbox"
          checked={isChecked}
          className="sr-only peer"
          onChange={handleChange}
        />
        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
      </label>
    </div>
  );
}
