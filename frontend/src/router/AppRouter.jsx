import { Routes, Route } from "react-router-dom";
import Layout from "../layout/Layout";
import Landing from "../pages/Landing";
import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";
import AuthCallback from "../pages/AuthCallback";
import Visors from "../pages/Visors";
import About from "../pages/About";

import bg1 from "../assets/backgrounds/bg-pattern-1.svg";
import bg2 from "../assets/backgrounds/bg-pattern-2.svg";
import bg3 from "../assets/backgrounds/bg-pattern-3.svg";
import bg4 from "../assets/backgrounds/bg-pattern-4.svg";

// --- Define all routes in a collection ---
const routeConfig = [
  { path: "/", component: Landing, backgroundImage: bg1 },
  { path: "/login", component: Login},
  { path: "/dashboard", component: Dashboard, backgroundImage: bg2 },
  { path: "/auth/callback", component: AuthCallback },
  { path: "/visors", component: Visors},
  { path: "/conocenos", component: About, backgroundImage: bg3 },
];

export default function AppRouter() {
  return (
    <Routes>
      {routeConfig.map(({ path, component: Component, backgroundClass, backgroundImage }) => (
        <Route
          key={path}
          path={path}
          element={
            <Layout backgroundClass={backgroundClass} backgroundImage={backgroundImage}>
              <Component />
            </Layout>
          }
        />
      ))}
    </Routes>
  );
}
