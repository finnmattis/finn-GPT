import { faStar } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useEffect, useState } from "react";

export default function MagicText() {
  //these values are for the stars
  const [left1, setLeft1] = useState(0);
  const [top1, setTop1] = useState(0);

  const [left2, setLeft2] = useState(0);
  const [top2, setTop2] = useState(0);
  const [animation2, setAnimation2] = useState(false);

  const [left3, setLeft3] = useState(0);
  const [top3, setTop3] = useState(0);
  const [animation3, setAnimation3] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setLeft1(Math.floor(Math.random() * 110 - 10));
      setTop1(Math.floor(Math.random() * 110 - 40));
      setTimeout(() => {
        setLeft2(Math.floor(Math.random() * 110 - 10));
        setTop2(Math.floor(Math.random() * 110 - 40));
        setAnimation2(true);
      }, 333);
      setTimeout(() => {
        setLeft3(Math.floor(Math.random() * 110 - 10));
        setTop3(Math.floor(Math.random() * 110 - 40));
        setAnimation3(true);
      }, 666);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <p className="mt-10 text-center text-6xl text-white sm:text-3xl">
      Look up a word in{"   "}
      <span className="relative inline-block text-purple-500">
        <FontAwesomeIcon
          className="absolute h-4 w-4 animate-twinkle"
          style={{ left: `${left1}%`, top: `${top1}%` }}
          icon={faStar}
        />
        <FontAwesomeIcon
          data-animate={animation2}
          className="absolute h-4 w-4 scale-0 data-[animate=true]:animate-twinkle"
          style={{ left: `${left2}%`, top: `${top2}%` }}
          icon={faStar}
        />
        <FontAwesomeIcon
          data-animate={animation3}
          className="absolute h-4 w-4 scale-0 data-[animate=true]:animate-twinkle"
          style={{ left: `${left3}%`, top: `${top3}%` }}
          icon={faStar}
        />
        <span className="animate-bg-pan bg-gradient-to-r from-purple-500 via-violet-500 to-pink-500 bg-[length:200%] bg-clip-text text-transparent">
          Whitiker's Words
        </span>
      </span>
    </p>
  );
}
