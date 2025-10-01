from django.shortcuts import render, get_object_or_404
import urllib.request 
import json 
from urllib.error import HTTPError, URLError 
import random
def index(request):
    # La lógica general de manejo de errores permanecerá aquí, pero se refinará
    
    if request.method == 'POST':
        pokemon = request.POST.get('pokemon', '').lower().strip()
        
        # Si el campo está vacío, renderiza la página sin error.
        accion = request.POST.get('accion', '')
        if accion == "aleio":
            pokemon = str(random.randint(1, 1025))
        
        if not pokemon:
            return render(request, 'main.html', {})
            
        pokemon_url_name = pokemon.replace(' ', '%20') # URL encode el espacio

        try:
            # 1. SOLICITUD PRINCIPAL DE DATOS (POKÉMON)
            url_pokeapi = urllib.request.Request(f"https://pokeapi.co/api/v2/pokemon/{pokemon_url_name}")
            url_pokeapi.add_header('User-Agent', "CustomDjangoApp") # Mejorar el User-Agent
            
            with urllib.request.urlopen(url_pokeapi) as response:
                source = response.read()
                list_of_data = json.loads(source)
            
            # -----------------------------------------------------------------
            # SOLUCIÓN CLAVE: Usar .get() para evitar KeyError y manejar 'height'
            # -----------------------------------------------------------------
            
            # Obtiene 'height' y 'weight' de forma segura. Si no existen, devuelve 0.
            # Convertimos a float, usando .get() y un valor por defecto seguro (0)
            height_raw = float(list_of_data.get('height', 0)) 
            weight_raw = float(list_of_data.get('weight', 0))

            height_obtained = height_raw * 0.1
            weight_obtained = weight_raw * 0.1

            # El resto de las extracciones también deben ser seguras usando .get()
            types = ', '.join([t['type']['name'].capitalize() for t in list_of_data.get('types', [])])
            abilities = ', '.join([a['ability']['name'].replace('-', ' ').capitalize() for a in list_of_data.get('abilities', [])])
            # Acceso seguro a moves con .get() y slice [:5]
            moves = ', '.join([m['move']['name'].replace('-', ' ').capitalize() for m in list_of_data.get('moves', [])[:5]]) 
            stats = ', '.join([f"{s['stat']['name'].capitalize()}: {s['base_stat']}" for s in list_of_data.get('stats', [])])

            # 2. SOLICITUD DE DATOS DE ESPECIE
            url_species = urllib.request.Request(f'https://pokeapi.co/api/v2/pokemon-species/{pokemon_url_name}')
            url_species.add_header('User-Agent', "CustomDjangoApp") 
            
            with urllib.request.urlopen(url_species) as response_species:
                source_species = response_species.read()
                species_data = json.loads(source_species)

                # Acceso seguro a flavor_text_entries
                flavor_text_entries = species_data.get('flavor_text_entries', [])

                flavor_text = next(
                    (entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                     for entry in flavor_text_entries
                     if entry.get('language', {}).get('name') == 'es'),
                    "Descripción no disponible."
                )

            # 3. CONTEXTO Y RENDERIZADO
            # Acceso seguro a campos anidados (como la imagen) usando .get() en cadena
            imagen_url = list_of_data.get('sprites', {}).get('other', {}).get('official-artwork', {}).get('front_default')

            data = {
                # Usamos .get() por seguridad, aunque 'id' y 'name' deberían existir aquí
                "id": str(list_of_data.get('id', 'N/A')), 
                "nombre": str(list_of_data.get('name', 'Pokémon Desconocido')).capitalize(),
                "altura": f"{round(height_obtained, 2)} m" if height_obtained > 0 else "N/A",
                "peso": f"{round(weight_obtained, 2)} kg" if weight_obtained > 0 else "N/A",
                "imagen": imagen_url,
                "tipos": types,
                "habilidades": abilities,
                "estadisticas": stats,
                "movimientos": moves,
                "descripcion": flavor_text,
            }

            return render(request, 'main.html', data)

        # 4. MANEJO DE EXCEPCIONES ESPECÍFICAS
        except HTTPError as e:
            # Error 404: Pokémon no encontrado
            if e.code == 404:
                return render(request, "main.html", {"error": f"El Pokémon '{pokemon.capitalize()}' no fue encontrado."})
            # Otros errores HTTP
            else:
                return render(request, "main.html", {"error": f"Error al consultar la API: Código {e.code}"})
        
        except URLError as e:
            # Error de red/conexión (no hay internet, DNS falló, etc.)
            return render(request, "main.html", {"error": f"Error de conexión: Verifica tu conexión a internet o la URL de la API."})

        except Exception as e:
            # Captura otros errores (JSON malformado, etc.)
            return render(request, "main.html", {"error": f"Ocurrió un error inesperado: {str(e)}"})

    # Si el método no es POST, solo renderiza la página vacía
    else:
        return render(request, 'main.html', {})