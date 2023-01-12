import React, {useState} from "react";
import Carousel from "react-bootstrap/Carousel";
import FriendGroup from "../media/friend-group.svg";
import Journal from "../media/journal.svg";
import Statistics from "../media/statistics.svg";

export default function WelcomeCarousel() {
  const [index, setIndex] = useState(0);
  const size = 64;
  const handleSelect = (selectedIndex, e) => {
    setIndex(selectedIndex);
  };

  return (
    <Carousel
      activeIndex={index}
      onSelect={handleSelect}
      controls={false}
      indicators={false}
      className="carousel"
      interval={4000}
      pause={false}
    >
      <Carousel.Item>
        <img
          src={FriendGroup}
          alt="Group of Friends"
          className="welcome-images"
        />
        <p className="welcome-text">
          Learn about yourself and your friends by logging your happiness each
          day.
        </p>
      </Carousel.Item>
      <Carousel.Item>
        <img src={Journal} alt="Journal" className="welcome-images" />
        <p className="welcome-text">Keep secure journal entries.</p>
      </Carousel.Item>
      <Carousel.Item>
        <div className="welcome-images">
          <img src={Statistics} alt="Statistics" className="welcome-images" />
        </div>
        <p className="welcome-text">View interesting trends and data.</p>
      </Carousel.Item>
    </Carousel>
  );
}
