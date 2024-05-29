/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable @typescript-eslint/no-unused-vars */
import React, { useState, useEffect } from "react";
import { AgGridReact } from "ag-grid-react"; // React Data Grid Component
import "ag-grid-community/styles/ag-grid.css"; // Mandatory CSS required by the grid
import "ag-grid-community/styles/ag-theme-quartz.css"; // Optional Theme applied to the grid
import { ColDef } from "ag-grid-community";
import { FaImages } from "react-icons/fa";
import { Tooltip } from "react-tooltip";
import { Business, OpeningHours, Photo, fetchBusinesses } from "../../services/apiService";


const ImageRenderer: React.FC<{ value: Photo[] }> = ({ value }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div>
      <button
        onClick={() => setShowTooltip(!showTooltip)}
        data-tip
        data-for="imageTooltip"
      >
        <FaImages />
        <span>{value?.length}</span>
      </button>
      {showTooltip && (
        <Tooltip id="imageTooltip" place="top">
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(2, 1fr)",
              gap: "10px",
            }}
          >
            {value?.map((photo, index) => (
              <img
                key={index}
                src={`https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=${photo.photo_reference}&key=YOUR_API_KEY`}
                alt="Place"
                style={{ width: "100%", height: "auto" }}
              />
            ))}
          </div>
        </Tooltip>
      )}
    </div>
  );
};

const OpeningHoursRenderer: React.FC<{ value: OpeningHours }> = ({ value }) => {
  return (
    <div>
      {value?.weekday_text?.map((text, index) => (
        <div key={index}>{text}</div>
      ))}
    </div>
  );
};

const Dataview: React.FC = () => {

  const [businesses, setBusinesses] = useState<Business[]>();

  const [columnDefs, setColumnDefs] = useState<ColDef[]>([
    { headerName: "Name", field: "name", sortable: true, filter: true },
    {
      headerName: "Address",
      field: "formatted_address",
      sortable: true,
      filter: true,
    },
    {
      headerName: "Phone Number",
      field: "formatted_phone_number",
      sortable: true,
      filter: true,
    },
    {
      headerName: "Images",
      field: "photos",
      cellRenderer: ImageRenderer,
      cellRendererParams: {
        photos: "photos",
      },
    },
    {
      headerName: "Opening Hours",
      field: "opening_hours",
      cellRenderer: OpeningHoursRenderer,
      cellRendererParams: {
        opening_hours: "opening_hours",
      },
    },
    {
      headerName: "Website",
      field: "website",
      sortable: true,
      filter: true,
    },
    {
      headerName: "Rating",
      field: "rating",
      sortable: true,
    },
    {
      headerName: "Total Rating",
      field: "user_ratings_total",
      sortable: true,
    },
  ]);

  
  useEffect(() => {
    
    const fetchBusinessData = async () => {
      try {
        const obj = JSON.parse(localStorage?.getItem('catalog')?? '{}');
        const data = await fetchBusinesses(obj);
        setBusinesses(data);
      } catch (error: any) {
        console.error(error);
      } finally {
      }
    };

    fetchBusinessData();
  }, []);

  return (
    <div
      className="ag-theme-quartz-dark"
      style={{ height: "100%", width: "100%", backgroundColor: "#182230" }}
    >
      <AgGridReact
        columnDefs={columnDefs}
        rowData={businesses}
        pagination={true}
        paginationPageSize={10}
        paginationPageSizeSelector={[10, 25, 50]}
      />
    </div>
  );
};

export default Dataview;
