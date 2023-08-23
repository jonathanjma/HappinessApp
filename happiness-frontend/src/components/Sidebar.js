import * as React from "react";
import PropTypes from "prop-types";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import CssBaseline from "@mui/material/CssBaseline";
import Divider from "@mui/material/Divider";
import Drawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import MenuIcon from "@mui/icons-material/Menu";
import { ListItemIcon } from "@mui/material";
import EntriesIcon from "../media/bookmark-book-icon.svg";
import StatsIcon from "../media/graph-up-icon.svg";
import GroupIcon from "../media/group-icon.svg";
import SettingsIcon from "../media/settings-icon.svg";

import TextField from "@mui/material/TextField";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";

import { NavLink } from "react-router-dom";
import { useUser } from "../contexts/UserProvider";
import { useState, useRef, useEffect } from "react";
import { formatDate, formatHappinessNum } from "../pages/SubmitHappiness";
import { useQuery, useMutation } from "react-query";
import { useApi } from "../contexts/ApiProvider";
const drawerWidth = 340;

const buttonStyle =
  "text-white bg-gradient-to-r from-raisin-500 via-raisin-600 to-raisin-700 shadow-lg font-roboto font-semibold rounded-xl text-sm px-3 outline-none py-2.5 text-center m-2";
const textStyle = "text-raisin-600";

