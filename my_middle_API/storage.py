import json
import os
import uuid
from datetime import datetime
from typing import Dict, Union, Tuple, Optional, Any, List
from pydantic import BaseModel
from typing import Any
import json
from datetime import datetime, date
from fastapi import HTTPException, status
from all_types.myapi_dtypes import ReqLocation
from config_factory import get_conf
import logging
from logging_wrapper import log_and_validate
from logging_wrapper import apply_decorator_to_module, preserve_validate_decorator


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


USERS_PATH = "Backend/users"
STORE_CATALOGS_PATH = "Backend/store_catalogs.json"
DATASET_LAYER_MATCHING_PATH = "Backend/dataset_layer_matching.json"
DATASETS_PATH = "Backend/datasets"
USER_LAYER_MATCHING_PATH = "Backend/user_layer_matching.json"
METASTORE_PATH = "Backend/layer_category_country_city_matching"
STORAGE_DIR = "Backend/storage"
USERS_INFO_PATH = "Backend/users_info.json"

CONF = get_conf()
os.makedirs(STORAGE_DIR, exist_ok=True)


def to_serializable(obj: Any) -> Any:
    """
    Convert a Pydantic model or any other object to a JSON-serializable format.

    Args:
    obj (Any): The object to convert.

    Returns:
    Any: A JSON-serializable representation of the object.
    """
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(to_serializable(item) for item in obj)
    elif isinstance(obj, BaseModel):
        return to_serializable(obj.dict(by_alias=True))
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif hasattr(obj, "__dict__"):
        return to_serializable(obj.__dict__)
    else:
        return obj


def convert_to_serializable(obj: Any) -> Any:
    """
    Convert an object to a JSON-serializable format and verify serializability.

    Args:
    obj (Any): The object to convert.

    Returns:
    Any: A JSON-serializable representation of the object.

    Raises:
    ValueError: If the object cannot be serialized to JSON.
    """
    try:
        serializable_obj = to_serializable(obj)
        json.dumps(serializable_obj)
        return serializable_obj
    except (TypeError, OverflowError, ValueError) as e:
        raise ValueError(f"Object is not JSON serializable: {str(e)}")


def get_filename(location_req: ReqLocation) -> str:
    """
    Generates a filename based on the location request parameters.

    Args:
    location_req (ReqLocation): The location request object.

    Returns:
    str: The generated filename.
    """
    try:
        lat, lng, radius, place_type = (
            location_req.lat,
            location_req.lng,
            location_req.radius,
            location_req.type,
        )
        return f"{STORAGE_DIR}/data_{lat}_{lng}_{radius}_{place_type}.json"
    except AttributeError as e:
        raise ValueError(f"Invalid location request object: {str(e)}")


async def get_data_from_storage(location_req: ReqLocation) -> Optional[Dict]:
    """
    Retrieves data from storage based on the location request.
    """
    filename = get_filename(location_req)
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                return json.load(file)
        return None
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error parsing data file")
    except IOError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error reading data file")


async def get_dataset_from_storage(dataset_id: str) -> Optional[Dict]:
    """
    Retrieves a dataset from storage based on the dataset ID.
    """
    filename = f"{STORAGE_DIR}/catalogue_data_{dataset_id}.json"
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                return json.load(file)
        return None
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error parsing dataset file")
    except IOError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error reading dataset file")


async def store_data(location_req: ReqLocation, data: Dict) -> None:
    """
    Stores data in a file based on the location request.
    """
    filename = get_filename(location_req)
    try:
        with open(filename, "w") as file:
            json.dump(data, file)
    except IOError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error writing data file")


async def search_metastore_for_string(string_search: str) -> Optional[Dict]:
    """
    Searches the metastore for a given string and returns the corresponding data if found.
    """
    meta_file_path = os.path.join(METASTORE_PATH, string_search)
    try:
        if os.path.exists(meta_file_path):
            with open(meta_file_path, "r") as f:
                return json.load(f)
        return None
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error parsing metastore file")
    except IOError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error reading metastore file")


def load_dataset_layer_matching() -> Dict:
    """ """
    try:
        with open(DATASET_LAYER_MATCHING_PATH, "r") as f:
            dataset_layer_matching = json.load(f)
        return dataset_layer_matching
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset layer matching file not found",
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error parsing dataset layer matching file",
        )



