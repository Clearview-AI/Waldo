# Waldo ReadMe.md

The purpose of the Waldo app is to provide a basic rundown of the capabilities of the Consent API. The Waldo app has the following functionalities:

1. Given a probe image, find instances of the probe face in a second image.
2. Managing and searching collections of images.
3. Other examples: compare and detect.

## Setup

1. Software prerequisites:
   1. Python3
   2. Python packages:
      1. requests ([Link](https://docs.python-requests.org/en/latest/))
      2. dotenv ([Link](https://pypi.org/project/python-dotenv/))
2. Download Waldo.py and place in a convenient directory.
3. In the Consent web app, generate an API key and copy the key.
4. In the same folder as Waldo.py, create a file called ‘.env’ with the following contents:

   ```bash
   API_KEY=paste_your_api_key_here
   ```

## Find a face in a second image

1. Place a probe image in the same folder as Waldo.py. The face of interest should be the largest face in this image or should be cropped so that it is the only face.
2. Place the image to be searched in the same folder as Waldo.py.
3. In the command line, execute the following command:

```bash
python3 waldo.py find <probe_image_name> <second_image_name>
```

1. Example output for a match is as follows:

```bash
Found results in 1 image in collection WaldoSearch.
- Found match in image 636ddcc169c82c8bf3d09f87287b61e0, similarity 0.83, coordinates (229, 32).
```

Note: The output references the collection ‘WaldoSearch’ because the implementation of this function is adding the reference image to a collection called ‘WaldoSearch’ and then searching that collection with the probe image.

## Managing and searching collections

Collections are databases of images that can be created, added to, and searched.

### Create a collection

A collection can be created with the following command:

```bash
python3 waldo.py create-collection <collection_name>
```

### Add an image to a collection

An image can be added to an existing collection with the following command:

```bash
python3 waldo.py add-collection <image_name>
```

### Search a collection with an image

A collection can be searched using a provided image using the following command.

```bash
python3 waldo.py search-collection <collection_name> <image_name>
```

Note: The provided image should either be cropped to the face or the face of interest should be largest in the image.

## Other examples

Two other functions are included in Waldo.py: compare and detect. These can be called to demonstrate their corresponding endpoints.

### Compare

The compare function accepts two image paths and will return the similarity score shared between the largest faces in each image.

```bash
python3 waldo.py compare <image1_name> <image2_name>
```

### Detect

The detect function accepts an image path and returns the coordinates of faces in the image, in pixels.

```bash
python3 waldo.py detect <image_name>
```