function ResponsiveDrawer(props) {
  const { user: userState, Logout } = useUser();
  const api = useApi();
  const me = userState.user;

  const [happiness, setHappiness] = useState("-");
  const isValidHappiness = (happiness) =>
    happiness !== "-" && happiness % 0.5 === 0 && 0 <= happiness <= 10;
  const [comment, setComment] = useState("");
  const [submissionStatus, setSubmissionStatus] = useState("Updated");
  // TODO refactor to use useRef! the let def was being reassigned
  // on every recomposition
  const postHappinessTimeout = useRef(undefined);
  const isInitialRender = useRef(true);

  const [updated, setUpdated] = useState(true);
  const commentBox = useRef();

  const weekday = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];
  const month = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  const UNSUBMITTED = "Unsubmitted (change the number to submit)";
  const UPDATING = "Updating...";
  const UPDATED = "Updated";
  const ERROR = "Error loading/retrieving happiness";

  const postHappinessMutation = useMutation({
    mutationFn: (newHappiness) => {
      return api.post("/happiness/", newHappiness);
    },
  });

  useEffect(() => {
    console.log(`Updating network: ${isValidHappiness(happiness)}`);
    if (isValidHappiness(happiness)) {
      console.log("loading network request");
      setSubmissionStatus(UPDATING);
      clearTimeout(postHappinessTimeout.current);
      postHappinessTimeout.current = setTimeout(() => {
        console.log("Sending request");
        postHappinessMutation.mutate({
          value: happiness,
          comment: comment,
          timestamp: formatDate(new Date()),
        });
      }, 1000);
    }
  }, [comment, happiness]);

  useEffect(() => {
    if (postHappinessMutation.isSuccess) {
      setSubmissionStatus("Updated");
    }
  }, [postHappinessMutation.isSuccess]);

  const today = new Date();
  const todayFormatted =
    weekday[today.getDay()] +
    ", " +
    today.toDateString().substring(4, 7) +
    " " +
    today.getDate() +
    ", " +
    today.getFullYear();

  const { window } = props;
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const [values, setValues] = React.useState({
    name: "Hello",
  });

  const handleChange = (name) => (event) => {
    setValues({ ...values, [name]: event.target.value });
  };

  const linkNames = ["/history/" + me.id, "/statistics", "/groups"];
  const icons = [EntriesIcon, StatsIcon, GroupIcon];

  // Networking

  // Make initial networking request to check for today's Happiness entry
  const { isLoading, data, isError, refetch, isSuccess } = useQuery(
    `happiness for ${me.id}`,
    () => {
      return api
        .get("/happiness/", {
          start: formatDate(today),
          end: formatDate(today),
        })
        .then((res) => res.data);
    }
  );

  // react to initial query
  useEffect(() => {
    if (isLoading) {
      // TODO from design: loading state for this submission box
      console.log(`Loading!`);
      setSubmissionStatus(UPDATING);
    } else if (isError) {
      // TODO from design: error state for this submission box
      console.log("Error!");
      setSubmissionStatus(ERROR);
    } else {
      console.log(`My successful data: ${data}`);
      console.log(`Something about my data: ${data[0] == null}`);
      if (data[0] == null) {
        setSubmissionStatus(UNSUBMITTED);
      } else {
        setSubmissionStatus(UPDATED);
        setHappiness(data[0].value);
        setComment(data[0].comment);
      }
    }
  }, [isLoading]);

  useEffect(() => {
    console.log("submission status changed " + submissionStatus);
  }, [submissionStatus]);

  const drawer = (
    <div className="h-full mx-3 my-4">
      {/* <Toolbar /> */}
      <div className="py-1 text-xl font-semibold">Account</div>
      <div className="pb-3 rounded-xl flex items-center">
        <NavLink
          to={"/profile/" + me.id}
          style={{ textDecoration: "none" }}
          className="flex items-center w-full"
        >
          <div className="items-center mr-2">
            <img
              className="mx-3 justify-center max-w-[50px] max-h-[50px] block mx-auto rounded-full sm:mx-0 sm:shrink-0"
              src={me.profile_picture}
              alt="profile"
            />
          </div>
          <div className="text-raisin-600">
            <div className="font-semibold text-lg">{me.username}</div>
            <div className="text-sm">
              Member since {me.created.substring(0, 4)}
            </div>
          </div>
        </NavLink>
        <div className="w-3/10" onClick={Logout}>
          <button className={buttonStyle}>Logout</button>
        </div>
      </div>

      <div className="py-1 text-xl font-semibold">Today's Entry</div>

      <div className="bg-buff-300 rounded-lg flex flex-wrap items-center my-2">
        <div className="w-full flex px-2 pt-4 items-center">
          <div className="pl-3 w-2/3 text-raisin-600">
            <div className="font-medium">{weekday[today.getDay()]}</div>
            <div className="text-2xl font-semibold">
              {month[today.getMonth()] + " " + today.getDate()}
            </div>
          </div>
          <div className="w-1/3 mr-3">
            <input
              className="w-24 h-14 text-4xl text-center rounded-lg bg-gray-100 focus:border-raisin-600 focus:border-2"
              type="number"
              inputMode="decimal"
              value={happiness}
              placeholder=""
              onChange={(e) => {
                console.log("changed");
                if (e.target.value < 0) {
                  setHappiness(0);
                } else if (e.target.value > 10) {
                  setHappiness(10);
                } else if (e.target.value.length > 3) {
                  setHappiness(e.target.value.toString().substring(0, 3));
                } else {
                  setHappiness(e.target.value);
                }
              }}
              onBlur={() => {
                if (happiness !== 10) {
                  setHappiness((prevHappiness) =>
                    formatHappinessNum(prevHappiness)
                  );
                }
              }}
            />
          </div>
        </div>
        <div className="w-full flex justify-center">
          <textarea
            ref={commentBox}
            id="large-input"
            value={comment}
            className={`w-full mt-3 mx-3 rounded-lg p-2 outline-none border-raisin-100 focus:border-raisin-200 border-2 focus:border-4 text-left text-sm`}
            style={{
              height: `${
                commentBox.current === undefined
                  ? 100
                  : Math.max(commentBox.current.scrollHeight, `100`)
              }px`,
              scrollbarColor: "#9191b6",
            }}
            placeholder={"Description"}
            maxLength="750"
            onChange={(e) => {
              handleChange("name");
              setComment(e.target.value);
            }}
          />
        </div>
        <div className="w-full text-right">
          <div className="text-raisin-600 mx-4 text-right text-sm">
            {comment.length + "/750"}
          </div>
        </div>
        <div className="w-full text-sm mx-4 flex">
          <div className="w-2/3">
            {today.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
          {/* Currently the time doesn't update so i need to fix that */}
          <div className="w-1/3 text-right">{submissionStatus}</div>
        </div>

        <button
          // onClick={onSubmitClick}
          className="flex-1 text-white bg-gradient-to-r from-raisin-500 via-raisin-600 to-raisin-700 shadow-lg font-roboto font-semibold rounded-lg text-sm px-5 outline-none py-2.5 text-center m-3"
        >
          Open Journal
        </button>
      </div>
      <List>
        {["Entries", "Stats", "Groups"].map((text, index) => (
          <ListItem key={text} disablePadding>
            <ListItemButton component={NavLink} to={linkNames[index]}>
              <ListItemIcon>
                <img src={icons[index]} />
              </ListItemIcon>
              <ListItemText primary={text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <List sx={{ justifyContent: "flex-end", width: "full" }}>
        <ListItem key={"Settings"} disablePadding>
          <ListItemButton commponent={NavLink} to={"/settings"}>
            <ListItemIcon>
              <img src={SettingsIcon} />
            </ListItemIcon>
            <ListItemText primary={"Settings"} />
          </ListItemButton>
        </ListItem>
      </List>
    </div>
  );

  const container =
    window !== undefined ? () => window().document.body : undefined;

  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
        }}
      >
        <Toolbar sx={{ color: "white" }}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: "none" } }}
          >
            <MenuIcon />
          </IconButton>
          <NavLink to={"/"} style={{ textDecoration: "none" }}>
            <Typography
              variant="h6"
              noWrap
              component="div"
              sx={{ color: "white" }}
            >
              Happiness App
            </Typography>
          </NavLink>
        </Toolbar>
      </AppBar>
      <Box
        // component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
        aria-label="mailbox folders"
      >
        {/* The implementation can be swapped with js to avoid SEO duplication of links. */}
        <Drawer
          container={container}
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: "block", md: "none" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: "none", md: "block" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar sx={{ color: "white" }} />
        {props.element}
      </Box>
    </Box>
  );
}

ResponsiveDrawer.propTypes = {
  /**
   * Injected by the documentation to work in an iframe.
   * You won't need it on your project.
   */
  window: PropTypes.func,
};

export default ResponsiveDrawer;
