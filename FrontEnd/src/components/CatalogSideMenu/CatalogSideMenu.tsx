import React, { useState, MouseEvent } from "react";
import styles from "./CatalogSideMenu.module.css";
import { MdLayers, MdArrowBackIos } from "react-icons/md";
import { useUIContext } from "../../context/UIContext";
import DataContainer from "../DataContainer/DataContainer";
import { useCatalogContext } from "../../context/CatalogContext";
import MultipleLayersSetting from "../MultipleLayersSetting/MultipleLayersSetting";

function CatalogSideMenu() {
  const { openModal, setSidebarMode } = useUIContext();
  const {
    setSelectedContainerType,
    selectedLayers,
    resetState,
    setFormStage,
    setLegendList,
    formStage,
    setSubscriptionPrice,
  } = useCatalogContext();

  function openCatalogModal(contentType: "Catalogue" | "Layer") {
    setSelectedContainerType(contentType);
    openModal(<DataContainer />);
  }

  function handleBackClick(event: MouseEvent) {
    setSidebarMode("default");
  }

  function handleAddCatalogClick(event: MouseEvent) {
    openCatalogModal("Catalogue");
  }

  function handleAddLayerClick(event: MouseEvent) {
    openCatalogModal("Layer");
  }

  function handleDiscardClick(event: MouseEvent) {
    resetState();
    setSidebarMode("default");
  }

function handleSaveClick() {
  const legends = selectedLayers
    .map(function (layer) {
      return layer.legend;
    })
    .filter(function (legend): legend is string {
      return !!legend;
    });

  setLegendList(legends);
  setFormStage("catalogue details");
  setSidebarMode("catalogDetails");
}

  return (
    <div className={styles.container}>
      <nav className={styles.nav}>
        <MdArrowBackIos className={styles.backIcon} onClick={handleBackClick} />
        <MdLayers className={styles.icon} />
      </nav>
      <div className={styles.content}>
        <div className={styles.section}>
          <p className={styles.sectionTitle}>Datasets</p>
          <button
            className={`${styles.addButton} ${styles.addDataButton}`}
            onClick={handleAddCatalogClick}
          >
            + Add Catalog
          </button>
        </div>
        <div className={styles.section}>
          <p className={styles.sectionTitle}>Layers</p>
          <button
            className={`${styles.addButton} ${styles.addLayerButton}`}
            onClick={handleAddLayerClick}
          >
            + Add Layer
          </button>
        </div>
        {selectedLayers.map(function (layer, index) {
          return <MultipleLayersSetting key={index} layerIndex={index} />;
        })}
      </div>
      {selectedLayers.length > 0 && (
        <div className={styles.saveButtonsContainer}>
          <button
            onClick={handleDiscardClick}
            className={`${styles.addButton} ${styles.addLayerButton}`}
          >
            Discard
          </button>
          <button
            onClick={handleSaveClick}
            className={`${styles.addButton} ${styles.addDataButton}`}
          >
            Save
          </button>
        </div>
      )}
    </div>
  );
}

export default CatalogSideMenu;
