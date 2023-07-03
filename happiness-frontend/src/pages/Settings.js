import ToggleSettingCard from "../components/ToggleSettingCard";
import { statSettings } from "../resources/StatSettings";
import { accountSettings } from "../resources/AccountSettings";
import ButtonSettingCard from "../components/ButtonSettingCard";
import { useUser } from "../contexts/UserProvider";
import React, { useState, useRef } from "react";
import { useMutation } from "react-query";
import { Button } from "react-bootstrap";
import InputField from "../components/InputField";
import { useApi } from "../contexts/ApiProvider";

export default function Settings() {
  const { user } = useUser();
  const api = useApi();
  const [settingToggleMap] = useState(new Map());
  user.user.settings.forEach((setting) => {
    settingToggleMap.set(setting.key, setting.enabled);
  });

  // below code for testing notif set
  console.log(settingToggleMap)
  const [notifError, setNotifError] = useState("");
  const addTimeField = useRef();
  const [isChecked, setIsChecked] = useState(Boolean(!settingToggleMap.has("Email Notifications")
  ? false
  : settingToggleMap.get("Email Notifications")));

  const submitTime = (ev) => {
    let newTime = addTimeField.current.value;
    console.log(newTime);
    api.post("/user/settings/", {
      "key": "Email Notifications",
      "enabled": isChecked,
      "value": newTime
    })
  }

  const toggleMutation = useMutation({
    mutationFn: (enabled) => {
        return api.post("/user/settings/", {
            "key": "Email Notifications",
            "enabled": !enabled
        })
    },
  })
  const handleChange = () => {
    console.log("ACTIVATED CHANGE")
    let wasFound = false
    console.log(user.user.settings)


    setIsChecked(!isChecked)
    user.user.settings.forEach((s) => {
        if (s.key === "Email Notifications") {
            s.enabled = !isChecked
            wasFound = true;
            console.log(`User settings after change: ${user.user.settings}`)
        }
    })
    if (!wasFound) {
        user.user.settings.push({
            "enabled": !isChecked,
            "key": "Email Notifications",
            "value": 2200 // default but set to something else if needed
        })
    }
    toggleMutation.mutate(isChecked)
}

// ORIGINAL CODE BELOW

  return (
    <>
      {/* <p className="text-3xl font-semibold text-raisin-600 ml-10 mb-4 mt-3">
        Account Settings
      </p>
      <div className="flex justify-left flex-wrap">
        {accountSettings.map((setting) => {
            console.log(`id: ${setting.id}`)
          return (
            <ButtonSettingCard
              key={setting.id}
              id={setting.id}
              name={setting.name}
              icon={setting.icon}
              isSensitive={setting.isSensitive}
            />
          );
        })}
      </div> */}
      <p className="text-3xl font-semibold text-raisin-600 ml-10 mb-4 mt-3">
        Statistics Settings
      </p>
      <div className="flex justify-left flex-wrap">
        {statSettings.map((setting) => {
          return (
            <ToggleSettingCard
              key={setting.id}
              name={setting.name}
              icon={setting.icon}
              defaultCheck={
                !settingToggleMap.has(setting.name)
                  ? false
                  : settingToggleMap.get(setting.name)
              }
            />
          );
        })}
      </div>

      {/* Following code for testing email notification setting */}
      <p className="text-3xl font-semibold text-raisin-600 ml-10 mb-4 mt-3">
        Notifications
      </p>
      <div className="w-[600px] h-[170px] md:h-[250px] m-2 py-8 px-8 max-w-lg rounded-xl shadow-lg space-y-2 sm:py-4 sm:flex-wrap sm:items-center sm:space-y-0 sm:space-x-6 bg-white">
      <div className="h-[100px]">
        <p className="text-xl">Email Notifications</p>

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
      <div className="flex justify-left flex-wrap">
        <InputField
                name="text"
                placeholder="Notification time"
                error={notifError}
                fieldRef={addTimeField}
        />
        <Button onClick={submitTime}>Set</Button>
      </div>
      <p className="text-xl">Current Notification Time: {user.user.settings[6].value}</p>
    </div>
    </>
  );
}