def fetch_dataset_id(
    lyr_id: str, dataset_layer_matching: Dict = None
) -> Tuple[str, Dict]:
    """
    Searches for the dataset ID associated with a given layer ID. This function
    reads the dataset-layer matching file and iterates through it to find the
    corresponding dataset for a given layer.
    """
    if dataset_layer_matching is None:
        dataset_layer_matching = load_dataset_layer_matching()

    for d_id, dataset_info in dataset_layer_matching.items():
        if lyr_id in dataset_info["prdcer_lyrs"]:
            return d_id, dataset_info
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found for this layer"
    )



def load_dataset(dataset_id: str) -> Dict:
    """
    Loads a dataset from file based on its ID.
    """
    dataset_filepath = os.path.join(DATASETS_PATH, f"{dataset_id}.json")
    try:
        with open(dataset_filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dataset file not found"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error parsing dataset file",
        )



def fetch_layer_owner(prdcer_lyr_id: str) -> str:
    """
    Fetches the owner of a layer based on the producer layer ID.
    """
    try:
        with open(USER_LAYER_MATCHING_PATH, "r") as f:
            user_layer_matching = json.load(f)
        layer_owner_id = user_layer_matching.get(prdcer_lyr_id)
        if not layer_owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Layer owner not found"
            )
        return layer_owner_id
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User layer matching file not found",
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error parsing user layer matching file",
        )



def load_user_profile(user_id: str) -> Dict:
    """
    Loads user data from a file based on the user ID.
    """
    user_file_path = os.path.join(USERS_PATH, f"user_{user_id}.json")
    try:
        with open(user_file_path, "r") as f:
            user_data = json.load(f)
        return user_data
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User profile does not exist"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error parsing user profile",
        )



def update_dataset_layer_matching(
    prdcer_lyr_id: str, bknd_dataset_id: str, records_count: int = 9191919
):
    try:
        if os.path.exists(DATASET_LAYER_MATCHING_PATH):
            with open(DATASET_LAYER_MATCHING_PATH, "r") as f:
                dataset_layer_matching = json.load(f)
        else:
            dataset_layer_matching = {}

        if bknd_dataset_id not in dataset_layer_matching:
            dataset_layer_matching[bknd_dataset_id] = {
                "records_count": records_count,
                "prdcer_lyrs": [],
            }

        if prdcer_lyr_id not in dataset_layer_matching[bknd_dataset_id]["prdcer_lyrs"]:
            dataset_layer_matching[bknd_dataset_id]["prdcer_lyrs"].append(prdcer_lyr_id)

        dataset_layer_matching[bknd_dataset_id]["records_count"] = records_count

        with open(DATASET_LAYER_MATCHING_PATH, "w") as f:
            json.dump(dataset_layer_matching, f, indent=2)
    except IOError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating dataset layer matching",
        )



def update_user_layer_matching(layer_id: str, layer_owner_id: str):
    try:
        with open(USER_LAYER_MATCHING_PATH, "r+") as f:
            user_layer_matching = json.load(f)
            user_layer_matching[layer_id] = layer_owner_id
            f.seek(0)
            json.dump(user_layer_matching, f, indent=2)
            f.truncate()
    except IOError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user layer matching",
        )



def update_user_profile(user_id: str, user_data: Dict):
    user_file_path = os.path.join(USERS_PATH, f"user_{user_id}.json")
    try:
        with open(user_file_path, "w") as f:
            json.dump(user_data, f, indent=2)
    except IOError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user profile",
        )



def fetch_user_layers(user_id: str) -> Dict[str, Any]:
    try:
        user_data = load_user_profile(user_id)
        user_layers = user_data.get("prdcer", {}).get("prdcer_lyrs", {})
        return user_layers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user layers: {str(e)}",
        )



def fetch_user_catalogs(user_id: str) -> Dict[str, Any]:
    try:
        user_data = load_user_profile(user_id)
        user_catalogs = user_data.get("prdcer", {}).get("prdcer_ctlgs", {})
        return user_catalogs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user catalogs: {str(e)}",
        )



def create_new_user(user_id: str, username: str, email: str) -> None:
    user_file_path = os.path.join(USERS_PATH, f"user_{user_id}.json")

    if os.path.exists(user_file_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile already exists",
        )

    user_data = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "prdcer": {"prdcer_lyrs": {}, "prdcer_ctlgs": {}},
    }

    try:
        with open(user_file_path, "w") as f:
            json.dump(user_data, f, indent=2)
    except IOError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating new user profile",
        )



