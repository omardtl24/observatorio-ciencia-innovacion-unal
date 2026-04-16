import { Routes, Route } from "react-router-dom";
import Layout from "../layout/Layout";
import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";
import CreateResource from "../pages/CreateResource";
import EditResource from "../pages/EditResource";
import Landing from "../pages/Landing";
import Resources from "../pages/Resources";
import Resource from "../pages/Resource";
import DataSources from "../pages/DataSources";
import CreateDataSource from "../pages/CreateDataSource";
import EditDataSource from "../pages/EditDataSource";
import ConnectionError from "../pages/ConnectionError";

// --- Define all routes in a collection ---
const routeConfig = [
  { path: "/login",
    component: Login, 
    backgroundClass: "bg-white" },
  { path: "/dashboard", 
    component: Dashboard, 
    backgroundClass: "bg-primary-green-soft" },
  { path: "/resources/create",
    component: CreateResource,
    backgroundClass: "bg-primary-blue-soft" },
  { path: "/resources/:type", 
    component: Resources, 
    backgroundClass: "bg-white" },
  { path: "/resource/edit/:type/:id",
    component: EditResource,
    backgroundClass: "bg-gray-100" },
  { path: "/resource/:type/:id", 
    component: Resource, 
    backgroundClass: "bg-secondary-gray-soft" },
  { path: "/data-sources",
    component: DataSources,
    backgroundClass: "bg-white" },
  { path: "/data-sources/create",
    component: CreateDataSource,
    backgroundClass: "bg-primary-blue-soft" },
  { path: "/data-sources/edit/:id",
    component: EditDataSource,
    backgroundClass: "bg-gray-100" },
  { path: "/", 
    component: Landing, 
    backgroundClass: "bg-gray-100"},
  { path: "/connection-error",
    component: ConnectionError,
    backgroundClass: "bg-gray-100"},
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
              <Layout {...route} path={path}>
                <Component />
              </Layout>
            }
          />
        );
      })}
    </Routes>
  );
}
