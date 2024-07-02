import PropTypes from "prop-types";
import { useState, useEffect } from "react";

const Firefly = ({ x, y }) => (
  <div
    style={{
      position: "absolute",
      left: `${x}px`,
      top: `${y}px`,
      width: "2px",
      height: "2px",
      borderRadius: "50%",
      backgroundColor: "#ffff00",
      boxShadow: "0 0 5px #ffff00",
      animation: "flicker 1.5s infinite alternate",
    }}
  />
);

Firefly.propTypes = {
  x: PropTypes.number.isRequired,
  y: PropTypes.number.isRequired,
};

const FireflyEffect = ({ count }) => {
  const [fireflies, setFireflies] = useState([]);

  useEffect(() => {
    const createFireflies = () => {
      return Array.from({ length: count }, () => ({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        vx: (Math.random() - 0.5) * 2,
        vy: (Math.random() - 0.5) * 2,
      }));
    };

    setFireflies(createFireflies());

    const moveFireflies = () => {
      setFireflies((prev) =>
        prev.map((fly) => ({
          x: (fly.x + fly.vx + window.innerWidth) % window.innerWidth,
          y: (fly.y + fly.vy + window.innerHeight) % window.innerHeight,
          vx: fly.vx + (Math.random() - 0.5) * 0.2,
          vy: fly.vy + (Math.random() - 0.5) * 0.2,
        }))
      );
    };

    const intervalId = setInterval(moveFireflies, 50);

    return () => clearInterval(intervalId);
  }, [count]);

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        overflow: "hidden",
      }}
    >
      {fireflies.map((fly, index) => (
        <Firefly key={index} x={fly.x} y={fly.y} />
      ))}
      <style>
        {`
          @keyframes flicker {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}
      </style>
    </div>
  );
};

FireflyEffect.propTypes = {
  count: PropTypes.number.isRequired,
};

export default FireflyEffect;
