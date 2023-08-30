import { Input } from "@mui/material";

export default function SearchBar() {
  return (
    <Input
      fullWidth
      disableUnderline
      placeholder="Search for dates, keywords, or scores"
      className="text-base rounded-[50px] border px-6 py-3"
    />
  );
}
