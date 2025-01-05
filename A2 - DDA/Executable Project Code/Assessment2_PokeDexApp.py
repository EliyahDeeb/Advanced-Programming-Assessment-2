import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
from PIL import Image, ImageTk
from io import BytesIO
import numpy as np

# Define colors for each type
type_colors = {
    "fire": "#F08030", "water": "#6890F0", "grass": "#78C850", "poison": "#A040A0",
    "electric": "#F8D030", "bug": "#A8B820", "normal": "#A8A878", "fairy": "#EE99AC",
    "flying": "#A890F0", "psychic": "#F85888", "ground": "#E0C068", "rock": "#B8A038",
    "ghost": "#705898", "ice": "#98D8D8", "dragon": "#7038F8", "dark": "#705848", "steel": "#B8B8D0", "fighting": "#C03028",
}

# Function to generate gradient
def generate_gradient(colors):
    gradient_size = 1450
    height = 925
    gradient = np.zeros((height, gradient_size, 3), dtype=np.uint8)
    
    if len(colors) == 1:
        color = [int(colors[0][j:j+2], 16) for j in (1, 3, 5)]
        # Set the second color to white if there's only one type
        second_color = [255, 255, 255]  # White color
        for x in range(gradient_size):
            r = int(color[0] * (1 - x / gradient_size) + second_color[0] * (x / gradient_size))
            g = int(color[1] * (1 - x / gradient_size) + second_color[1] * (x / gradient_size))
            b = int(color[2] * (1 - x / gradient_size) + second_color[2] * (x / gradient_size))
            gradient[:, x] = [r, g, b]
    else:
        for i in range(len(colors) - 1):
            start_color = [int(colors[i][j:j+2], 16) for j in (1, 3, 5)]
            end_color = [int(colors[i + 1][j:j+2], 16) for j in (1, 3, 5)]
            for x in range(gradient_size):
                ratio = x / gradient_size
                r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
                g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
                b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
                gradient[:, x] = [r, g, b]
    
    gradient_img = Image.fromarray(gradient)
    return ImageTk.PhotoImage(gradient_img)


# Function to fetch Pokémon data
def fetch_pokemon_data():
    pokemon_name = entry.get().lower().strip()

    if pokemon_name == "":
        messagebox.showwarning("Input Error", "Please enter a Pokémon name or ID.")
        return
    
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        data = response.json()

        # Extract relevant data from the response
        name = data['name'].capitalize()
        pokemon_id = data['id']  # Pokémon ID
        types = [t['type']['name'].capitalize() for t in data['types']]  # Capitalize the type names
        height = data['height'] / 10  # Height in meters
        weight = data['weight'] / 10  # Weight in kilograms
        
        # Pokémon stats (HP, Attack, Defense, etc.)
        stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
        
        # Pokémon abilities
        abilities = [ability['ability']['name'].capitalize() for ability in data['abilities']]
        
        # Pokémon image (sprite)
        sprite_url = data['sprites']['front_default']
        sprite_response = requests.get(sprite_url)
        sprite_image = Image.open(BytesIO(sprite_response.content))
        sprite_image = sprite_image.resize((150, 150))
        sprite = ImageTk.PhotoImage(sprite_image)

        # Update the labels with the Pokémon data
        id_label.config(text=f"ID: {pokemon_id}", font=("Pixelify Sans", 14), bg=None)
        name_label.config(text=f"Name: {name}", font=("Pixelify Sans", 14), bg=None)
        types_label.config(text=f"Types: {', '.join(types)}", font=("Pixelify Sans", 12), bg=None)
        height_label.config(text=f"Height: {height} m", font=("Pixelify Sans", 12), bg=None)
        weight_label.config(text=f"Weight: {weight} kg", font=("Pixelify Sans", 12), bg=None)
        
        # Update abilities
        abilities_label.config(text=f"Abilities: {', '.join(abilities)}", font=("Pixelify Sans", 12), bg=None)
        
        # Update sprite image
        sprite_label.config(image=sprite)
        sprite_label.image = sprite  # Keep a reference to avoid garbage collection

        # Update background with a gradient of the Pokémon's types
        colors = [type_colors[t.lower()] for t in types]
        gradient_image = generate_gradient(colors)
        window.config(bg="white")  # Set a neutral background color first
        background_label.config(image=gradient_image)
        background_label.image = gradient_image  # Keep a reference to avoid garbage collection

        # Update the progress bars for stats
        update_stat_bars(stats)

        # Fetch and update evolution chain
        fetch_evolution_chain(data['species']['url'])

    except requests.exceptions.HTTPError:
        messagebox.showerror("Error", f"Pokémon {pokemon_name} not found.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Request Error", f"Error fetching data: {e}")

# Function to update the progress bars with stats
def update_stat_bars(stats):
    hp_bar['value'] = stats.get('hp', 0)
    attack_bar['value'] = stats.get('attack', 0)
    defense_bar['value'] = stats.get('defense', 0)
    speed_bar['value'] = stats.get('speed', 0)

    # Change the color of stat text to black
    hp_stat.config(text=f"HP: {stats.get('hp', '-')}", fg="black", bg=None)  
    attack_stat.config(text=f"Attack: {stats.get('attack', '-')}", fg="black", bg=None) 
    defense_stat.config(text=f"Defense: {stats.get('defense', '-')}", fg="black", bg=None) 
    speed_stat.config(text=f"Speed: {stats.get('speed', '-')}", fg="black", bg=None)

