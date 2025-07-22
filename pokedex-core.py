import requests
import ipywidgets as widgets
from IPython.display import display, clear_output, Image

#Output widget API results
output = widgets.Output()


def fetch_pokemon_data(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    response = requests.get(url)

    with output:
      clear_output()
      if response.status_code == 200:
        data = response.json()
        image_url = data['sprites']["front_default"]
        name = data['name']
        height = data['height']
        weight = data['weight']
        abilities = [a['ability']['name'] for a in data['abilities']]
        result = f"Name: {name}\nHeight: {height}\nWeight: {weight}\nAbilities: {', '.join(abilities)}"
      else:
        result = f"Could not find Pokémon: {pokemon_name}"
      print(result)
      if image_url:
        display(Image(url=image_url))
      else:
        print("No image available for this pokemon.")



# Create widgets
pokemon_input = widgets.Text(
    value='pikachu',
    placeholder='Enter Pokémon name',
    description='Pokémon:',
    disabled=False
)

search_button = widgets.Button(
    description='Search',
    button_style='success'
)

clear_output_button = widgets.Button(
    description='Clear',
    button_style='info'
)



# Event handlers
def on_button_click(b):
    fetch_pokemon_data(pokemon_input.value)
def on_clear_click_2(b):
    with output:
      clear_output()
def on_enter_pressed(change):
  fetch_pokemon_data(change.value)

#Bind events
search_button.on_click(on_button_click)    
clear_output_button.on_click(on_clear_click_2)
pokemon_input.on_submit(on_enter_pressed)

# Display the UI
display(pokemon_input, search_button, output, clear_output_button)
