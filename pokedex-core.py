import requests
import ipywidgets as widgets
from IPython.display import display, clear_output

# caching
pokemon_data_cache = {}
image_url_cache = {}
type_list_cache = {}
evolution_chain_cache = {}

# Header image
header_image_url = "https://assets.stickpng.com/images/612ce4761b9679000402af1c.png"

try:
    response = requests.get(header_image_url)
    if response.status_code == 200:
        header_image_data = response.content
        header = widgets.Image(
            value=header_image_data,
            format='png',
            layout=widgets.Layout(height='281.25px', width='500px')
        )
    else:
        header = widgets.Label("⚠️ Could not load header image.")
except:
    header = widgets.Label("⚠️ Image error.")


# Fetch data

def fetch_pokemon_data(pokemon_name):
    name_key = pokemon_name.lower()

    loading_spinner.value = "🔄 Loading..."
    with output:
        clear_output()

        if name_key in pokemon_data_cache:
            data = pokemon_data_cache[name_key]
        else:
            url = f"https://pokeapi.co/api/v2/pokemon/{name_key}"
            response = requests.get(url)
            if response.status_code != 200:
                print(f"❌ Could not find Pokémon: {pokemon_name}")
                loading_spinner.value = ""
                return
            data = response.json()
            pokemon_data_cache[name_key] = data

        # Extract info
        name = data['name'].capitalize()
        height = data['height']
        weight = data['weight']
        abilities = ', '.join([a['ability']['name'] for a in data['abilities']])
        result = f"Name: {name}\nHeight: {height}\nWeight: {weight}\nAbilities: {abilities}"
        print(result)

        fetch_evolution_chain_images(name_key)

    loading_spinner.value = ""


def get_pokemon_image_url(pokemon_name):
    name_key = pokemon_name.lower()
    if name_key in image_url_cache:
        return image_url_cache[name_key]

    url = f"https://pokeapi.co/api/v2/pokemon/{name_key}"
    response = requests.get(url)
    if response.status_code == 200:
        img_url = response.json()['sprites']['front_default']
        image_url_cache[name_key] = img_url
        return img_url
    return None


def fetch_evolution_chain_images(pokemon_name):
    name_key = pokemon_name.lower()

    if name_key in evolution_chain_cache:
        evolution_names = evolution_chain_cache[name_key]
    else:
        # Fetch species and evolution chain as before
        species_url = f"https://pokeapi.co/api/v2/pokemon-species/{name_key}"
        species_response = requests.get(species_url)
        if species_response.status_code != 200:
            print(f"❌ Could not find species data for: {pokemon_name}")
            return

        species_data = species_response.json()
        evolution_chain_url = species_data['evolution_chain']['url']

        evolution_response = requests.get(evolution_chain_url)
        if evolution_response.status_code != 200:
            print("❌ Could not retrieve evolution chain.")
            return

        chain = evolution_response.json()['chain']
        evolution_names = extract_full_evolution_chain(chain)
        # Cache under all species names in the chain
        for name in evolution_names:
            evolution_chain_cache[name.lower()] = evolution_names

    display_full_evolution_images(evolution_names, current=name_key)


def extract_full_evolution_chain(chain_node):
    """
    Recursively extract a flat list of Pokémon names in a single evolution path.
    Assumes a linear chain (no branches) — picks the first evolve_to path.
    """
    chain = [chain_node['species']['name']]
    evolves_to = chain_node.get('evolves_to')

    while evolves_to:
        next_node = evolves_to[0]
        chain.append(next_node['species']['name'])
        evolves_to = next_node.get('evolves_to')

    return chain


# UI elements
pokemon_input = widgets.Text(
    value='pikachu',
    placeholder='Enter Pokémon name',
    description='',
    disabled=False,
    layout=widgets.Layout(width='200px')
)

search_button = widgets.Button(
    description='Search',
    button_style='success'
)

browse_button = widgets.Button(
    description='Browse by Type',
    button_style='warning'
)

clear_button = widgets.Button(
    description='Clear',
    button_style='info'
)

type_dropdown = widgets.Dropdown(
    options=[],
    description='',
    disabled=True,
    layout=widgets.Layout(width='200px')
)

loading_spinner = widgets.HTML(value="", layout=widgets.Layout(margin="0 0 10px 0"))


# Container to dynamically swap inputs
input_ui = widgets.HBox([pokemon_input, search_button, browse_button, clear_button])

# Output widget for displaying results
output = widgets.Output()

# Event Handlers
def on_search_click(_):
    if type_dropdown.disabled == False:
        switch_to_text_input_ui()
        return

    fetch_pokemon_data(pokemon_input.value)

