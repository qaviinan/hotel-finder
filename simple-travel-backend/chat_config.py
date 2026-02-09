import os

DEFAULT_PROMPT_WITH_HISTORY = """
    You are a financial Q&A expert who specializes in trading knowledge. Your responses must always be rooted in the context provided for each query.
    You are also provided with the conversation history with the user. Make sure to use relevant context from conversation history as needed.

    Here are some guidelines to follow:

    1. Refrain from explicitly mentioning the context provided in your response.
    2. The context should silently guide your answers without being directly acknowledged. Therefore do not mention things like 'chapter 4' or 'strategy 6'
    3. Do not use phrases such as 'According to the context provided', 'Based on the context, ...' etc.
    4. Make your answer descriptive, step-by-step and include all the technical details from the context

    Context information:
    ----------------------
    $context
    ----------------------

    Conversation history:
    ----------------------
    $history
    ----------------------

    Query: $query
    Answer:
    """ 
DEFAULT_PROMPT_WITHOUT_HISTORY = """
    You are a financial Q&A expert system. Your responses must always be rooted in the context provided for each query.

    Here are some guidelines to follow:

    1. Refrain from explicitly mentioning the context provided in your response.
    2. The context should silently guide your answers without being directly acknowledged.
    3. Do not use phrases such as 'According to the context provided', 'Based on the context, ...' etc.

    Context information:
    ----------------------
    $context
    ----------------------

    Query: $query
    Answer:
    """ 
HOTEL_QUERY_PROMPT = """
    Empty placeholders, please ignore: $context

    Write a python query for a dataframe of hotel listings. I will provide the column names, example values from each column and the user's query. Your task is to convert the user's query to a pandas query in the format I will specify. Here is the list of column names and data types;
    'bathroom_count : [1. 5. 6.]',
    'bed_count : [2 6 4]',
    'bedroom_count : [2. 1. 6.]',
    "city : ['Khet Huai Khwang' 'Huai Khwang' 'Huaikhwang']",
    "country : ['Thailand']",
    'guestControls/allowsChildren : [ True False]',
    'guestControls/allowsEvents : [False  True]',
    'guestControls/allowsInfants : [ True False]',
    'guestControls/allowsPets : [False  True]',
    'guestControls/allowsSmoking : [False  True]',
    'guestControls/personCapacity : [7 5 4]',
    'amenity_Kitchen : [ True False]',
    'amenity_Elevator : [ True False]',
    'amenity_Wifi : [ True False]',
    'amenity_Heating : [ True False]',
    'amenity_Iron : [ True False]',
    'amenity_Cable TV : [ True False]',
    'amenity_Gym : [ True False]',
    'amenity_Hair dryer : [ True False]',
    'amenity_Dryer : [False  True]',
    'amenity_Hangers : [ True False]',
    'amenity_Washer : [ True False]',
    'amenity_Essentials : [True False nan]',
    'amenity_Shampoo : [True False nan]',
    'amenity_Pool : [True False nan]',
    'amenity_Air conditioning : [True nan False]',
    'amenity_TV : [True nan False]',
    'amenity_Smoke alarm : [True False nan]',
    'amenity_Carbon monoxide alarm : [False True nan]',
    'amenity_Fire extinguisher : [True False nan]',
    'amenity_Coffee maker : [nan True False]',
    'amenity_Refrigerator : [nan True False]',
    'amenity_Dishwasher : [nan True False]',
    'amenity_Dishes and silverware : [nan True]',
    'amenity_Oven : [nan True]',
    'amenity_Stove : [nan True]',
    'amenity_BBQ grill : [nan True]',
    'amenity_Patio or balcony : [nan True]',
    'amenity_Backyard : [nan True]',
    'amenity_Cleaning available during stay : [nan True]',
    'amenity_Host greets you : [nan True]',
    'amenity_Waterfront : [nan True]',
    'amenity_Safe : [nan True]',
    'amenity_Board games : [nan True]',
    'amenity_Hot water kettle : [nan True]',
    'amenity_Sound system : [nan True]',
    'amenity_Outdoor shower : [nan True]',
    'amenity_Hot_water : [False nan True]',
    'amenity_Outdoor_dining_area : [nan True]',
    'amenity_Dining_table : [nan True]',
    'amenity_Outdoor_furniture : [nan True]',
    'amenity_Freezer : [nan True]',
    'maxNights : [1125  365   30]',
    'minNights : [  1 100   3]',
    'numberOfGuests : [7 5 4]',
    'pricing/rate/amount : [27001  7776  8100]',
    'reviewDetailsInterface/reviewCount : [12 40 53]',
    'Accuracy : [4.5 4.6 4.8]',
    'Communication : [4.5 4.6 4.8]',
    'Cleanliness : [4.3 4.2 4.5]',
    'Location : [4.8 4.7 4.6]',
    'Check-in : [4.7 4.5 4.8]',
    'Value : [4.7 4.2 4.5]',
    'reviewsModule/localizedOverallRating : [4.58 4.33 4.48]',
    'stars : [4.58 4.33 4.48]',
    "roomType : ['Entire condo' 'Entire rental unit' 'Private room in hostel']",
    "roomTypeCategory : ['entire_home' 'private_room' 'hotel_room' 'shared_room']"

    Now I will provide 2 successful examples of this task:
    User's query; Need at least 2 beds, 3 bathrooms. Price should be under 1000 and pets should be allowed
    Converted python query:
    df[
        (df['bed_count'] >= 2) &
        (df['bathroom_count'] >= 3) &
        (df['pricing/rate/amount'] < 1000) &
        (df['guestControls/allowsPets'] == True)
    ]

    User's query: Looking for rooms with at least 2 beds. Price must be less than 1000. Should have kitchen and wifi.
    Converted python query:
    df[
    (df['bed_count'] >= 2) &
    (df['pricing/rate/amount'] < 1000) &
    (df['amenity_Kitchen'] == True) &
    (df['amenity_Wifi'] == True)
    ]

    Now  I will provide the user's query, which you will convert to a python query. 
    Only return the query and no other text, so that I can directly run the query in a python interpreter.
    Also, if a part of the query does not match any columns, then simply ignore that part.
    User's query: $query
    """

