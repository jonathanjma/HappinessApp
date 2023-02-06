import {useState} from "react";

export default function Users(num) {
  const [users, setUsers] = useState([
    {
      id: 1,
      name: "Alex",
      email: "ayw29@cornell.edu",
      img: "https://images-ext-1.discordapp.net/external/-EIjsJAZFDJw3y57OkMdXG2u199aL0rtccT2dcp22dk/%3Fsize%3D4096/https/cdn.discordapp.com/avatars/285542608024109057/9e3499987c94208af7ddb20e65907d1a.png",
      friends: [20, 3, 4],
      group: [1, 2, 4],
      settings: [[true, false], 0],
      data: [
        {
          date: "1/5",
          level: 10,
          pubComment: "yay",
          privComment: "yayayayayayayay",
        },
        {
          date: "1/6",
          level: 4,
          pubComment: "horrible",
          privComment: "very bad day",
        },
        {
          date: "1/7",
          level: 6.5,
          pubComment: "alex avverage",
          privComment: "hmmmm",
        },
        {
          date: "1/8",
          level: 3,
          pubComment: "VERY interesting :((((. A lot of computer issues.",
        },
        {
          date: "1/9",
          level: 10,
        },
        {
          date: "1/10",
          level: 7,
          pubComment:
            "nice daynice daynice daynice daynice daynice daynice daynice daynice daynice daynice daynice day",
        },
        {
          date: "1/11",
          level: 9,
          pubComment: "nice day",
        },
        {
          date: "1/12",
          level: 9,
          pubComment:
            "hi! best day ever and i really enjoyed the day :). I love exploring and biking and going to different places around the world and city!",
        },
      ],
      measures: {
        mean: 7.3125,
        median: 8,
        mode: 10,
        range: 7,
        stdev: 2.8052,
        min: 3,
        q1: 5.25,
        q3: 9.5,
        max: 10,
      },
      // currently these stats are hardcoded in, but either they can be stored on database or calculated in the program
      // we can decide later
    },
    {
      id: 2,
      name: "Zach",
      email: "zes4@cornell.edu",
      img: "https://play-lh.googleusercontent.com/o7hHBVIagQ_rylkmNuIx_sOEzaoAgRSHQhsfBM_C5MV3nJThWC_kkTYaBJJwTnfVc7I",
      friends: [1],
      group: [1, 2],
      settings: [0, 0],
      data: [
        {
          date: "1/5",
          level: null,
          pubComment: "dominion",
          privComment: "used the best dominion strategy.",
        },
        {
          date: "1/6",
          level: 8,
          pubComment:
            "dominion! Best game ever. Did a lot of good things today :)",
          privComment: "used the best dominion strategy.",
        },
        {
          date: "1/7",
          level: 8,
          pubComment: "aced that prelim",
          privComment: "best test ever",
        },
        {
          date: "1/8",
          level: 10,
        },
        {
          date: "1/9",
          level: 3,
        },
        {
          date: "1/10",
          level: 2,
        },
        {
          date: "1/11",
          level: 4,
        },
        {
          date: "1/12",
          level: 6,
        },
      ],
      measures: {
        mean: 7.3125,
        median: 8,
        mode: 10,
        range: 7,
        stdev: 2.8052,
        min: 3,
        q1: 5.25,
        q3: 9.5,
        max: 10,
      },
    },
    {
      id: 3,
      name: "Jonathan",
      email: "jjm498@cornell.edu",
      img: "https://combo.staticflickr.com/pw/images/buddyicon04_r.png#196752228@N08",
      friends: [1],
      group: [1, 2, 3],
      settings: [0, 0],
      data: [
        {
          date: "1/5",
          level: 5,
          pubComment: "decent",
          privComment: "not as good as I would have liked",
        },
        {
          date: "1/6",
          level: 1,
          pubComment: "crying",
          privComment: "my pet elephant got lost :(",
        },
        {
          date: "1/7",
          level: 9.5,
          pubComment: "almost the best day ever",
          privComment: "won a million dollars, but elephant still lost :(",
        },
        {
          date: "1/8",
          level: 5,
        },
        {
          date: "1/9",
          level: 2,
        },
        {
          date: "1/10",
          level: null,
        },
        {
          date: "1/11",
          level: null,
        },
        {
          date: "1/12",
          level: null,
        },
      ],
      measures: {
        mean: 7.3125,
        median: 8,
        mode: 10,
        range: 7,
        stdev: 2.8052,
        min: 3,
        q1: 5.25,
        q3: 9.5,
        max: 10,
      },
    },
    {
      id: 4,
      name: "Jeremy",
      email: "jeremydominion@hotmail.com",
      img: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/I-172.svg/1200px-I-172.svg.png",
      friends: [],
      group: [1, 3],
      settings: [0, 0],
      data: [
        {
          date: "1/5",
          level: 6,
          pubComment: "good",
          privComment: "not as good as I would have liked",
        },
        {
          date: "1/6",
          level: 8,
          pubComment: "exciting",
          privComment: "fantastic! Loved it :).",
        },
        {
          date: "1/7",
          level: 3,
          pubComment: "not as good",
          privComment: "worst day ever :(",
        },
        {
          date: "1/8",
          level: 3,
        },
        {
          date: "1/9",
          level: 2,
        },
        {
          date: "1/10",
          level: 1,
        },
        {
          date: "1/11",
          level: 4,
        },
        {
          date: "1/12",
          level: 5,
        },
      ],
      measures: {
        mean: 7.3125,
        median: 8,
        mode: 10,
        range: 7,
        stdev: 2.8052,
        min: 3,
        q1: 5.25,
        q3: 9.5,
        max: 10,
      },
    },
    {
      id: 5,
      name: "Sasha",
      email: "sashaair@gmail.com",
      img: "https://www.stadthalle.com/tools/imager/imager.php?file=%2Fmedia%2Fimage%2Foriginal%2F5168.jpg&height=750",
      friends: [6],
      group: [],
      settings: [0, 0],
      data: [
        {
          date: "1/5",
          level: 10,
          pubComment: "asdad",
          privComment: "hehe",
        },
        {
          date: "1/6",
          level: 2,
          pubComment: "sad",
          privComment: "bad! hated it :().",
        },
        {
          date: "1/7",
          level: 4.5,
          pubComment: "not as good",
          privComment: "mediocre day :(",
        },
        {
          date: "1/8",
          level: null,
        },
        {
          date: "1/9",
          level: null,
        },
        {
          date: "1/10",
          level: null,
        },
        {
          date: "1/11",
          level: null,
        },
        {
          date: "1/12",
          level: null,
        },
      ],
      measures: {
        mean: 7.3125,
        median: 8,
        mode: 10,
        range: 7,
        stdev: 2.8052,
        min: 3,
        q1: 5.25,
        q3: 9.5,
        max: 10,
      },
    },
    {
      id: 6,
      name: "Andrew",
      email: "andrewthegreat@yahoo.com",
      img: "https://c4.wallpaperflare.com/wallpaper/868/982/438/blue-background-orange-fruit-yellow-orange-wallpaper-preview.jpg",
      friends: [5],
      group: [1, 4],
      settings: [0, 0],
      data: [
        {
          date: "1/5",
          level: 6,
          pubComment: "good",
          privComment: "not as good as I would have liked",
        },
        {
          date: "1/6",
          level: 2,
          pubComment: "exciting",
          privComment: "fantastic! Loved it :).",
        },
        {
          date: "1/7",
          level: 7.5,
          pubComment: "not as good",
          privComment: "worst day ever :(",
        },
        {
          date: "1/8",
          level: null,
        },
        {
          date: "1/9",
          level: 4.0,
        },
        {
          date: "1/10",
          level: 7.5,
        },
        {
          date: "1/11",
          level: null,
        },
        {
          date: "1/12",
          level: null,
        },
      ],
      measures: {
        mean: 7.3125,
        median: 8,
        mode: 10,
        range: 7,
        stdev: 2.8052,
        min: 3,
        q1: 5.25,
        q3: 9.5,
        max: 10,
      },
    },
  ]);
  return users.find((item) => item.id === num);
}

// -------------------------------------------

/*
- uuid
- name
- profile picture
- email?
- data 
- friends
- groups (group id)
- settings
    - graph component:
        - weekly
        - monthly (checkboxes that allows you to choose between one, other, or both) (one must be checked)
        - yearly (for later)
        - all time (for later)
        - for now: true/false for weekly then monthly
    - statistics
        - mean (average)/median default (0)
        - options: standard deviation, mode, range, maximum/minimum, 1st and 3rd quartile
    - clear data/delete account



- settings:
  - what statistics
  - delete account
  - log out
*/