def load_store_catalogs() -> Dict[str, Any]:
    try:
        with open(STORE_CATALOGS_PATH, "r") as f:
            store_ctlgs = json.load(f)
        return store_ctlgs
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store catalogs file not found",
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error parsing store catalogs file",
        )



def save_dataset(bknd_dataset_id: str, dataset: Dict):
    """Save the dataset to a file"""
    try:
        with open(f"{DATASETS_PATH}/{bknd_dataset_id}.json", "w") as f:
            json.dump(dataset, f)
    except IOError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving dataset",
        )



def update_metastore(ccc_filename: str, bknd_dataset_id: str):
    """Update the metastore with the new layer information"""
    if bknd_dataset_id is not None:
        try:
            metastore_data = {
                "bknd_dataset_id": bknd_dataset_id,
                "created_at": datetime.now().isoformat(),
            }
            with open(f"{METASTORE_PATH}/{ccc_filename}", "w") as f:
                json.dump(metastore_data, f)
        except IOError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating metastore",
            )



def get_country_code(country_name: str) -> str:
    country_codes = {"United Arab Emirates": "AE", "Saudi Arabia": "SA", "Canada": "CA"}
    return country_codes.get(country_name, "")



async def fetch_country_city_data() -> Dict[str, List[Dict[str, float]]]:
    """
    Returns a set of country and city data for United Arab Emirates, Saudi Arabia, and Canada.
    The data is structured as a dictionary where keys are country names and values are lists of cities.
    """
    data = {
        "United Arab Emirates": [
            {"name": "Dubai", "lat": 25.2048, "lng": 55.2708},
            {"name": "Abu Dhabi", "lat": 24.4539, "lng": 54.3773},
            {"name": "Sharjah", "lat": 25.3573, "lng": 55.4033},
        ],
        "Saudi Arabia": [
            {"name": "Riyadh", "lat": 24.7136, "lng": 46.6753},
            {"name": "Jeddah", "lat": 21.5433, "lng": 39.1728},
            {"name": "Mecca", "lat": 21.4225, "lng": 39.8262},
        ],
        "Canada": [
            {"name": "Toronto", "lat": 43.6532, "lng": -79.3832},
            {"name": "Vancouver", "lat": 49.2827, "lng": -123.1207},
            {"name": "Montreal", "lat": 45.5017, "lng": -73.5673},
        ],
    }
    return data



async def fetch_nearby_categories() -> Dict:
    """
    Provides a comprehensive list of nearby place categories, organized into
    broader categories. This function returns a large, predefined dictionary
    of categories and subcategories, covering various aspects of urban life
    such as automotive, culture, education, entertainment, and more.
    """
    try:
        with open("Backend/google_categories.json", "r") as f:
            categories = json.load(f)
        return categories
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categories file not found"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error parsing categories file",
        )



def generate_layer_id() -> str:
    return "l" + str(uuid.uuid4())



def generate_user_id() -> str:
    file_path = "Backend/users_info.json"

    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            existing_ids = set(user["user_id"] for user in data.get("users", []))
    except FileNotFoundError:
        existing_ids = set()
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error parsing users info file",
        )

    while True:
        new_id = str(uuid.uuid4())
        if new_id not in existing_ids:
            return new_id



def load_users_info() -> Dict:
    try:
        if os.path.exists(USERS_INFO_PATH):
            with open(USERS_INFO_PATH, "r") as f:
                return json.load(f)
        return {"users": []}
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error parsing users info file",
        )



def save_users_info(users_info: Dict):
    try:
        with open(USERS_INFO_PATH, "w") as f:
            json.dump(users_info, f, indent=2)
    except IOError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving users info",
        )



def is_username_or_email_taken(username: str, email: str) -> bool:
    users_info = load_users_info()
    for user in users_info["users"]:
        if user["username"] == username or user["email"] == email:
            return True
    return False



def add_user_to_info(user_id: str, username: str, email: str, hashed_password: str):
    users_info = load_users_info()
    users_info["users"].append(
        {
            "user_id": user_id,
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
        }
    )
    save_users_info(users_info)



def get_user_by_username(username: str) -> Optional[Dict]:
    users_info = load_users_info()
    for user in users_info["users"]:
        if user["username"] == username:
            return user
    return None





# Apply the decorator to all functions in this module
apply_decorator_to_module(logger)(__name__)
