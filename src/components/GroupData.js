import {useState} from "react";

export default function GroupData(id) {
  const [groups, setGroups] = useState({
    1: { name: "the bois", users: [1, 2, 3, 4, 6] },
    2: { name: "the devs", users: [1, 2, 3] },
    3: { name: "jonathan+jeremey", users: [3, 4] },
    4: { name: "alex+andrew", users: [1, 6] },
  });

  return groups[id];
}
