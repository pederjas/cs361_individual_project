CS361 Individual Project - Pet Finder


Hosting TBD: I have not deployed this yet... but you can go ahead an run it locally, if you're so inclined.


Getting started (steps if you want to run this on your own):
* clone repo
* create a virtual environment: python -m venv venv
* activate the virtual environment: source venv/bin/activate
* install dependencies: pip install -r requirements.txt
* create a file at the root of the project called: "google_api_key" and copy and paste your google "places" api key into the file
* startup flask: flask run


Making requests; this services exposes two API services: places_api and place_detail_api ... accessible through http GET requests:

1. /places_api ... takes three parameters: 
* zip_code
* radius_miles
* keywords (keywords is a comma delimited list, url-encoded "%2C" or not should still work with the flask requests library)
* Example Request: http://127.0.0.1:5000/places_api?zip_code=97116&radius_miles=10&keywords=pets,veterinary
* Example Response:
```
[{
    business_status: "OPERATIONAL",
    distance_miles: 3.4,
    geometry: {
        location: {
            lat: 45.6183988,
            lng: -123.1146567
        },
        viewport: {
            northeast: {
                lat: 45.61974842989272,
                lng: -123.1132174701073
            },
            southwest: {
                lat: 45.61704877010727,
                lng: -123.1159171298928
            }
        }
    },
    icon: "https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/generic_business-71.png",
    icon_background_color: "#7B9EB0",
    icon_mask_base_uri: "https://maps.gstatic.com/mapfiles/place_api/icons/v2/generic_pinlet",
    name: "Banks Veterinary Service",
    opening_hours: {
        open_now: false
    },
    photos: [{
        height: 5312,
        html_attributions: [
            "<a href="
            https: //maps.google.com/maps/contrib/113637864926839469960">James Griffith</a>"
        ],
        photo_reference: "AfLeUgM_oulB--FH2gA9LPMwGMrSNX2GX9xkAgrAxyoha0Oyj-BWuLHTxM_MFptZfqQS5WJvBT75a72Hd3uv2zTjS0mHL9dn7AkW14NZ9PAvmnghOWrI62SJDdJRRQF9gF-2B3i1apV9VC-rImls5gW0vX0gVCK-6XSv6ITeR4v3bzFdraTy",
        width: 2988
    }],
    place_id: "ChIJVVVVVUAdlVQRnZRoyaPTbQc",
    plus_code: {
        compound_code: "JV9P+94 Banks, Oregon",
        global_code: "84QRJV9P+94"
    },
    rating: 4.7,
    reference: "ChIJVVVVVUAdlVQRnZRoyaPTbQc",
    scope: "GOOGLE",
    types: [
        "veterinary_care",
        "point_of_interest",
        "establishment"
    ],
    user_ratings_total: 283,
    vicinity: "13541 NW Main St, Banks"
}]
```

2. /place_detail_api ... takes a single parameter
NOTE: Careful with the place_detail_api as it does charge per request $0.003 per call (adds up)... which is why this is a separate endpoint (prefer user interaction) and I have not included my google_api_key ;)
* place_id (obtained from the /places_api JSON response)
* Example Request: http://127.0.0.1:5000/place_detail_api?place_id=ChIJ-z9MCdUblVQRu4KBPhaDBlk
* Example Response:
```
{
    formatted_address: "2625 Pacific Ave, Forest Grove, OR 97116, USA",
    formatted_phone_number: "(503) 357-8880",
    name: "Pacific Avenue Veterinary Clinic",
    place_id: "ChIJ-z9MCdUblVQRu4KBPhaDBlk",
    url: "https://maps.google.com/?cid=6414958850797044411",
    website: "https://www.pacificavenuevetclinic.com/"
}
```

Basic UML:

![alt text](uml.png "UML Sequence Diagram")