FINAL_COLUMNS = [
 'idStr',
 'name',
 'address',
 'bathroom_count',
 'bed_count',
 'bedroom_count',
 'city',
 'country',
 'guestControls/allowsChildren',
 'guestControls/allowsEvents',
 'guestControls/allowsInfants',
 'guestControls/allowsPets',
 'guestControls/allowsSmoking',
 'guestControls/personCapacity',
 'guestControls/structuredHouseRules/0',
 'guestControls/structuredHouseRules/1',
 'guestControls/structuredHouseRules/2',
 'amenity_Kitchen',
 'amenity_Elevator',
 'amenity_Wifi',
 'amenity_Heating',
 'amenity_Iron',
 'amenity_Cable TV',
 'amenity_Gym',
 'amenity_Hair dryer',
 'amenity_Dryer',
 'amenity_Hangers',
 'amenity_Washer',
 'amenity_Essentials',
 'amenity_Shampoo',
 'amenity_Pool',
 'amenity_Air conditioning',
 'amenity_TV',
 'amenity_Smoke alarm',
 'amenity_Carbon monoxide alarm',
 'amenity_Fire extinguisher',
 'amenity_Coffee maker',
 'amenity_Refrigerator',
 'amenity_Dishwasher',
 'amenity_Dishes and silverware',
 'amenity_Oven',
 'amenity_Stove',
 'amenity_BBQ grill',
 'amenity_Patio or balcony',
 'amenity_Backyard',
 'amenity_Cleaning available during stay',
 'amenity_Host greets you',
 'amenity_Waterfront',
 'amenity_Safe',
 'amenity_Board games',
 'amenity_Hot water kettle',
 'amenity_Sound system',
 'amenity_Outdoor shower',
 'amenity_Hot_water',
 'amenity_Outdoor_dining_area',
 'amenity_Dining_table',
 'amenity_Outdoor_furniture',
 'amenity_Freezer',
 'maxNights',
 'minNights',
 'numberOfGuests',
 'photos/0/pictureUrl',
 'photos/0/thumbnailUrl',
 'photos/1/pictureUrl',
 'photos/1/thumbnailUrl',
 'photos/2/pictureUrl',
 'photos/2/thumbnailUrl',
 'photos/3/pictureUrl',
 'photos/3/thumbnailUrl',
 'photos/4/pictureUrl',
 'photos/4/thumbnailUrl',
 'photos/5/pictureUrl',
 'photos/5/thumbnailUrl',
 'photos/6/pictureUrl',
 'photos/6/thumbnailUrl',
 'photos/7/pictureUrl',
 'photos/7/thumbnailUrl',
 'photos/8/pictureUrl',
 'photos/8/thumbnailUrl',
 'photos/9/pictureUrl',
 'photos/9/thumbnailUrl',
 'photos/10/pictureUrl',
 'photos/10/thumbnailUrl',
 'photos/11/pictureUrl',
 'photos/11/thumbnailUrl',
 'photos/12/pictureUrl',
 'photos/12/thumbnailUrl',
 'photos/13/pictureUrl',
 'photos/13/thumbnailUrl',
 'photos/14/pictureUrl',
 'photos/14/thumbnailUrl',
 'photos/15/pictureUrl',
 'photos/15/thumbnailUrl',
 'photos/16/pictureUrl',
 'photos/16/thumbnailUrl',
 'photos/17/pictureUrl',
 'photos/17/thumbnailUrl',
 'photos/18/pictureUrl',
 'photos/18/thumbnailUrl',
 'photos/19/pictureUrl',
 'photos/19/thumbnailUrl',
 'photos/20/pictureUrl',
 'photos/20/thumbnailUrl',
 'photos/21/pictureUrl',
 'photos/21/thumbnailUrl',
 'photos/22/pictureUrl',
 'photos/22/thumbnailUrl',
 'photos/23/pictureUrl',
 'photos/23/thumbnailUrl',
 'photos/24/pictureUrl',
 'photos/24/thumbnailUrl',
 'photos/25/pictureUrl',
 'photos/25/thumbnailUrl',
 'photos/26/pictureUrl',
 'photos/26/thumbnailUrl',
 'photos/27/pictureUrl',
 'photos/27/thumbnailUrl',
 'photos/28/pictureUrl',
 'photos/28/thumbnailUrl',
 'photos/29/pictureUrl',
 'photos/29/thumbnailUrl',
 'photos/30/pictureUrl',
 'photos/30/thumbnailUrl',
 'pricing/rate/amount',
 'reviewDetailsInterface/reviewCount',
 'Accuracy',
 'Communication',
 'Cleanliness',
 'Location',
 'Check-in',
 'Value',
 'reviewsModule/localizedOverallRating',
 'stars',
 'roomType',
 'roomTypeCategory',
 'sectionedDescription/description',
 'sectionedDescription/houseRules',
 'sectionedDescription/interaction',
 'sectionedDescription/locale',
 'sectionedDescription/localizedLanguageName',
 'sectionedDescription/name',
 'sectionedDescription/neighborhoodOverview',
 'sectionedDescription/notes',
 'sectionedDescription/space',
 'sectionedDescription/summary',
 'sectionedDescription/transit',
 'url'
 ]