def on_clear_click(_):
    with output:
        clear_output()

def on_enter_key(_):
    fetch_pokemon_data(pokemon_input.value)

def on_browse_click(_):
    url = "https://pokeapi.co/api/v2/type/"
    response = requests.get(url)
    if type_dropdown.disabled == False:
      if response.status_code == 200:
          types = response.json()['results']
          type_dropdown.options = [(t['name'].capitalize(), t['name']) for t in types if t['name'] not in ['unknown', 'shadow']]
          type_dropdown.disabled = False
          with output:
              clear_output()
              print("Select a type from the dropdown to browse Pokémon.")
      else:
          with output:
              clear_output()
              print("⚠️ Failed to fetch types.")
    else: switch_to_type_browse_ui()

#UI Switches
def switch_to_text_input_ui():
    type_dropdown.disabled = True
    type_dropdown.value = None
    pokemon_input.value = ''
    search_button.description = 'Search'
    input_ui.children = [pokemon_input, search_button, browse_button, clear_button]
    with output:
        clear_output()

def switch_to_type_browse_ui():
    # Fetch types and enable dropdown
    url = "https://pokeapi.co/api/v2/type/"
    response = requests.get(url)

    if response.status_code == 200:
        types = response.json()['results']
        type_dropdown.options = [(t['name'].capitalize(), t['name']) for t in types if t['name'] not in ['unknown', 'shadow']]
        type_dropdown.value = None
        type_dropdown.disabled = False

        search_button.description = 'Search by Name'
        input_ui.children = [type_dropdown, search_button, clear_button]

        with output:
            clear_output()
            print("🔍 Select a type to browse Pokémon.")
    else:
        with output:
            clear_output()
            print("⚠️ Failed to fetch types.")

# List view logic
def on_type_selected(change):
    if not change.new:
        return

    type_key = change.new.lower()
    loading_spinner.value = "🔄 Loading Pokémon..."

    output.clear_output(wait=True)

    with output:
        if type_key in type_list_cache:
            pokemon_list = type_list_cache[type_key]
        else:
            url = f"https://pokeapi.co/api/v2/type/{type_key}"
            response = requests.get(url)
            if response.status_code != 200:
                print("⚠️ Could not fetch Pokémon of that type.")
                loading_spinner.value = ""
                return
            data = response.json()
            pokemon_list = sorted(set(p['pokemon']['name'] for p in data['pokemon']))
            type_list_cache[type_key] = pokemon_list

        print(f"Found {len(pokemon_list)} Pokémon of type '{type_key.capitalize()}':")

        buttons = []
        for name in pokemon_list[:50]:
            btn = widgets.Button(description=name.capitalize())
            btn.layout.width = '100%'  # full width
            # Let height be default (no setting)
            buttons.append(btn)

            def make_on_click(poke_name):
                return lambda _: fetch_pokemon_data(poke_name)

            btn.on_click(make_on_click(name))

        list_box = widgets.VBox(buttons, layout=widgets.Layout(width='100%'))

        scrollable_container = widgets.Box(
            [list_box],
            layout=widgets.Layout(
                height='auto',          # fixed height container
                overflow_y='auto',       # vertical scrollbar when needed
                overflow_x='hidden',     # no horizontal scrollbar
                border='1px solid #ccc',
                padding='5px',
                width='450px',
                max_width='100%',
                flex_flow='column nowrap'  # prevent children from wrapping
            )
        )

        display(scrollable_container)

    loading_spinner.value = ""

# Display evolution chain images logic
def display_full_evolution_images(evolution_names, current=None):
    """Display all Pokémon in the evolution line, with the current one optionally emphasized."""
    def create_image_widget(name):
        url = get_pokemon_image_url(name)
        label = widgets.HTML(
            f"<b>{name.capitalize()}</b>" if name == current else name.capitalize()
        )

        if url:
            try:
                image_data = requests.get(url).content
                return widgets.VBox([
                    widgets.Image(value=image_data, format='png', width=100, height=100),
                    label
                ])
            except Exception:
                return widgets.VBox([label, widgets.Label("(Image error)")])
        return widgets.VBox([label, widgets.Label("(No image)")])

    image_widgets = [create_image_widget(name) for name in evolution_names]
    display(widgets.HBox(image_widgets), Layout=widgets.Layout(width='120px', padding='5px'))


# Bind Events
search_button.on_click(on_search_click)
browse_button.on_click(on_browse_click)
clear_button.on_click(on_clear_click)
pokemon_input.on_submit(on_enter_key)
type_dropdown.observe(on_type_selected, names='value')



# Display UI
display(widgets.VBox([header, input_ui, loading_spinner, output]))
