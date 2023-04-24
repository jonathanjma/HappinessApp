import ToggleSettingCard from "../components/ToggleSettingCard";
import { statSettings } from "../resources/StatSettings";
import { accountSettings } from "../resources/AccountSettings";
import ButtonSettingCard from "../components/ButtonSettingCard";
import { useUser } from "../contexts/UserProvider";
import React, { useState } from "react";

export default function Settings() {
  const { user } = useUser();
  const [settingValueMap] = useState(new Map());
  user.user.settings.forEach((setting) => {
    settingValueMap.set(setting.key, setting.value);
  });

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
                !settingValueMap.has(setting.name)
                  ? false
                  : settingValueMap.get(setting.name)
              }
            />
          );
        })}
      </div>
    </>
  );
}