EASY_NAME_MAP = {
    # Already defined mappings
    'amenity_Kitchen': 'Kitchen',
    'amenity_Elevator': 'Elevator',
    'amenity_Wifi': 'Wifi',
    'amenity_Heating': 'Heating',
    'amenity_Iron': 'Iron',
    'amenity_Cable TV': 'Cable TV',
    'amenity_Gym': 'Gym',
    'amenity_Hair dryer': 'Hair Dryer',
    'amenity_Dryer': 'Dryer',
    'amenity_Hangers': 'Hangers',
    'amenity_Washer': 'Washer',
    'amenity_Essentials': 'Essentials',
    'amenity_Shampoo': 'Shampoo',
    'amenity_Pool': 'Pool',
    'amenity_Air conditioning': 'Air Conditioning',
    'amenity_TV': 'TV',
    'amenity_Smoke alarm': 'Smoke Alarm',
    'amenity_Carbon monoxide alarm': 'Carbon Monoxide Alarm',
    'amenity_Fire extinguisher': 'Fire Extinguisher',
    'amenity_Coffee maker': 'Coffee Maker',
    'amenity_Refrigerator': 'Refrigerator',
    'amenity_Dishwasher': 'Dishwasher',
    'amenity_Dishes and silverware': 'Dishes and Silverware',
    'amenity_Oven': 'Oven',
    'amenity_Stove': 'Stove',
    'amenity_BBQ grill': 'BBQ Grill',
    'amenity_Patio or balcony': 'Patio or Balcony',
    'amenity_Backyard': 'Backyard',
    'amenity_Cleaning available during stay': 'Cleaning Service Available',
    'amenity_Host greets you': 'Host Greeting',
    'amenity_Waterfront': 'Waterfront',
    'amenity_Safe': 'Safe',
    'amenity_Board games': 'Board Games',
    'amenity_Hot water kettle': 'Hot Water Kettle',
    'amenity_Sound system': 'Sound System',
    'amenity_Outdoor shower': 'Outdoor Shower',
    'amenity_Hot water': 'Hot Water',
    'amenity_Outdoor_dining_area': 'Outdoor Dining Area',
    'amenity_Dining_table': 'Dining Table',
    'amenity_Outdoor_furniture': 'Outdoor Furniture',
    'amenity_Freezer': 'Freezer',
    'pricing/rate/amount': 'Price',
    # Continuation of new mappings
    'bathroom_count': 'Bathroom Count',
    'bed_count': 'Bed Count',
    'bedroom_count': 'Bedroom Count',
    'guestControls/allowsChildren': 'Allows Children',
    'guestControls/allowsEvents': 'Allows Events',
    'guestControls/allowsInfants': 'Allows Infants',
    'guestControls/allowsPets': 'Allows Pets',
    'guestControls/allowsSmoking': 'Allows Smoking',
    'guestControls/personCapacity': 'Person Capacity',
    'guestControls/structuredHouseRules/0': 'House Rule 1',
    'guestControls/structuredHouseRules/1': 'House Rule 2',
    'guestControls/structuredHouseRules/2': 'House Rule 3',
    'reviewDetailsInterface/reviewCount': 'Total Reviews',
    'reviewsModule/localizedOverallRating': 'Overall Rating',
    'sectionedDescription/description': 'Description',
    'sectionedDescription/houseRules': 'House Rules',
    'sectionedDescription/interaction': 'Host Interaction',
    'sectionedDescription/locale': 'Locale',
    'sectionedDescription/localizedLanguageName': 'Language',
    'sectionedDescription/name': 'Property Name',
    'sectionedDescription/neighborhoodOverview': 'Neighborhood Overview',
    'sectionedDescription/notes': 'Additional Notes',
    'sectionedDescription/space': 'Space Description',
    'sectionedDescription/summary': 'Summary',
    'sectionedDescription/transit': 'Local Transit Info',
    # Simple renaming
    'city': 'City',
    'country': 'Country',
    'maxNights': 'Maximum Nights',
    'minNights': 'Minimum Nights',
    'numberOfGuests': 'Guest Capacity',
    'roomType': 'Room Type',
    'roomTypeCategory': 'Room Category',
    'url': 'Listing URL'
    # Further additions can be added here as needed
}
