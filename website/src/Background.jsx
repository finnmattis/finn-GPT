import React, { useRef, useEffect } from "react";
import * as THREE from "three";

const Background = () => {
  const mountRef = useRef(null);

  useEffect(() => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      2000
    );
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    mountRef.current.appendChild(renderer.domElement);

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

    function animate() {
      requestAnimationFrame(animate);
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

    animate();

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      mountRef.current.removeChild(renderer.domElement);
    };
  }, []);

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
      }}
    />
  );
};

export default Background;
