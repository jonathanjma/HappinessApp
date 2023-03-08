import ToggleSettingCard from "../components/ToggleSettingCard";
import { statSettings } from "../resources/StatSettings";
import { accountSettings } from "../resources/AccountSettings";
import ButtonSettingCard from "../components/ButtonSettingCard";

export default function Settings(props) {
  /*Props.settings should be an array of settings
      that contains information about the settings.*/
  return (
    <>
      <p className="text-3xl font-semibold text-raisin-600 ml-10 mb-4 mt-3">
        Account Settings
      </p>
      <div className="flex justify-left flex-wrap">
        {accountSettings.map((setting) => {
          return (
            <ButtonSettingCard
              id={setting.id}
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
          return (
            <ToggleSettingCard
              id={setting.id}
              name={setting.name}
              icon={setting.icon}
            />
          );
        })}
      </div>
    </>
  );
}
