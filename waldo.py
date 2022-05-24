import sys
import os
import json
import time
import requests
from dotenv import load_dotenv

if __name__ == "__main__":

    # globals
    dotenv_path = str.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    API_KEY = os.environ.get("API_KEY")
    if API_KEY == None:
        raise Exception("API key not found in .env file in base directory.")
    HEADERS = {"Authorization": "Bearer "+ API_KEY }

    BASE_URL = 'developers.clearview.ai'

    CREATE_URL = BASE_URL + '/v1/collections'
    ADD_URL = BASE_URL + '/v1/collections/{collection_name}/images_file'
    SEARCH_URL = BASE_URL + '/v1/collections/{collection_name}/search_file'
    COMPARE_URL = BASE_URL + '/v1/compare_images_file'
    DETECT_URL = BASE_URL + '/v1/detect_image_file'

    # given an image with one main face, searches a second image for the main face
    def find(probe_image, ref_image):

        # creates collection to search in
        # still succeeds if the collection has already been created
        collection_name = "WaldoSearch"
        create_response, success = createCollection(collection_name, False)
        if not success:
            raise Exception(f"\n\n- Exception: Failed to create or access collection '{collection_name}'.\n")

        # adds reference image to temp collection
        add_response, success = addCollection(collection_name, ref_image, False)
        attempts = 1
        while add_response.status_code == 403 and attempts < 12:
            print(f"\nWaiting for new collection to come online before searching...")
            time.sleep(2)
            add_response, success = addCollection(collection_name, ref_image, False)
            attempts = attempts + 1
        if not success:
            raise Exception(f"\n\n- Exception: Failed to add reference image '{ref_image}' to collection '{collection_name}'. Please wait a minute and try again.\n")

        time.sleep(5)

        # searches temp collection with probe image
        search_response, success = searchCollection(collection_name, probe_image, True)
        if not success:
            raise Exception(f"\n\n- Exception: Failed to search collection '{collection_name}' with image '{probe_image}'.\n")

    # creates a collection given a name
    def createCollection(collection_name, verbose):

        res = requests.post(
            url=CREATE_URL,
            headers=HEADERS,
            json={"collection_name": collection_name},
        )

        # prints result and returns response
        if res.status_code == 201:
            if verbose:
                print(f"\n- Created collection '{collection_name}'.\n")
            return res, True
        elif res.status_code == 409:
            if verbose:
                print(f"\n- Collection '{collection_name}' already exists.\n")
            return res, True
        else:
            if verbose:
                print(f"\n- Create collection returned HTTP code {res.status_code}.\n")
            return res, False
        
    # adds image to collection given a name and image path
    def addCollection(collection_name, image_path, verbose):

        metadata = { "foo" : "bar" }
        metadata = json.dumps(metadata)
        data = {}
        data['image_metadata'] = metadata

        res = requests.post(
            url=ADD_URL.format(collection_name=collection_name),
            files={'image': open(image_path, 'rb')},
            headers=HEADERS,
            data=data
        )

        # prints result and returns response
        if res.status_code == 201:
            if verbose:
                print(f"\n- Added '{image_path}' to collection '{collection_name}'.\n")
            return res, True
        elif res.status_code == 409:
            if verbose:
                print(f"\n- Image '{image_path}' already exists in collection '{collection_name}'.\n")
            return res, True
        else:
            if verbose:
                print(f"\n- Add collection returned HTTP code {res.status_code}.\n")
            return res, False
        
    # searches a collection given a name and image path
    def searchCollection(collection_name, image_path, verbose):

        res = requests.post(
            url=SEARCH_URL.format(collection_name=collection_name),
            files={'image': open(image_path, 'rb')},
            headers=HEADERS,
            data={"all_faces": True}
        )

        # lists search results with similarity and bounding box
        if res.status_code == 201:
            if verbose:
                response = res.json()
                number_of_results = response['data']['total_items']
                if number_of_results == 1:
                    print(f"\nFound results in {number_of_results} image in collection {collection_name}.")
                else:
                    print(f"\nFound results in {number_of_results} images in collection {collection_name}.")
                if number_of_results > 0:
                    for result in response['data']['items']:
                        for face in result["faces_found"]:
                            print(f"- Found match in image {result['image']['image_id']}, similarity {round(face['similarity'], 2)}, coordinates ({face['bounding_box'][0]}, {face['bounding_box'][1]}).")
                print("\n")
            return res, True
        else:
            if verbose:
                print(f"\n- Search of collection '{collection_name}' returned HTTP code {res.status_code}.\n")
            return res, False

    # returns similarity of two images
    def compare(image1, image2):

        files={'image_a': open(image1, 'rb'), 'image_b': open(image2, 'rb')}

        res = requests.post(
            url=COMPARE_URL,
            headers=HEADERS,
            files=files
        )

        if res.status_code == 200:
            response = res.json()
            print(f"\n- Images share a similarity score of {round(response['data']['similarity'], 2)}.\n")
        else:
            print(f"\n- Image compare returned HTTP code {res.status_code}.\n")

    # detects face locations in image
    def detect(image):

        files={'image': open(image, 'rb')}
        data={"all_faces": True}

        res = requests.post(
            url=DETECT_URL,
            headers=HEADERS,
            files=files,
            data=data
        )

        if res.status_code == 201:
            response = res.json()
            if response['data']['total_items'] == 0:
                print(f"\nFound no faces in {image}.")
            elif response['data']['total_items'] == 1:
                print(f"\nFound {response['data']['total_items']} face in {image}.")
                for item in response['data']['items']:
                    print(f"- Found face at ({item['bounding_box'][0]},{item['bounding_box'][1]}).\n")
            else:
                print(f"\nFound {response['data']['total_items']} faces in {image}.")
                for item in response['data']['items']:
                    print(f"- Found face at ({item['bounding_box'][0]},{item['bounding_box'][1]}).")
                print("\n")
        else:
            print(f"\n- Image detection of '{image}' returned HTTP code {res.status_code}.\n")

    # gets operation argument
    operation = sys.argv[1]

    # calls operation method
    if operation == "find":
        if(len(sys.argv) == 4):
            find(sys.argv[2], sys.argv[3])
        else:
            raise Exception("\n- Incorrect number of arguments for 'find'.\n- Correct syntax: find <probe_image_path> <reference_image_path>\n")
    elif operation == "create-collection":
        if(len(sys.argv) == 3):
            createCollection(sys.argv[2], True)
        else:
            raise Exception("\n- Incorrect number of arguments for 'create-collection'.\n- Correct syntax: create-collection <collection_name>\n")
    elif operation == "add-collection":
        if(len(sys.argv) == 4):
            addCollection(sys.argv[2], sys.argv[3], True)
        else:
            raise Exception("\n- Incorrect number of arguments for 'add-collection'.\n- Correct syntax: add-collection <collection_name> <image_path>\n")
    elif operation == "search-collection":
        if(len(sys.argv) == 4):
            searchCollection(sys.argv[2], sys.argv[3], True)
        else:
            raise Exception("\n- Incorrect number of arguments for 'search-collection'.\n- Correct syntax: search-collection <collection_name> <image_path>\n")
    elif operation == "compare":
        if(len(sys.argv) == 4):
            compare(sys.argv[2], sys.argv[3])
        else:
            raise Exception("\n- Incorrect number of arguments for 'compare'.\n- Correct syntax: compare <image_1> <image_2>\n")
    elif operation == "detect":
        if(len(sys.argv) == 3):
            detect(sys.argv[2])
        else:
            raise Exception("\n- Incorrect number of arguments for 'detect'.\n- Correct syntax: detect <image_path>\n")
    else:
        print('''Invalid operation. Accepted operations are:
            find <probe_image_path> <reference_image_path>
            create-collection <collection_name>
            add-collection <collection_name> <image_path>
            search-collection <collection_name> <image_path>
            compare <image_1> <image_2>
            detect <image_path>
            ''')