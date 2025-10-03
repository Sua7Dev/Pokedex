from django.shortcuts import render
import urllib.request
import json
from urllib.error import HTTPError, URLError
import random


def index(request):
    tipos_disponibles = []
    try:
        url_types = urllib.request.Request("https://pokeapi.co/api/v2/type")
        url_types.add_header('User-Agent', "CustomDjangoApp")
        with urllib.request.urlopen(url_types) as response:
            data_types = json.loads(response.read())
            tipos_disponibles = [t["name"].capitalize() for t in data_types.get("results", [])]
    except:
        tipos_disponibles = []

    if request.method == 'POST':
        pokemon = request.POST.get('pokemon', '').lower().strip()
        accion = request.POST.get('accion', '')
        if accion == "aleio":
            pokemon = str(random.randint(1, 1025))

        filtro_tipo = request.POST.get('tipo', '').lower().strip()
        filtro_altura = request.POST.get('altura', '').strip()
        filtro_peso = request.POST.get('peso', '').strip()

        if not pokemon:
            return render(request, 'main.html', {"tipos_disponibles": tipos_disponibles})

        pokemon_url_name = pokemon.replace(' ', '%20')

        try:
            url_pokeapi = urllib.request.Request(f"https://pokeapi.co/api/v2/pokemon/{pokemon_url_name}")
            url_pokeapi.add_header('User-Agent', "CustomDjangoApp")

            with urllib.request.urlopen(url_pokeapi) as response:
                source = response.read()
                list_of_data = json.loads(source)

            height_raw = float(list_of_data.get('height', 0))
            weight_raw = float(list_of_data.get('weight', 0))

            height_obtained = height_raw * 0.1
            weight_obtained = weight_raw * 0.1

            types = [t['type']['name'] for t in list_of_data.get('types', [])]
            abilities = ', '.join([a['ability']['name'].replace('-', ' ').capitalize() for a in list_of_data.get('abilities', [])])
            moves = ', '.join([m['move']['name'].replace('-', ' ').capitalize() for m in list_of_data.get('moves', [])[:5]])
            stats = ', '.join([f"{s['stat']['name'].capitalize()}: {s['base_stat']}" for s in list_of_data.get('stats', [])])

            url_species = urllib.request.Request(f'https://pokeapi.co/api/v2/pokemon-species/{pokemon_url_name}')
            url_species.add_header('User-Agent', "CustomDjangoApp")

            with urllib.request.urlopen(url_species) as response_species:
                source_species = response_species.read()
                species_data = json.loads(source_species)

                flavor_text_entries = species_data.get('flavor_text_entries', [])

                flavor_text = next(
                    (entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                     for entry in flavor_text_entries
                     if entry.get('language', {}).get('name') == 'es'),
                    "Descripción no disponible."
                )

            imagen_url = list_of_data.get('sprites', {}).get('other', {}).get('official-artwork', {}).get('front_default')

            data = {
                "id": str(list_of_data.get('id', 'N/A')),
                "nombre": str(list_of_data.get('name', 'Pokémon Desconocido')).capitalize(),
                "altura": f"{round(height_obtained, 2)} m" if height_obtained > 0 else "N/A",
                "peso": f"{round(weight_obtained, 2)} kg" if weight_obtained > 0 else "N/A",
                "imagen": imagen_url,
                "tipos": ', '.join([t.capitalize() for t in types]),
                "habilidades": abilities,
                "estadisticas": stats,
                "movimientos": moves,
                "descripcion": flavor_text,
                "tipos_disponibles": tipos_disponibles
            }

            if filtro_tipo and filtro_tipo not in types:
                return render(request, "main.html", {"error": f"No coincide con el tipo {filtro_tipo.capitalize()}", "tipos_disponibles": tipos_disponibles})

            if filtro_altura and height_raw != float(filtro_altura):
                return render(request, "main.html", {"error": f"No coincide con la altura {filtro_altura}", "tipos_disponibles": tipos_disponibles})

            if filtro_peso and weight_raw != float(filtro_peso):
                return render(request, "main.html", {"error": f"No coincide con el peso {filtro_peso}", "tipos_disponibles": tipos_disponibles})

            return render(request, 'main.html', data)

        except HTTPError as e:
            if e.code == 404:
                return render(request, "main.html", {"error": f"El Pokémon '{pokemon.capitalize()}' no fue encontrado.", "tipos_disponibles": tipos_disponibles})
            else:
                return render(request, "main.html", {"error": f"Error al consultar la API: Código {e.code}", "tipos_disponibles": tipos_disponibles})

        except URLError as e:
            return render(request, "main.html", {"error": "Error de conexión con la API.", "tipos_disponibles": tipos_disponibles})

        except Exception as e:
            return render(request, "main.html", {"error": f"Ocurrió un error inesperado: {str(e)}", "tipos_disponibles": tipos_disponibles})

    else:
        return render(request, 'main.html', {"tipos_disponibles": tipos_disponibles})
