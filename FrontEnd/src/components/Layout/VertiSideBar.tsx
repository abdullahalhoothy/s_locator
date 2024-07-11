import React from "react";
import { Routes, Route } from "react-router-dom";
import styles from "./VertiSideBar.module.css";
import ExpandableMenu from "../ExpandableMenu/ExpandableMenu";
import Home from "../../pages/Home/Home";
import About from "../../pages/About/About";
import Dataview from "../../pages/Dataview/Dataview";
import { useCatalogContext } from "../../context/CatalogContext";
import { useUIContext} from "../../context/UIContext";
import CatalogSideMenu from "../CatalogSideMenu/CatalogSideMenu";
import CatalogDetailsForm from "../CatalogDetailsForm/CatalogDetailsForm";
import DefaultMenu from "../DefaultMenu/DefaultMenu";
import Login from "../../pages/Login/Login";
import UserProfile from "../../pages/Profile/UserProfile";
import Register from "../../pages/Register/Register";

function Layout() {
  const { selectedCatalog } = useCatalogContext();
  const { sidebarMode } = useUIContext();

  const sidebarContent =
    sidebarMode === "default" ? (
      <ExpandableMenu >
        <DefaultMenu />
      </ExpandableMenu>
    ) : sidebarMode === "catalog" ? (
      <div className={styles.CreateCatalogMenu}>
        <CatalogSideMenu />
      </div>
    ) : sidebarMode === "catalogDetails" && selectedCatalog ? (
      <div className={styles.CreateCatalogMenu}>
        <CatalogDetailsForm />
      </div>
    ) : null;

  return (
    <div className={styles.layout}>
      {sidebarContent}
      <div className={styles.content}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/profile" element={<UserProfile />} />
          <Route path="/tabularView" element={<Dataview />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </div>
    </div>
  );
}

export default Layout;
