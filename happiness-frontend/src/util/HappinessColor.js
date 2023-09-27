export function happinessColor(happiness) {
    let colors = [
        "bg-[#ff0000]",
        "bg-[#ff4628]",
        "bg-[#ff8423]",
        "bg-[#ff9d23]",
        "bg-[#ffbf2a]",
        "bg-[#ffdd0b]",
        "bg-[#94e000]",
        "bg-[#68c600]",
        "bg-[#12b500]",
        "bg-[#009f05]",
        "bg-[#007e17]",
    ];
    return colors[Math.floor(happiness)];
    // return colors[Math.floor(happiness / 0.5)];
}