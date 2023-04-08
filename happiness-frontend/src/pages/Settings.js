import ToggleSettingCard from "../components/ToggleSettingCard";
import { statSettings } from "../resources/StatSettings";
import { accountSettings } from "../resources/AccountSettings";
import ButtonSettingCard from "../components/ButtonSettingCard";
import {useApi} from "../contexts/ApiProvider";
import {useQuery} from "react-query";
import {useUser} from "../contexts/UserProvider";
import {Spinner} from "react-bootstrap";
import React, {useEffect, useState} from "react";

export default function Settings(props) {
  /*Props.settings should be an array of settings
      that contains information about the settings.*/
    const  { user } = useUser()
    const api = useApi()
    const [settingValueMap] = useState(new Map());
    // defaultValuesSet contains whether the default value for each toggle was set. This prevents the buttons
    // from loading before the map is populated.
    const [defaultValuesSet, setDefaultValuesSet] = useState(false)
    const {isLoading, data, isError} = useQuery(`settings for ${user.id}`, () => {
        return api.get("/user/settings/").then((res) => res.data)
    })

    const checkSettings = () => {
        if (isLoading || isError) {
            return
        }
        // console.log(`Settings data: ${JSON.stringify(data)}`)
        data.forEach((setting) => {
            settingValueMap.set(setting["key"], setting.value)
        })
        // console.log(settingValueMap)
        setDefaultValuesSet(true)
    }

    useEffect(() => {
        checkSettings()
    }, [isLoading])

    if (isLoading || !defaultValuesSet) {
        return (
            <div className="flex flex-row items-center justify-center ">
                <Spinner />
            </div>
        );
    }

    if (isError) {
        return (
            <span>
            Error loading data (try to logout and log back in, or alert the devs {" "}
                <a href={"https://forms.gle/n3aFRA9fmpM22UdEA"}>
              here
            </a>
            )
          </span>
        )
    }

  return (
    <>
      <p className="text-3xl font-semibold text-raisin-600 ml-10 mb-4 mt-3">
        Account Settings
      </p>
      <div className="flex justify-left flex-wrap">
        {accountSettings.map((setting) => {
          return (
            <ButtonSettingCard
              key={setting.id}
              name={setting.name}
              icon={setting.icon}
              isSensitive={setting.isSensitive}
            />
          );
        })}
      </div>
      <p className="text-3xl font-semibold text-raisin-600 ml-10 mb-4 mt-3">
        Statistics Settings
      </p>
      <div className="flex justify-left flex-wrap">
        {statSettings.map((setting) => {
            // console.log(settingValueMap)
            // console.log(`setting.name: ${setting.name}`)
          return (
            <ToggleSettingCard
              key={setting.id}
              name={setting.name}
              icon={setting.icon}
              defaultCheck={!settingValueMap.has(setting.name) ? false : settingValueMap.get(setting.name)}
            />
          );
        })}
      </div>
    </>
  );
}
