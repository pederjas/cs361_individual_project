from flask import Flask, request, render_template, redirect
import random
import gmaps
import zmq
import json

app = Flask(__name__)
pet_data = None

@app.route('/places_api', methods=['GET'])
def places_api():
    return gmaps.get_places(zip_code=request.args.get('zip_code'), radius_miles=request.args.get('radius_miles'), keywords=request.args.get('keywords'))

@app.route('/place_detail_api', methods=['GET'])
def place_detail_api():
    return gmaps.get_place_detail(place_id = request.args.get('place_id'))

@app.route('/petfinder_api', methods=['GET'])
def petfinder_api(animal_type=None, zipcode=97116, distance=100, qty=100):
    # Animal types must of the following: ('dog', 'cat', 'rabbit', 'small-furry', 'horse', 'bird', 'scales-fins-other', 'barnyard')
    context = zmq.Context()
    print("Connecting to zeromq server…")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    if animal_type is not None:
        request = {"animal_type": animal_type, "zipcode": zipcode, "distance": distance, "qty": qty}
    else:
        request = {"zipcode": zipcode, "distance": distance, "qty": qty}
    json_request = json.dumps(request)
    print(f"Sending request: {json_request}")
    socket.send_json(request)
    res = socket.recv_json()
    print(f"Response received...")
    return res

@app.route('/get_pet_data', methods=['GET'])
def get_pet_data():
    global pet_data
    if pet_data is None:
        pet_data = {}
        for pet_info in petfinder_api()['animals']:

            this_info = {}
            this_info['category'] = pet_info['species'] if str(pet_info['species']).lower() == 'dog' or str(pet_info['species']).lower() == 'cat' else 'other' 
            this_info['pet_id'] = pet_info['id']
            this_info['name'] = pet_info['name'].strip()
            this_info['description'] = pet_info['description']
            this_info['age'] = pet_info['age']
            this_info['photo_primary'] = pet_info['primary_photo_cropped']['small'] if pet_info['primary_photo_cropped'] is not None else 'static/img/placeholder.jpg'
            this_info['date_intake'] = pet_info['published_at'].split('T')[0]
            this_info['shelter_id'] = pet_info['organization_id']
            this_info['status'] = pet_info['status']
            this_info['size'] = pet_info['size']
            this_info['gender'] = pet_info['gender']
            this_info['profile_url'] = pet_info['url']

            tags_list = []
            try: 
                tags_list.append(pet_info['name']) 
            except: 
                pass
            try: 
                tags_list.append(pet_info['gender'])
            except: 
                pass
            try: 
                tags_list.append(pet_info['colors']['primary'])
            except: 
                pass
            try:
                tags_list.append(pet_info['colors']['secondary'])
            except:
                pass
            try:
                tags_list.append(pet_info['breeds']['primary'])
            except:
                pass
            try:
                tags_list.append(pet_info['breeds']['secondary'])
            except:
                pass
            tags_clean = []
            for tag in tags_list:
                if tag is not None:
                    tags_clean.append(tag)
            this_info['tags'] = ' / '.join(tags_clean)

            pet_data[pet_info['id']] = this_info

    return pet_data

@app.route('/', methods=['GET'])
def index():

    global pet_data
    if len(request.args) == 0:
        pet_data = None
    pet_data = get_pet_data()
    pet_data_filtered = {}

    data = {}
    data['filter'] = {}
    # exact match
    data['filter']['category'] = request.args.get('category') if request.args.get('category') is not None else ''
    data['filter']['pet_id'] = request.args.get('pet_id') if request.args.get('pet_id') is not None else ''
    data['filter']['name'] = request.args.get('name') if request.args.get('name') is not None else ''
    data['filter']['gender'] = request.args.get('gender') if request.args.get('gender') is not None else ''
    data['filter']['age'] = request.args.get('age') if request.args.get('age') is not None else ''
    data['filter']['size'] = request.args.get('size') if request.args.get('size') is not None else ''
    data['filter']['shelter_id'] = request.args.get('shelter_id') if request.args.get('shelter_id') is not None else ''
    data['filter']['date_intake'] = request.args.get('date_intake') if request.args.get('date_intake') is not None else ''
    # fuzzy match
    data['filter']['tags'] = request.args.get('tags') if request.args.get('tags') is not None else ''
    data['filter']['breed'] = request.args.get('breed') if request.args.get('breed') is not None else ''
    data['filter']['color'] = request.args.get('color') if request.args.get('color') is not None else ''
    # todo
    data['filter']['sort_by'] = request.args.get('sort_by') if request.args.get('sort_by') is not None else ''
    data['filter']['sort_order'] = request.args.get('sort_order') if request.args.get('sort_order') is not None else ''

    for pet_id in pet_data:
        pet_info = pet_data[pet_id]
        keep = True
        for filter in data['filter']:
            if request.args.get(filter) is not None:
                if filter == 'tags':
                    if request.args.get(filter).lower() not in str(pet_info[filter]).lower():
                        keep = False
                else:
                    if request.args.get(filter).lower() != str(pet_info[filter]).lower():
                        keep = False
        if keep:
            pet_data_filtered[pet_id] = pet_info

    data['pet_data'] = pet_data_filtered

    return render_template('index.html', data=data)

