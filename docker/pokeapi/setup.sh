#!/bin/sh
set -eu

python manage.py migrate --settings=config.docker-compose

python manage.py shell --settings=config.docker-compose -c "
from data.v2.build import build_all
from pokemon_v2.models import Pokemon, PokemonCries

pokemon_count = Pokemon.objects.count()
cries_count = PokemonCries.objects.count()
print(f'Pokemon count before setup: {pokemon_count}')
print(f'Pokemon cries count before setup: {cries_count}')
if pokemon_count == 0 or cries_count == 0:
    print('PokeAPI data missing or partial; running build_all()')
    build_all()
else:
    print('PokeAPI data already loaded; skipping build_all()')
"