# Function to fetch and display the evolution chain
def fetch_evolution_chain(species_url):
    try:
        species_response = requests.get(species_url)
        species_data = species_response.json()

        # Get the evolution chain URL from species data
        evolution_url = species_data['evolution_chain']['url']
        evolution_response = requests.get(evolution_url)
        evolution_data = evolution_response.json()

        # Extract the evolutionary stages
        evolution_chain = []
        chain = evolution_data['chain']

        # Function to traverse the evolution chain recursively
        def traverse_chain(chain, current_chain=[]):
            # Add current species to the evolution chain
            current_chain.append(chain['species']['name'].capitalize())
            
            if 'evolves_to' in chain and chain['evolves_to']:
                # If there are multiple evolutions, we process each separately
                for next_chain in chain['evolves_to']:
                    traverse_chain(next_chain, current_chain[:])  # Pass a copy of the current chain
            else:
                # When there's no further evolution, we append this path to the final evolution chain
                evolution_chain.append(' --> '.join(current_chain))

        traverse_chain(chain)

        # Display the evolution chain as a comma-separated list
        if evolution_chain:
            evolution_label.config(text=f"Evolution: {' // '.join(evolution_chain)}", font=("Pixelify Sans", 12), bg=None)
        else:
            evolution_label.config(text="Evolution: No evolution found.", font=("Pixelify Sans", 12), bg=None)

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Evolution Error", f"Error fetching evolution data: {e}")

# Creating the main window
window = tk.Tk()
window.title("Eli's Pokedex")
window.geometry("1450x925")
window.resizable(False, False)

# Background label for gradient
background_label = tk.Label(window)
background_label.place(relwidth=1, relheight=1)

# Frame for the search section
search_frame = tk.Frame(window, bd=2, relief="solid", padx=10, pady=10)  # Added border
search_frame.pack(pady=10)

# Search input and button
label = tk.Label(search_frame, text="Enter Pokémon name or ID:", font=("Pixelify Sans", 12))
label.grid(row=0, column=0, padx=10, pady=5)

entry = tk.Entry(search_frame, font=("Pixelify Sans", 12), width=20)
entry.grid(row=0, column=1, padx=10, pady=5)

search_button = tk.Button(search_frame, text="Search", command=fetch_pokemon_data, font=("Pixelify Sans", 12))
search_button.grid(row=0, column=2, padx=10, pady=5)

# Frame for Pokémon image
sprite_frame = tk.Frame(window, bd=2, relief="solid", padx=10, pady=10)  # Added border
sprite_frame.pack(pady=20)

sprite_label = tk.Label(sprite_frame)
sprite_label.grid(row=0, column=0, padx=10, pady=10)

# Frame for Pokémon basic info
info_frame = tk.Frame(window, bd=2, relief="solid", padx=10, pady=10)  # Added border
info_frame.pack(pady=10)

# ID label (added)
id_label = tk.Label(info_frame, text="ID: -", font=("Pixelify Sans", 14), bg=None)
id_label.grid(row=0, column=0, padx=10, pady=5)

name_label = tk.Label(info_frame, text="Name: -", font=("Pixelify Sans", 14), bg=None)
name_label.grid(row=1, column=0, padx=10, pady=5)

types_label = tk.Label(info_frame, text="Types: -", font=("Pixelify Sans", 12), bg=None)
types_label.grid(row=2, column=0, padx=10, pady=5)

height_label = tk.Label(info_frame, text="Height: -", font=("Pixelify Sans", 12), bg=None)
height_label.grid(row=3, column=0, padx=10, pady=5)

weight_label = tk.Label(info_frame, text="Weight: -", font=("Pixelify Sans", 12), bg=None)
weight_label.grid(row=4, column=0, padx=10, pady=5)

# Frame for Pokémon stats
stats_frame = tk.Frame(window, bd=2, relief="solid", padx=10, pady=10)  # Added border
stats_frame.pack(pady=10)

# Create progress bars for stats
hp_bar = ttk.Progressbar(stats_frame, maximum=255, length=300)
hp_bar.grid(row=0, column=1, padx=10, pady=5)

attack_bar = ttk.Progressbar(stats_frame, maximum=255, length=300)
attack_bar.grid(row=1, column=1, padx=10, pady=5)

defense_bar = ttk.Progressbar(stats_frame, maximum=255, length=300)
defense_bar.grid(row=2, column=1, padx=10, pady=5)

speed_bar = ttk.Progressbar(stats_frame, maximum=255, length=300)
speed_bar.grid(row=3, column=1, padx=10, pady=5)

# Labels for stats text
hp_stat = tk.Label(stats_frame, text="HP: -", font=("Pixelify Sans", 12), bg=None)
hp_stat.grid(row=0, column=0, padx=10, pady=5)

attack_stat = tk.Label(stats_frame, text="Attack: -", font=("Pixelify Sans", 12), bg=None)
attack_stat.grid(row=1, column=0, padx=10, pady=5)

defense_stat = tk.Label(stats_frame, text="Defense: -", font=("Pixelify Sans", 12), bg=None)
defense_stat.grid(row=2, column=0, padx=10, pady=5)

speed_stat = tk.Label(stats_frame, text="Speed: -", font=("Pixelify Sans", 12), bg=None)
speed_stat.grid(row=3, column=0, padx=10, pady=5)

# Frame for Pokémon abilities
abilities_frame = tk.Frame(window, bd=2, relief="solid", padx=10, pady=10)  # Added border
abilities_frame.pack(pady=10)

abilities_label = tk.Label(abilities_frame, text="Abilities: -", font=("Pixelify Sans", 12), bg=None)
abilities_label.pack(pady=5)

# Frame for evolution chain
evolution_frame = tk.Frame(window, bd=2, relief="solid", padx=10, pady=10)  # Added border
evolution_frame.pack(pady=10)

evolution_label = tk.Label(evolution_frame, text="Evolution: -", font=("Pixelify Sans", 12), bg=None)
evolution_label.pack(pady=5)

# Run the GUI loop
window.mainloop()