@app.route('/details', methods=['GET'])
def details():
    pet_data = get_pet_data()
    if request.args.get('pet_id') is not None:
        return render_template('details.html', data=pet_data[int(request.args.get('pet_id'))])
    else:
        return redirect('/details?pet_id=%s' % (random.choice(list(pet_data.keys()))))

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

# pet data stubb...
def get_pet_data_mockup():
    global pet_data
    if pet_data is None:
        pet_data = {}
        breeds_dogs = ["Affenpinscher", "Afghan Hound", "African Hunting Dog", "Airedale Terrier", "Akbash Dog", "Akita", "Alapaha Blue Blood Bulldog", "Alaskan Husky", "Alaskan Malamute", "American Bulldog", "American Bully", "American Eskimo Dog", "American Eskimo Dog (Miniature)", "American Foxhound", "American Pit Bull Terrier", "American Staffordshire Terrier", "American Water Spaniel", "Anatolian Shepherd Dog", "Appenzeller Sennenhund", "Australian Cattle Dog", "Australian Kelpie", "Australian Shepherd", "Australian Terrier", "Azawakh", "Barbet", "Basenji", "Basset Bleu de Gascogne", "Basset Hound", "Beagle", "Bearded Collie", "Beauceron", "Bedlington Terrier", "Belgian Malinois", "Belgian Tervuren", "Bernese Mountain Dog", "Bichon Frise", "Black and Tan Coonhound", "Bloodhound", "Bluetick Coonhound", "Boerboel", "Border Collie", "Border Terrier", "Boston Terrier", "Bouvier des Flandres", "Boxer", "Boykin Spaniel", "Bracco Italiano", "Briard", "Brittany", "Bull Terrier", "Bull Terrier (Miniature)", "Bullmastiff", "Cairn Terrier", "Cane Corso", "Cardigan Welsh Corgi", "Catahoula Leopard Dog", "Caucasian Shepherd (Ovcharka)", "Cavalier King Charles Spaniel", "Chesapeake Bay Retriever", "Chinese Crested", "Chinese Shar-Pei", "Chinook", "Chow Chow", "Clumber Spaniel", "Cocker Spaniel", "Cocker Spaniel (American)", "Coton de Tulear", "Dalmatian", "Doberman Pinscher", "Dogo Argentino", "Dutch Shepherd", "English Setter", "English Shepherd", "English Springer Spaniel", "English Toy Spaniel", "English Toy Terrier", "Eurasier", "Field Spaniel", "Finnish Lapphund", "Finnish Spitz", "French Bulldog", "German Pinscher", "German Shepherd Dog", "German Shorthaired Pointer", "Giant Schnauzer", "Glen of Imaal Terrier", "Golden Retriever", "Gordon Setter", "Great Dane", "Great Pyrenees", "Greyhound", "Griffon Bruxellois", "Harrier", "Havanese", "Irish Setter", "Irish Terrier", "Irish Wolfhound", "Italian Greyhound", "Japanese Chin", "Japanese Spitz", "Keeshond", "Komondor", "Kooikerhondje", "Kuvasz", "Labrador Retriever", "Lagotto Romagnolo", "Lancashire Heeler", "Leonberger", "Lhasa Apso", "Maltese", "Miniature American Shepherd", "Miniature Pinscher", "Miniature Schnauzer", "Newfoundland", "Norfolk Terrier", "Norwich Terrier", "Nova Scotia Duck Tolling Retriever", "Old English Sheepdog", "Olde English Bulldogge", "Papillon", "Pekingese", "Pembroke Welsh Corgi", "Perro de Presa Canario", "Pharaoh Hound", "Plott", "Pomeranian", "Poodle (Miniature)", "Poodle (Toy)", "Pug", "Puli", "Pumi", "Rat Terrier", "Redbone Coonhound", "Rhodesian Ridgeback", "Rottweiler", "Russian Toy", "Saint Bernard", "Saluki", "Samoyed", "Schipperke", "Scottish Deerhound", "Scottish Terrier", "Shetland Sheepdog", "Shiba Inu", "Shih Tzu", "Shiloh Shepherd", "Siberian Husky", "Silky Terrier", "Smooth Fox Terrier", "Soft Coated Wheaten Terrier", "Spanish Water Dog", "Spinone Italiano", "Staffordshire Bull Terrier", "Standard Schnauzer", "Swedish Vallhund", "Thai Ridgeback", "Tibetan Mastiff", "Tibetan Spaniel", "Tibetan Terrier", "Toy Fox Terrier", "Treeing Walker Coonhound", "Vizsla", "Weimaraner", "Welsh Springer Spaniel", "West Highland White Terrier", "Whippet", "White Shepherd", "Wire Fox Terrier", "Wirehaired Pointing Griffon", "Wirehaired Vizsla", "Xoloitzcuintli", "Yorkshire Terrier"]
        breeds_cats = ["Abyssinian", "Aegean", "American Curl", "American Bobtail", "American Shorthair", "American Wirehair", "Arabian Mau", "Australian Mist", "Asian", "Asian Semi-longhair", "Balinese", "Bambino", "Bengal", "Birman", "Bombay", "Brazilian Shorthair", "British Semi-longhair", "British Shorthair", "British Longhair", "Burmese", "Burmilla", "California Spangled", "Chantilly-Tiffany", "Chartreux", "Chausie", "Cheetoh", "Colorpoint Shorthair", "Cornish Rex", "Cymric", "Cyprus", "Devon Rex", "Donskoy", "Dragon Li", "Dwarf cat", "Egyptian Mau", "European Shorthair", "Exotic Shorthair", "Foldex", "German Rex", "Havana Brown", "Highlander", "Himalayan", "Japanese Bobtail", "Javanese", "Karelian Bobtail", "Khao Manee", "Korat", "Korean Bobtail", "Korn Ja", "Kurilian Bobtail", "LaPerm", "Lykoi", "Maine Coon", "Manx", "Mekong Bobtail", "Minskin", "Munchkin", "Nebelung", "Napoleon", "Norwegian Forest cat", "Ocicat", "Ojos Azules", "Oregon Rex", "Oriental Bicolor", "Oriental Shorthair", "Oriental Longhair", "PerFold", "Persian (Modern Persian Cat)", "Persian (Traditional Persian Cat)", "Peterbald", "Pixie-bob", "Raas", "Ragamuffin", "Ragdoll", "Russian Blue", "Russian White, Black and Tabby", "Sam Sawet", "Savannah", "Scottish Fold", "Selkirk Rex", "Serengeti", "Serrade petit", "Siamese", "Siberian", "Singapura", "Snowshoe", "Sokoke", "Somali", "Sphynx", "Suphalak", "Thai", "Thai Lilac", "Tonkinese", "Toyger", "Turkish Angora", "Turkish Van", "Ukrainian Levkoy"]
        breeds_other = ["Lizard", "Bird", "Fish", "Mouse", "Rat"]
        category_list = []
        for _ in breeds_dogs:
            category_list.append("dogs")
        for _ in breeds_cats:
            category_list.append("cats")
        for _ in breeds_other:
            category_list.append("other")
        colors = ["Black", "Brown", "Yellow", "White", "Blue Merle", "Red Merle", "Tri-Color", "Spotted", "Striped"]
        name_list = ["Ace", "Alma", "Archie", "Aspen", "Bailey", "Bandit", "Bear", "Beau", "Bentley", "Beso", "Bruno", "Buddy", "Chandler", "Coco", "Conejito", "Diego", "Dixie", "Duke", "Durango", "Esmerelda ", "Fernando", "Finn", "Ginger", "Gracie", "Gunther", "Gus", "Hank", "Hazel", "Hermosa", "Hidalgo", "Ivy", "Jack", "Jax", "Joey", "Josefina", "Juno", "Kobe", "Kona", "Lady", "Leo", "Lexi", "Lily", "Loki", "Lola", "Louie", "Lucky", "Lucy", "Mariposa", "Maya", "Mia", "Molly", "Moose", "Murphey", "Nala", "Nina", "Nova", "Oliver", "Ollie", "Oscar", "Pablo", "Paco", "Paisley", "Perrita", "Piper", "Princess", "Riley", "Rosa", "Ross", "Roxy", "Scout", "Sofía", "Sonora ", "Stella", "Teddy", "Thor", "Tucker", "Willow", "Winnie", "Winston", "Xena"]
        for pet_id in range(1, 1000):
            pet_data[pet_id] = {}
            pet_data[pet_id]['category'] = random.choice(category_list)
            pet_data[pet_id]['shelter_id'] = random.randint(1, 10)
            pet_data[pet_id]['pet_id'] = pet_id

            if pet_data[pet_id]['category'] == "dogs":
                pet_data[pet_id]['breed'] = random.choice(breeds_dogs)
            elif pet_data[pet_id]['category'] == "cats":
                pet_data[pet_id]['breed'] = random.choice(breeds_cats)
            else:
                pet_data[pet_id]['breed'] = random.choice(breeds_other)
            pet_data[pet_id]['color'] = random.choice(colors)

            pet_data[pet_id]['name'] = random.choice(name_list)

            pet_data[pet_id]['date_intake'] = '2023-01-%02d' % (1 + random.randint(0, 15))
            pet_data[pet_id]['date_euthanization'] = '2023-03-%02d' % (1 + random.randint(0, 30))

            search_string = ''
            for search_field in ['name', 'color', 'category', 'breed']:
                search_string = '%s %s' % (search_string, pet_data[pet_id][search_field])

            pet_data[pet_id]['search'] = search_string
        for pet_id in pet_data:
            print(pet_data[pet_id])
    return pet_data