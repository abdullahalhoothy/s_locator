import React, { useEffect, useState, ChangeEvent } from "react";
import { HttpReq } from "../../services/apiService";
import {
  formatSubcategoryName,
  processData,
} from "../../utils/helperFunctions";
import {
  City,
  FirstFormResponse,
  FormData,
} from "../../types/allTypesAndInterfaces";
import styles from "./LayerDetailsForm.module.css";
import Loader from "../Loader/Loader";
import { useLayerContext } from "../../context/LayerContext";
import urls from "../../urls.json";

function LayerDetailsForm() {
  const { handleNextStep, setFirstFormResponse, loading, setDatasetInfo } =
    useLayerContext();

  const [firstFormData, setFirstFormData] = useState<FormData>({
    selectedCountry: "",
    selectedCity: "",
    selectedCategory: "",
    selectedSubcategory: "",
  });

  const [countries, setCountries] = useState<string[]>([]);
  const [cities, setCities] = useState<City[]>([]);
  const [citiesData, setCitiesData] = useState<{ [country: string]: City[] }>(
    {}
  );
  const [categories, setCategories] = useState<string[]>([]);
  const [subcategories, setSubcategories] = useState<string[]>([]);
  const [categoriesData, setCategoriesData] = useState<{
    [category: string]: string[];
  }>({});
  const [localLoading, setLocalLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  // City request response information
  const [cityResMessage, setCityResMessage] = useState<string>("");
  const [cityResId, setCityResId] = useState<string>("");

  // Categories request response information
  const [categoriesResMessage, setCategoriesResMessage] = useState<string>("");
  const [categoriesResId, setCategoriesResId] = useState<string>("");

  // Nearby_cities post response information
  const [postResMessage, setPostResMessage] = useState<string>("");
  const [postResId, setPostResId] = useState<string>("");

  function fetchData() {
    HttpReq<string[]>(
      urls.country_city,
      function (data) {
        setCountries(processData(data, setCitiesData));
      },
      setCityResMessage,
      setCityResId,
      setLocalLoading,
      setError
    );

    HttpReq<string[]>(
      urls.nearby_categories,
      function (data) {
        setCategories(processData(data, setCategoriesData));
      },
      setCategoriesResMessage,
      setCategoriesResId,
      setLocalLoading,
      setError
    );
  }

  useEffect(function () {
    fetchData();
  }, []);

  function handleChange(event: ChangeEvent<HTMLSelectElement>) {
    const { name, value } = event.target;
    setFirstFormData(function (prevData) {
      return {
        ...prevData,
        [name]: value,
      };
    });

    if (name === "selectedCountry") {
      const selectedCountryCities = citiesData[value] || [];
      setCities(selectedCountryCities);
      setFirstFormData(function (prevData) {
        return {
          ...prevData,
          selectedCity: "", // Reset selected city when country changes
        };
      });
    } else if (name === "selectedCategory") {
      const selectedSubcategories = categoriesData[value] || [];
      setSubcategories(selectedSubcategories);
      setFirstFormData(function (prevData) {
        return {
          ...prevData,
          selectedSubcategory: "", // Reset selected subcategory when category changes
        };
      });
    }
  }

  function validateForm() {
    if (
      !firstFormData.selectedCountry ||
      !firstFormData.selectedCity ||
      !firstFormData.selectedCategory ||
      !firstFormData.selectedSubcategory
    ) {
      setError(new Error("All fields are required."));
      return false;
    }
    setError(null);
    return true;
  }

  function handleButtonClick(action: string) {
    if (validateForm()) {
      handleFirstFormApiCall(action);
    }
  }

  function handleFirstFormApiCall(action: string) {
    const selectedCity = cities.find(function (city) {
      return city.name === firstFormData.selectedCity;
    });

    if (!selectedCity) {
      setError(new Error("Selected city not found."));
      return;
    }

    const postData = {
      dataset_category: firstFormData.selectedSubcategory,
      dataset_country: firstFormData.selectedCountry,
      dataset_city: firstFormData.selectedCity,
    };

    HttpReq<FirstFormResponse>(
      urls.create_layer,
      function (response) {
        setFirstFormResponse(response as FirstFormResponse); 
        if (response.bknd_dataset_id && response.prdcer_lyr_id) {
          setDatasetInfo({
            bknd_dataset_id: response.bknd_dataset_id,
            prdcer_lyr_id: response.prdcer_lyr_id,
          });
        }
      },
      setPostResMessage,
      setPostResId,
      setLocalLoading,
      setError,
      "post",
      postData
    );

    handleNextStep();
  }

  return (
    <div className={styles.container}>
      <div className={styles.formGroup}>
        <label className={styles.label} htmlFor="country">
          Country:
        </label>
        <select
          id="country"
          name="selectedCountry"
          className={styles.select}
          value={firstFormData.selectedCountry}
          onChange={handleChange}
        >
          <option value="" disabled>
            Select a country
          </option>
          {countries.map(function (country) {
            return (
              <option key={country} value={country}>
                {country}
              </option>
            );
          })}
        </select>
      </div>
      <div className={styles.formGroup}>
        <label className={styles.label} htmlFor="city">
          City:
        </label>
        <select
          id="city"
          name="selectedCity"
          className={styles.select}
          value={firstFormData.selectedCity}
          onChange={handleChange}
          disabled={!firstFormData.selectedCountry}
        >
          <option value="" disabled>
            Select a city
          </option>
          {cities.map(function (city) {
            return (
              <option key={city.name} value={city.name}>
                {city.name}
              </option>
            );
          })}
        </select>
      </div>
      <div className={styles.formGroup}>
        <label className={styles.label} htmlFor="category">
          Category:
        </label>
        <select
          id="category"
          name="selectedCategory"
          className={styles.select}
          value={firstFormData.selectedCategory}
          onChange={handleChange}
        >
          <option value="" disabled>
            Select a category
          </option>
          {categories.map(function (category) {
            return (
              <option key={category} value={category}>
                {category}
              </option>
            );
          })}
        </select>
      </div>
      <div className={styles.formGroup}>
        <label className={styles.label} htmlFor="subcategory">
          Subcategory:
        </label>
        <select
          id="subcategory"
          name="selectedSubcategory"
          className={styles.select}
          value={firstFormData.selectedSubcategory}
          onChange={handleChange}
          disabled={!firstFormData.selectedCategory}
        >
          <option value="" disabled>
            Select a subcategory
          </option>
          {subcategories.map(function (subcategory) {
            return (
              <option key={subcategory} value={subcategory}>
                {formatSubcategoryName(subcategory)}
              </option>
            );
          })}
        </select>
      </div>
      {error && <p className={styles.error}>{error.message}</p>}
      <div className={styles.buttonContainer}>
        {localLoading || loading ? (
          <Loader />
        ) : (
          <>
            <button
              className={styles.button}
              onClick={function () {
                handleButtonClick("Get Sample");
              }}
            >
              Get Sample
            </button>
            <button
              className={styles.button}
              onClick={function () {
                handleButtonClick("Get Data");
              }}
            >
              Get Data
            </button>
          </>
        )}
      </div>
      {localLoading && <Loader />}
    </div>
  );
}

export default LayerDetailsForm;
