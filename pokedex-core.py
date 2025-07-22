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
        #Get image
        image_url = data['sprites']["front_default"]
        #Get general info
        name = data['name']
        height = data['height']
        weight = data['weight']
        abilities = [a['ability']['name'] for a in data['abilities']]
        result = f"Name: {name}\nHeight: {height}\nWeight: {weight}\nAbilities: {', '.join(abilities)}"
      else:
        result = f"Could not find Pokémon: {pokemon_name}"
      print(result)
      # if image_url:
      #   display(Image(url=image_url))
      # else:
      #   print("No image available for this pokemon.")
      fetch_evolution_chain_images(pokemon_name)


def get_pokemon_image_url(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['sprites']['front_default']
    return None

def fetch_evolution_chain_images(pokemon_name):
    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_name.lower()}"
    species_response = requests.get(species_url)

    if species_response.status_code != 200:
        print(f"Could not find species data for: {pokemon_name}")
        return

    species_data = species_response.json()
    evolution_chain_url = species_data['evolution_chain']['url']

    evolution_response = requests.get(evolution_chain_url)
    if evolution_response.status_code != 200:
        print("Could not retrieve evolution chain.")
        return

    evolution_data = evolution_response.json()
    chain = evolution_data['chain']

    # Flatten the evolution chain
    evolution_names = []
    while chain:
        evolution_names.append(chain['species']['name'])
        if chain['evolves_to']:
            chain = chain['evolves_to'][0]
        else:
            break

    # Find current Pokémon's position
    try:
        index = evolution_names.index(pokemon_name.lower())
    except ValueError:
        print("Pokémon not found in evolution chain.")
        return

    # Get previous and next evolution names
    previous = evolution_names[index - 1] if index > 0 else None
    next_ = evolution_names[index + 1] if index < len(evolution_names) - 1 else None

    # Display images
    from IPython.display import Image, display


    display_evolution_images(previous, pokemon_name, next_)


    # if previous:
    #     prev_img = get_pokemon_image_url(previous)
    #     print(f"Previous Evolution: {previous.capitalize()}")
    #     if prev_img:
    #         display(Image(url=prev_img))

    # if next_:
    #     next_img = get_pokemon_image_url(next_)
    #     print(f"Next Evolution: {next_.capitalize()}")
    #     if next_img:
    #         display(Image(url=next_img))

def display_evolution_images(previous=None, current=None, next_=None):
    images = []

    def create_image_widget(name):
        if name:
            url = get_pokemon_image_url(name)
            if url:
                return widgets.VBox([
                    widgets.Image(value=requests.get(url).content, format='png', width=100, height=100),
                    widgets.Label(name.capitalize())
                ])
        return widgets.VBox([widgets.Label("None")])

    images.append(create_image_widget(previous))
    images.append(create_image_widget(current))
    images.append(create_image_widget(next_))

    display(widgets.HBox(images))


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
