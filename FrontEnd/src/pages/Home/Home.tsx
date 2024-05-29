/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable @typescript-eslint/no-unused-vars */
import { useEffect, useState } from "react";
import CatalogueCard from "../../components/CatalogueCard/CatalogueCard";
import styles from "./Home.module.css";
import Modal from "../../components/Modal/Modal";
import {
  getCatalog,
  Catalog,
  fetchBusinesses,
} from "../../services/apiService";
import {
  useLocation,
  useSearchParams,
} from "react-router-dom";
import mapboxgl from "mapbox-gl";

mapboxgl.accessToken = process.env?.REACT_APP_MAPBOX_KEY ?? "";
mapboxgl.setRTLTextPlugin(
  'https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-rtl-text/v0.2.3/mapbox-gl-rtl-text.js',()=>{}
);
const useQuery = () => {
  return new URLSearchParams(useLocation().search);
};

function createQueryString(queryObject: any = {}) {
  let queryString = Object.keys(queryObject)
    .filter(
      (key) =>
        queryObject[key] &&
        !(Array.isArray(queryObject[key]) && !queryObject[key].length)
    )
    .map((key) => {
      return Array.isArray(queryObject[key])
        ? queryObject[key]
            .map(
              (item: any) =>
                `${encodeURIComponent(key)}=${encodeURIComponent(item)}`
            )
            .join("&")
        : `${encodeURIComponent(key)}=${encodeURIComponent(queryObject[key])}`;
    })
    .join("&");
  return queryString ? `?${queryString}` : "";
}

const HomeComponent = () => {
  const location = useLocation();
  const query = useQuery();

  let [searchParams, setSearchParams] = useSearchParams();

  const [businesses, setBusinesses] = useState<any>(null);

  const [cardData, setCardData] = useState<Catalog[] | undefined>(undefined);
  const [showModal, setShowModal] = useState(true);
  const openModal = () => setShowModal(true);
  const closeModal = () => setShowModal(false);

  useEffect(() => {
    const catalog = {
      catalogue_dataset_id: query.get("catalogue_dataset_id"),
    };
    localStorage.setItem("catalog", JSON.stringify(catalog));
    fetchBusinessData();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.search]);

  const handleMoreInfo = (catalog: Catalog) => {
    let params = createQueryString({
      catalogue_dataset_id: catalog.id,
    });
    setSearchParams(params);
    closeModal();
  };

  const fetchBusinessData = async () => {
    try {
      const obj = JSON.parse(localStorage?.getItem("catalog") ?? "{}");

      if (!businesses && obj.catalogue_dataset_id) {
        const data1 = await fetchBusinesses(obj);
        let formatedData: any = {
          type: "FeatureCollection",
          features: [],
        };
        data1?.forEach((x) => {
          formatedData.features.push({
            type: "Feature",
            properties: {},
            geometry: {
              type: "Point",
              coordinates: [
                x.geometry?.location?.lng,
                x.geometry?.location?.lat
              ],
            },
          });
        });
        setBusinesses(formatedData);
      }
    } catch (error: any) {
      console.error(error);
    } finally {
    }
  };

  useEffect(() => {
    const fetchCatalogData = async () => {
      if (!cardData) {
        try {
          const data = await getCatalog();
          setCardData(data);
        } catch (error: any) {
          console.error(error);
        } finally {
        }
      }
    };

    fetchCatalogData();
  }, []);

  useEffect(() => {
    const map = new mapboxgl.Map({
      container: "map-container",
      style: "mapbox://styles/mapbox/streets-v11",
      center: businesses?.features[0]?.geometry?.coordinates ?? [
        39.6074258, 24.4738121,
      ],
      attributionControl: true,
      zoom: 13,
    });

    map.addControl(new mapboxgl.NavigationControl(), "top-right");
    if (businesses) {
      map.on("load", () => {
        if (!!businesses?.features && businesses?.features?.length) {
          map.setCenter(businesses?.features[0]?.geometry?.coordinates);
          map.addSource("circle", {
            type: "geojson",
            data: businesses,
          });

          map.addLayer({
            id: "circle-layer",
            type: "circle",
            source: "circle",
            paint: {
              "circle-radius": 13,
              "circle-color": "#12939A",
              "circle-opacity": 0.8,
              "circle-stroke-width": 0.4,
              "circle-stroke-color": "#898989",
            },
          });
        }
      });
      return () => map.remove();
    }
  }, [businesses]);

  return (
    <div className={styles.content}>
      <div
        id="map-container"
        style={{ width: "96%", height: "100vh", zIndex: 99 }}
      />
      ;
      <Modal show={showModal} onClose={closeModal}>
        <h2 className={styles.catalogueHeading}>Add Data to Map</h2>
        <div className={styles.catalogueWrapper}>
          {cardData?.map((item) => (
            <CatalogueCard
              key={item.id}
              id={item.id}
              thumbnail_url={item.thumbnail_url}
              name={item.name}
              records_number={item.records_number}
              description={item.description}
              onMoreInfo={() => handleMoreInfo(item)}
              can_access={item.can_access}
            />
          ))}
        </div>
      </Modal>
    </div>
  );
};

export default HomeComponent;
