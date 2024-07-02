import PropTypes from "prop-types";
import { useRef, useEffect, useState } from "react";
import * as THREE from "three";

const StarsBackground = ({ currentTheme }) => {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const [isBackgroundReady, setIsBackgroundReady] = useState(false);

  useEffect(() => {
    const mountRefCurrent = mountRef.current;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      2000
    );
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    mountRefCurrent.appendChild(renderer.domElement);

    const starCount = 10000;
    const stars = new THREE.Group();

    function createStar() {
      const size = Math.random() * 0.5 + 0.5;
      const geometry = new THREE.SphereGeometry(size, 8, 8);
      const material = new THREE.MeshBasicMaterial({ color: 0xffffff });
      const star = new THREE.Mesh(geometry, material);

      star.position.set(
        Math.random() * 2000 - 1000,
        Math.random() * 2000 - 1000,
        Math.random() * 2000 - 1000
      );

      return star;
    }

    for (let i = 0; i < starCount; i++) {
      stars.add(createStar());
    }

    scene.add(stars);
    camera.position.z = 5;

    sceneRef.current = { scene, camera, renderer, stars };
    setIsBackgroundReady(true);

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);

      // Dispose of Three.js resources
      scene.traverse((object) => {
        if (object.geometry) object.geometry.dispose();
        if (object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach((material) => material.dispose());
          } else {
            object.material.dispose();
          }
        }
      });

      renderer.dispose();

      if (mountRefCurrent && renderer.domElement) {
        mountRefCurrent.removeChild(renderer.domElement);
      }
    };
  }, [mountRef, sceneRef, setIsBackgroundReady]);

  useEffect(() => {
    if (!isBackgroundReady) return;

    const { scene, camera, renderer, stars } = sceneRef.current;
    let animationFrameId;

    function animate() {
      animationFrameId = requestAnimationFrame(animate);
      stars.children.forEach((star) => {
        star.position.z += 2;
        if (star.position.z > 1000) {
          star.position.z = -1000;
          star.position.x = Math.random() * 2000 - 1000;
          star.position.y = Math.random() * 2000 - 1000;
        }
      });
      renderer.render(scene, camera);
    }

    if (currentTheme === 1) {
      animate();
    }

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [currentTheme, isBackgroundReady]);

  return (
    <div
      ref={mountRef}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        overflow: "hidden",
        opacity: currentTheme === 1 ? 1 : 0,
        transition: "opacity 0.5s ease-in-out",
        pointerEvents: currentTheme === 1 ? "auto" : "none",
      }}
    />
  );
};

StarsBackground.propTypes = {
  currentTheme: PropTypes.number.isRequired,
};

export default StarsBackground;
