#https://gist.github.com/elktros/faa43bbf413d4414e2cbbea580143d05
import google.generativeai as genai
import os
import orjson
import pyrebase
import re

#configuring the firebase
config = {
  "apiKey": "kZty974kFM87dECEB8UP8Bkrg1hUj8DNU8bg6PLF",
  "authDomain": "ai-kitechen-default-rtdb.firebaseio.com",
  "databaseURL": "https://ai-kitechen-default-rtdb.firebaseio.com/",
  "storageBucket": "ai-kitechen-default-rtdb.appspot.com"
}

firebase = pyrebase.initialize_app(config)
# Get a reference to the database service
db = firebase.database()
print(db)
user_order = db.child("user_order").get().val()
print(user_order)

#shelfdatabase used to store the ingredients
shelfdatabase = {"weight" : {"tomato" : 2.0 ,
                             "potato" : 2.0,
                             "carrot" : 2.0 ,
                             "ladysfinger" : 5.0,
                             "raddish" : 2.0,
                             "cardomon_powder" : 0.5,
                             "chilli_powder" : 0.5,
                             "turmuric_powder" : 0.5,
                             "pepper_powder" : 0.5,
                             "garam_masala" :0.5,
                             "rice" : 5.0
                             },

                 "quantity" : { "egg" : 10 ,
                                "noodles" : 10
                              },
                 
                 "litres" : { "water" : 2.0,
                              "oil" : 1.0
                             },

                 
                 "vessel" : ["pan" , "cooker" , "pot" , "sausepan" ,"Stockpot"
                             ]
                     }
#function to extract the specific keys from shelfdatabase
def get_all_keys(data, main_keys):
    all_keys = []
    for main_key in main_keys:
        if main_key in data and isinstance(data[main_key], dict):
            all_keys.extend(data[main_key].keys())
    return all_keys

#function to create the prompt structure
def prompt(user_order,shelfdatabase):
    ingredient = get_all_keys(shelfdatabase, ['weight', 'quantity', 'litres'])
    ingredientStr = ' '.join([str(elem) for elem in ingredient])
    print(ingredientStr)
    return 'user order : ' + user_order + ' , the ingredient i have'+ ingredientStr + ' , give the receipe for the user order while considering the ingredient  with cooking steps as seperate keys and ingredients in a seperate keys and mention the time for each steps in a seperate keys at the end of eeach line in numbers without minutes , ' + 'if the ingredients is not in the ingredientStr give the ingredients which is not present and dont give response in bold just give the response in normal text' + 'label cooking step as steps' + 'highlight the process of cooking being done like boiling , frying , baking , roasting , grilling , steaming , sauteing , simmering , braising , poaching , stewing , blanching , broiling , deep frying , shallow frying , pressure cooking , slow cooking , smoking , marinating , pickling , curing , fermenting , drying , freezing , canning' + 'remove the ** for numbers'

#function to get the recipe from the generative model    
def get_recipe(query):
    genai.configure(api_key = 'AIzaSyCKzSRI2TScnw2WIeQJTky9i8E588CH6gk')
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(query)
    return response.text

#function to parse the response
def parse(response):
    cont = orjson.loads(response)
    return cont

def stringsplit(response):

# Extract ingredients
    ingredients_pattern = re.compile(r'\*\*Ingredients:\*\*\n\n((?:\* .+\n)+)')
    ingredients_match = ingredients_pattern.search(response)
    ingredients_list = []

    if ingredients_match:
        ingredients_section = ingredients_match.group(1).strip()
        ingredients_list = [line.strip('* ').split('(')[0].strip() for line in ingredients_section.split('\n')]

    # Extract steps, times, and actions
    steps_pattern = re.compile(r'\*\*Steps:\*\*\n\n((?:\d+\. .+\n)+)')
    steps_match = steps_pattern.search(response)
    steps_list = []
    times_list = []
    actions_list = []

    if steps_match:
        steps_section = steps_match.group(1).strip()
        steps_lines = [line.strip() for line in steps_section.split('\n')]
        for line in steps_lines:
            step_time_match = re.search(r'(\d+)$', line)
            time = step_time_match.group(1) if step_time_match else ""
       
            if time:
                line = line[:step_time_match.start()].strip()
                #print(line)    
            action_match = re.search(r'\*\*(.+?)\*\*', line)
            if action_match:
                action = action_match.group(1).strip()
                actions_list.append(action)

            steps_list.append(line)
            times_list.append(time)

# Output the results
    print("Ingredients:")
    for ingredient in ingredients_list:
        print(f"- {ingredient}")

    print("\nSteps:")
    for step in steps_list:
        print(f"- {step}")

    print("\nTimes:")
    for time in times_list:
        print(f"- {time}")

    print("\nActions:")
    for action in actions_list:
        print(f"- {action}")


#main code to get the recipe
Ai_query = prompt(user_order,shelfdatabase)
response = get_recipe(Ai_query)
print(stringsplit(response))