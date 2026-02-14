import { Routes, Route } from "react-router-dom";
import Layout from "../layout/Layout";
import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";


import Bg1 from "../assets/backgrounds/bg-pattern-1.svg?react";
import Bg2 from "../assets/backgrounds/bg-pattern-2.svg?react";
import Bg3 from "../assets/backgrounds/bg-pattern-3.svg?react";
import Bg4 from "../assets/backgrounds/bg-pattern-4.svg?react";

// --- Define all routes in a collection ---
const routeConfig = [
  { path: "/login", component: Login, 
    backgroundSVGImage: Bg2, 
    svgFillClass: "text-primary-cyan-base",
    backgroundClass: "bg-gray-100" },
  { path: "/dashboard", 
    component: Dashboard, 
    backgroundSVGImage: Bg3, 
    svgFillClass: "text-primary-cyan-strong",
    backgroundClass: "bg-gray-100" },
];

export default function AppRouter() {
  return (
    <Routes>
      {routeConfig.map((route) => {
        const { path, component: Component } = route;

        return (
          <Route
            key={path}
            path={path}
            element={
              <Layout {...route}>
                <Component />
              </Layout>
            }
          />
        );
      })}
    </Routes>
  );
}
