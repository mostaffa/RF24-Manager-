import React from "react"
import { Routes, Route } from "react-router"
import Loader from "../components/ui/loader/Loader"

const Layout = React.lazy(() => import("../pages/dashboard/layout/Layout"))
const MainView = React.lazy(() => import("../pages/dashboard/main/MainView"))
const Dialogs = React.lazy(
  () => import("../pages/dashboard/notifications/Dialogs"),
)
const NotificationAlerts = React.lazy(
  () => import("../pages/dashboard/notifications/NotificationAlerts"),
)
const ProfileSettings = React.lazy(
  () => import("../pages/dashboard/Profile/Settings"),
)
const Roles = React.lazy(() => import("../pages/dashboard/admin/roles/Roles"))

export default function DashboardRouter() {
  return (
    <Routes>
      <Route
        path="/me"
        element={
          <React.Suspense fallback={<Loader />}>
            <ProfileSettings />
          </React.Suspense>
        }
      />
      <Route
        path="/layout"
        element={
          <React.Suspense fallback={<Loader />}>
            <Layout />
          </React.Suspense>
        }
      />
      <Route
        path="/notifications/dialogs"
        element={
          <React.Suspense fallback={<Loader />}>
            <Dialogs />
          </React.Suspense>
        }
      />
      <Route
        path="/notifications/alerts"
        element={
          <React.Suspense fallback={<Loader />}>
            <NotificationAlerts />
          </React.Suspense>
        }
      />
      <Route
        path="/*"
        element={
          <React.Suspense fallback={<Loader />}>
            <MainView />
          </React.Suspense>
        }
      />
      <Route
        path="/admin/roles"
        element={
          <React.Suspense fallback={<Loader />}>
            <Roles />
          </React.Suspense>
        }
      />
    </Routes>
  )
}
