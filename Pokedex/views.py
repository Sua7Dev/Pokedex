from django.shortcuts import render
import urllib.request 
import json 
from urllib.error import HTTPError

def index(request):
    try:
        if request.method == 'POST':
            pokemon = request.POST['pokemon'].lower().strip()
            pokemon = pokemon.replace(' ', '%20')
            url_pokeapi = urllib.request.Request(f'https://pokeapi.co/api/v2/pokemon/{pokemon}')
            url_pokeapi.add_header('User-Agent', "pikachu")
            source = urllib.request.urlopen(url_pokeapi).read()
            list_of_data = json.loads(source)


            height_obtained = float(list_of_data['height']) * 0.1
            weight_obtained = float(list_of_data['weight']) * 0.1


            types = [t['type']['name'].capitalize() for t in list_of_data['types']]
            abilities = [a['ability']['name'].replace('-', ' ').capitalize() for a in list_of_data['abilities']]
            stats = {s['stat']['name'].capitalize(): s['base_stat'] for s in list_of_data['stats']}
            moves = [m['move']['name'].replace('-', ' ').capitalize() for m in list_of_data['moves'][:3]]
            url_species = urllib.request.Request(f'https://pokeapi.co/api/v2/pokemon-species/{pokemon}')
            url_species.add_header('User-Agent', "pikachu")
            source_species = urllib.request.urlopen(url_species).read()
            species_data = json.loads(source_species)
            flavor_text = next(
                (entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                 for entry in species_data['flavor_text_entries']
                 if entry['language']['name'] == 'es'),
                "Descripción no disponible."
            )
            data = {
                "id": str(list_of_data['id']),
                "nombre": str(list_of_data['name']).capitalize(),
                "altura": f"{round(height_obtained, 2)} m",
                "peso": f"{round(weight_obtained, 2)} kg",
                "imagen": list_of_data['sprites']['front_default'],
                "tipos": types,
                "habilidades": abilities,
                "estadisticas": stats,
                "movimientos": moves,
                "descripcion": flavor_text,
            }
            print(data)
            return render(request, 'main.html', data)
        else:
            return render(request, 'main.html', {})
    except HTTPError:
        return render(request, "main.html", {"error": "Pokémon no encontrado."})
    except Exception as e:
        return render(request, "main.html", {"error": f"Ocurrió un error: {str(e)}"})
