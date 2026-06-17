// Base URLs
const API_BASE_URL = 'http://127.0.0.1:8002/api';
const POKEAPI_BASE = 'https://pokeapi.co/api/v2';

// 10 Teams State
const teams = Array.from({ length: 10 }, (_, i) => ({
  name: `Time ${i + 1}`,
  slots: Array.from({ length: 6 }, () => ({
    name: "",
    id: null,
    level: 100,
    gender: "♂",
    item: "Nenhum",
    stats: { hp: 0, attack: 0, defense: 0, "special-attack": 0, "special-defense": 0, speed: 0 },
    types: [],
    moves: [],
    desc: "Vazio",
    isAce: false, // first Ace (red star)
    isSecondAce: false // second Ace (red heart)
  })),
  primaryStrategy: "balanced pressure",
  secondaryStrategy: "complementary coverage",
  aces: []
}));

let activeTeamIndex = 0;
let activeSlotIndex = 0; // index inside active team slots (0 to 5)

// List of all 1200 Pokemon
let pokemonList = [];

// DOM Elements
const teamNameInput = document.getElementById('team-name-input');
const btnTeamPrev = document.getElementById('btn-team-prev');
const btnTeamNext = document.getElementById('btn-team-next');
const btnDados = document.getElementById('btn-dados');
const btnEquipe = document.getElementById('btn-equipe');
const btnFechar = document.getElementById('btn-fechar');
const btnGerenciadorToggle = document.getElementById('btn-gerenciador-toggle');

// Left Profile Elements
const pkmnLevelInput = document.getElementById('pkmn-level');
const btnGenderM = document.getElementById('btn-gender-m');
const btnGenderF = document.getElementById('btn-gender-f');
const activePkmnImg = document.getElementById('active-pkmn-img');
const activePkmnName = document.getElementById('active-pkmn-name');
const activePkmnType = document.getElementById('active-pkmn-type');
const activePkmnItem = document.getElementById('active-pkmn-item');

// Moves buttons
const btnMoves = [
  document.getElementById('btn-move-1'),
  document.getElementById('btn-move-2'),
  document.getElementById('btn-move-3'),
  document.getElementById('btn-move-4')
];

// Stats elements
const statsBars = {
  hp: { fill: document.getElementById('bar-hp'), val: document.getElementById('val-hp') },
  atk: { fill: document.getElementById('bar-atk'), val: document.getElementById('val-atk') },
  def: { fill: document.getElementById('bar-def'), val: document.getElementById('val-def') },
  spa: { fill: document.getElementById('bar-spa'), val: document.getElementById('val-spa') },
  spd: { fill: document.getElementById('bar-spd'), val: document.getElementById('val-spd') },
  spe: { fill: document.getElementById('bar-spe'), val: document.getElementById('val-spe') }
};

// Box Slots Grid
const boxSlots = document.querySelectorAll('.box-slot');

// Pokedex
const pokedexDesc = document.getElementById('pokedex-desc');

// Gerenciador / Pokemon List Elements
const rightPanel = document.getElementById('right-panel');
const btnPokemonsList = document.getElementById('btn-pokemons-list');
const pokemonsDropdown = document.getElementById('pokemons-dropdown-box');
const pokemonSearchInput = document.getElementById('pokemon-search-input');
const pokemonsScrollGrid = document.getElementById('pokemons-scroll-grid');
const suggestionsListVertical = document.getElementById('suggestions-list-vertical');

// Team Builder settings panel (DADOS)
const generatorConfigBox = document.getElementById('generator-config-box');
const primaryStrategyInput = document.getElementById('primary-strategy');
const secondaryStrategyInput = document.getElementById('secondary-strategy');
const aceInputs = document.getElementById('ace-inputs');
const btnGenerateTeam = document.getElementById('btn-generate-team');
const btnBanPkmn = document.getElementById('btn-ban-pkmn');

// Retro Alert Modal
const retroAlert = document.getElementById('retro-alert');
const retroAlertTitle = document.getElementById('retro-alert-title');
const retroAlertMsg = document.getElementById('retro-alert-msg');
const btnRetroAlertOk = document.getElementById('btn-retro-alert-ok');

// Move Details Modal
const moveDetailsModal = document.getElementById('move-details-modal');
const moveModalTitle = document.getElementById('move-modal-title');
const moveDetailName = document.getElementById('move-detail-name');
const moveDetailCategory = document.getElementById('move-detail-category');
const moveDetailType = document.getElementById('move-detail-type');
const moveDetailPower = document.getElementById('move-detail-power');
const moveDetailAccuracy = document.getElementById('move-detail-accuracy');
const moveDetailPP = document.getElementById('move-detail-pp');
const moveDetailDesc = document.getElementById('move-detail-desc');
const btnMoveModalClose = document.getElementById('btn-move-modal-close');

// --- Helper: Retro Alert ---
function showRetroAlert(message, title = "ATENÇÃO") {
  retroAlertTitle.textContent = title;
  retroAlertMsg.textContent = message;
  retroAlert.style.display = 'flex';
}
btnRetroAlertOk.addEventListener('click', () => {
  retroAlert.style.display = 'none';
});

// --- Initialize Pokemon Database (1 to 1200) ---
async function loadPokemonDatabase() {
  try {
    const response = await fetch(`${POKEAPI_BASE}/pokemon?limit=1200`);
    if (response.ok) {
      const data = await response.json();
      pokemonList = data.results.map((item) => {
        // Extract ID from URL
        const parts = item.url.split('/').filter(Boolean);
        const id = parts[parts.length - 1];
        return {
          name: item.name,
          id: parseInt(id),
          sprite: `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${id}.png`,
          artwork: `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${id}.png`
        };
      });
      renderPokemonsGrid(pokemonList);
    } else {
      showRetroAlert("Erro ao carregar lista de Pokémon da API.");
    }
  } catch (error) {
    showRetroAlert("Falha ao se conectar à API externa para carregar banco de Pokémon.");
  }
}

// Render the grid list of 1200 Pokemon in Gerenciador
function renderPokemonsGrid(list) {
  pokemonsScrollGrid.innerHTML = '';
  list.forEach(pkmn => {
    const item = document.createElement('div');
    item.className = 'list-sprite-item';
    item.innerHTML = `
      <img src="${pkmn.sprite}" alt="${pkmn.name}" loading="lazy">
      <span class="list-name">${pkmn.name}</span>
    `;

    // Hover tooltip / status details
    let hoverTimeout;
    item.addEventListener('mouseenter', () => {
      hoverTimeout = setTimeout(async () => {
        const desc = await getPokemonDescription(pkmn.id);
        pokedexDesc.textContent = `[${pkmn.name.toUpperCase()}] - ${desc}`;
      }, 300);
    });

    item.addEventListener('mouseleave', () => {
      clearTimeout(hoverTimeout);
    });

    // Click selects the pokemon into the active slot
    item.addEventListener('click', () => {
      assignPokemonToActiveSlot(pkmn);
      pokemonsDropdown.style.display = 'none';
    });

    pokemonsScrollGrid.appendChild(item);
  });
}

// Search filter inside Pokemons list
pokemonSearchInput.addEventListener('input', (e) => {
  const query = e.target.value.toLowerCase().trim();
  const filtered = pokemonList.filter(p => p.name.includes(query));
  renderPokemonsGrid(filtered);
});

// --- Fetch Helpers ---
async function getPokemonDescription(nameOrId) {
  try {
    const response = await fetch(`${POKEAPI_BASE}/pokemon-species/${nameOrId}`);
    if (response.ok) {
      const data = await response.json();
      const ptEntry = data.flavor_text_entries.find(e => e.language.name === 'pt' || e.language.name === 'pt-BR');
      if (ptEntry) return ptEntry.flavor_text.replace(/[\f\n\r]/g, ' ');
      const enEntry = data.flavor_text_entries.find(e => e.language.name === 'en');
      if (enEntry) return enEntry.flavor_text.replace(/[\f\n\r]/g, ' ');
    }
  } catch (e) {
    console.error(e);
  }
  return "Descrição da Pokédex não disponível.";
}

// --- Team Management & Rendering ---
function renderActiveTeam() {
  const team = teams[activeTeamIndex];
  teamNameInput.value = team.name;

  // Sync builder settings UI
  primaryStrategyInput.value = team.primaryStrategy;
  secondaryStrategyInput.value = team.secondaryStrategy;
  aceInputs.value = team.aces.join(', ');

  // Render Box Slots
  boxSlots.forEach((slot, index) => {
    const pkmn = team.slots[index];
    const spriteHolder = slot.querySelector('.sprite-holder');
    const slotNameSpan = slot.querySelector('.slot-name');

    // Remove active style
    slot.classList.remove('active-slot');
    if (index === activeSlotIndex) {
      slot.classList.add('active-slot');
    }

    // Set badges
    const existingAce = slot.querySelector('.slot-badge-ace');
    if (existingAce) existingAce.remove();

    if (pkmn.name) {
      slotNameSpan.textContent = pkmn.name;
      const id = pkmn.id;
      spriteHolder.innerHTML = `<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${id}.png" alt="${pkmn.name}">`;
      slot.classList.remove('empty');

      // Aces badges (red star / heart)
      if (pkmn.isAce) {
        const star = document.createElement('span');
        star.className = 'slot-badge-ace star-red';
        star.innerHTML = '★';
        slot.appendChild(star);
      } else if (pkmn.isSecondAce) {
        const heart = document.createElement('span');
        heart.className = 'slot-badge-ace heart-red';
        heart.innerHTML = '♥';
        slot.appendChild(heart);
      }
    } else {
      slotNameSpan.textContent = "Vazio";
      spriteHolder.innerHTML = '';
      slot.classList.add('empty');
    }
  });

  // Render Left Profile for selected slot
  renderLeftProfile();
}

function renderLeftProfile() {
  const team = teams[activeTeamIndex];
  const pkmn = team.slots[activeSlotIndex];

  if (pkmn.name) {
    activePkmnName.textContent = pkmn.name;
    activePkmnType.textContent = pkmn.types.join(' / ') || '-';
    pkmnLevelInput.value = pkmn.level;
    activePkmnItem.value = pkmn.item;

    if (pkmn.gender === "♂") {
      btnGenderM.classList.add('active');
      btnGenderF.classList.remove('active');
    } else {
      btnGenderM.classList.remove('active');
      btnGenderF.classList.add('active');
    }

    activePkmnImg.src = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${pkmn.id}.png`;

    // Render Stats
    Object.keys(statsBars).forEach(stat => {
      const val = pkmn.stats[stat] || 0;
      const percent = Math.min(100, Math.round((val / 255) * 100));
      statsBars[stat].fill.style.width = `${percent}%`;
      statsBars[stat].val.textContent = val;
    });

    // Render Moves buttons
    btnMoves.forEach((btn, idx) => {
      const move = pkmn.moves[idx];
      if (move) {
        btn.textContent = move.name;
        btn.className = `move-btn type-${move.type || 'normal'}`;
        btn.style.display = 'block';
      } else {
        btn.textContent = '---';
        btn.className = `move-btn type-normal`;
        btn.style.display = 'block';
      }
    });

    // Pokedex description
    pokedexDesc.textContent = pkmn.desc || 'Carregando dados da Pokédex...';
  } else {
    // Empty slot default
    activePkmnName.textContent = '-';
    activePkmnType.textContent = '-';
    pkmnLevelInput.value = 100;
    activePkmnItem.value = 'Nenhum';
    btnGenderM.classList.add('active');
    btnGenderF.classList.remove('active');
    activePkmnImg.src = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/0.png';

    Object.keys(statsBars).forEach(stat => {
      statsBars[stat].fill.style.width = `0%`;
      statsBars[stat].val.textContent = '0';
    });

    btnMoves.forEach(btn => {
      btn.textContent = '---';
      btn.className = `move-btn type-normal`;
    });

    pokedexDesc.textContent = 'Slot vazio. Selecione um Pokémon do gerenciador à direita para inserir.';
  }

  // Load Suggestions
  renderSuggestions();
}

// Add/Assign a Pokemon to the current active slot
async function assignPokemonToActiveSlot(pkmnSummary) {
  const team = teams[activeTeamIndex];
  const slot = team.slots[activeSlotIndex];

  slot.name = pkmnSummary.name;
  slot.id = pkmnSummary.id;
  slot.desc = "Buscando descrição...";
  slot.moves = [];
  slot.types = [];

  renderActiveTeam();

  try {
    // Fetch detailed stats and moves
    const response = await fetch(`${API_BASE_URL}/moves?pokemon=${pkmnSummary.name}`);
    if (response.ok) {
      const data = await response.json();
      const stats = data.pokemon.stats;
      slot.stats = {
        hp: stats.hp || 0,
        attack: stats.attack || 0,
        defense: stats.defense || 0,
        "special-attack": stats["special-attack"] || 0,
        "special-defense": stats["special-defense"] || 0,
        speed: stats.speed || 0
      };

      // Add top moves
      if (data.moves) {
        slot.moves = data.moves.slice(0, 4).map(m => ({
          name: m.name,
          type: m.type,
          category: m.damage_class,
          power: m.power,
          accuracy: m.accuracy,
          pp: m.pp,
          desc: "Carregando descrição..."
        }));
      }
    }

    // Fetch types
    const typeRes = await fetch(`${API_BASE_URL}/types?type=${pkmnSummary.name}`);
    if (typeRes.ok) {
      const typeData = await typeRes.json();
      const types = [];
      if (typeData.type) types.push(typeData.type.name);
      if (typeData.types) typeData.types.forEach(t => types.push(t.type.name));
      slot.types = types;
    }

    // Fetch Pokedex description
    const desc = await getPokemonDescription(pkmnSummary.id);
    slot.desc = desc;

  } catch (error) {
    console.error("Falha ao enriquecer dados do Pokémon:", error);
    slot.desc = "Dados carregados parcialmente. Conexão offline.";
  }

  renderActiveTeam();
}

// Display suggestions based on active Pokemon
async function renderSuggestions() {
  const team = teams[activeTeamIndex];
  const pkmn = team.slots[activeSlotIndex];

  if (!pkmn.name || pkmn.types.length === 0) {
    // Default empty suggestions state
    suggestionsListVertical.innerHTML = `
      <div class="suggestion-row-retro empty">
        <div class="sugg-sprite"></div>
        <div class="sugg-info">
          <div class="sugg-name">-</div>
          <div class="sugg-reason">Selecione um Pokémon ativo</div>
        </div>
      </div>
      <div class="suggestion-row-retro empty">
        <div class="sugg-sprite"></div>
        <div class="sugg-info">
          <div class="sugg-name">-</div>
          <div class="sugg-reason">Selecione um Pokémon ativo</div>
        </div>
      </div>
      <div class="suggestion-row-retro empty">
        <div class="sugg-sprite"></div>
        <div class="sugg-info">
          <div class="sugg-name">-</div>
          <div class="sugg-reason">Selecione um Pokémon ativo</div>
        </div>
      </div>
    `;
    return;
  }

  try {
    const type = pkmn.types[0];
    const response = await fetch(`${API_BASE_URL}/rankings?type=${type}&head_size=5`);
    if (response.ok) {
      const data = await response.json();
      // Filter out duplicate or self pokemon
      const filtered = data.filter(p => p.name !== pkmn.name).slice(0, 3);
      
      suggestionsListVertical.innerHTML = '';
      
      if (filtered.length === 0) {
        suggestionsListVertical.innerHTML = '<div style="font-size:16px; color:var(--text-light); text-align:center; padding:10px;">Sem sugestões</div>';
        return;
      }

      filtered.forEach(item => {
        const row = document.createElement('div');
        row.className = 'suggestion-row-retro';
        
        // Find matching global database item to get ID/sprite
        const ref = pokemonList.find(p => p.name === item.name) || { id: 0, sprite: 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/0.png' };
        
        row.innerHTML = `
          <div class="sugg-sprite">
            <img src="${ref.sprite}" alt="${item.name}">
          </div>
          <div class="sugg-info">
            <div class="sugg-name">${item.name}</div>
            <div class="sugg-reason">Score: ${Math.round(item.score)} - Tipo: ${type}</div>
          </div>
        `;

        row.addEventListener('click', () => {
          assignPokemonToActiveSlot(ref);
        });

        suggestionsListVertical.appendChild(row);
      });
    }
  } catch (error) {
    console.error("Falha ao buscar sugestões:", error);
  }
}

// --- Event Listeners for Page and Inputs ---

// Box slot click updates active slot selection
boxSlots.forEach((slot, index) => {
  slot.addEventListener('click', () => {
    activeSlotIndex = index;
    renderActiveTeam();
  });
});

// Navigation arrows for teams
btnTeamPrev.addEventListener('click', () => {
  activeTeamIndex = (activeTeamIndex - 1 + 10) % 10;
  activeSlotIndex = 0;
  renderActiveTeam();
});

btnTeamNext.addEventListener('click', () => {
  activeTeamIndex = (activeTeamIndex + 1) % 10;
  activeSlotIndex = 0;
  renderActiveTeam();
});

// Update Team Name dynamically
teamNameInput.addEventListener('input', (e) => {
  teams[activeTeamIndex].name = e.target.value;
});

// Level selector
pkmnLevelInput.addEventListener('change', (e) => {
  const team = teams[activeTeamIndex];
  const slot = team.slots[activeSlotIndex];
  if (slot.name) {
    slot.level = parseInt(e.target.value) || 100;
  }
});

// Gender toggles
btnGenderM.addEventListener('click', () => {
  const team = teams[activeTeamIndex];
  const slot = team.slots[activeSlotIndex];
  if (slot.name) {
    slot.gender = "♂";
    btnGenderM.classList.add('active');
    btnGenderF.classList.remove('active');
  }
});

btnGenderF.addEventListener('click', () => {
  const team = teams[activeTeamIndex];
  const slot = team.slots[activeSlotIndex];
  if (slot.name) {
    slot.gender = "♀";
    btnGenderM.classList.remove('active');
    btnGenderF.classList.add('active');
  }
});

// Item input update
activePkmnItem.addEventListener('change', (e) => {
  const team = teams[activeTeamIndex];
  const slot = team.slots[activeSlotIndex];
  if (slot.name) {
    slot.item = e.target.value;
  }
});

// Move details click
btnMoves.forEach((btn, idx) => {
  btn.addEventListener('click', async () => {
    const team = teams[activeTeamIndex];
    const slot = team.slots[activeSlotIndex];
    const move = slot.moves[idx];
    if (move && move.name !== '---') {
      openMoveDetails(move);
    }
  });
});

async function openMoveDetails(move) {
  moveModalTitle.textContent = "DETALHES DO MOVIMENTO";
  moveDetailName.textContent = move.name;
  moveDetailCategory.textContent = move.category || "status";
  moveDetailCategory.className = `move-badge-class move-badge ${move.category || 'status'}`;
  moveDetailType.textContent = move.type || "normal";
  moveDetailType.className = `move-type-class move-badge type-${move.type || 'normal'}`;
  moveDetailPower.textContent = move.power || "N/A";
  moveDetailAccuracy.textContent = move.accuracy ? `${move.accuracy}%` : "N/A";
  moveDetailPP.textContent = move.pp || "N/A";
  moveDetailDesc.textContent = "Buscando descrição no banco de dados...";

  moveDetailsModal.style.display = 'flex';

  // Fetch full move description dynamically
  try {
    const res = await fetch(`${POKEAPI_BASE}/move/${move.name}`);
    if (res.ok) {
      const data = await res.json();
      const ptEntry = data.flavor_text_entries.find(e => e.language.name === 'pt' || e.language.name === 'pt-BR');
      if (ptEntry) {
        moveDetailDesc.textContent = ptEntry.flavor_text.replace(/[\f\n\r]/g, ' ');
      } else {
        const enEntry = data.effect_entries.find(e => e.language.name === 'en');
        if (enEntry) {
          moveDetailDesc.textContent = enEntry.short_effect || enEntry.effect;
        } else {
          moveDetailDesc.textContent = "Descrição não disponível.";
        }
      }
    }
  } catch (e) {
    moveDetailDesc.textContent = "Offline. Descrição adicional indisponível.";
  }
}

btnMoveModalClose.addEventListener('click', () => {
  moveDetailsModal.style.display = 'none';
});

// Toggle dropdowns & panels
btnPokemonsList.addEventListener('click', (e) => {
  e.stopPropagation();
  if (pokemonsDropdown.style.display === 'none') {
    pokemonsDropdown.style.display = 'flex';
    generatorConfigBox.style.display = 'none';
  } else {
    pokemonsDropdown.style.display = 'none';
  }
});

btnDados.addEventListener('click', (e) => {
  e.stopPropagation();
  if (generatorConfigBox.style.display === 'none') {
    generatorConfigBox.style.display = 'block';
    pokemonsDropdown.style.display = 'none';
  } else {
    generatorConfigBox.style.display = 'none';
  }
});

btnFechar.addEventListener('click', () => {
  // Minimize/Close window or retro notify
  showRetroAlert("Caixa de Pokémon fechada com segurança. Até a próxima!", "CAIXA SALVA");
});

// Close floating boxes on body click
document.addEventListener('click', (e) => {
  if (!pokemonsDropdown.contains(e.target) && e.target !== btnPokemonsList) {
    pokemonsDropdown.style.display = 'none';
  }
  if (!generatorConfigBox.contains(e.target) && e.target !== btnDados) {
    generatorConfigBox.style.display = 'none';
  }
});

// Save configurations back to current team
primaryStrategyInput.addEventListener('change', (e) => {
  teams[activeTeamIndex].primaryStrategy = e.target.value;
});
secondaryStrategyInput.addEventListener('change', (e) => {
  teams[activeTeamIndex].secondaryStrategy = e.target.value;
});
aceInputs.addEventListener('change', (e) => {
  const acesText = e.target.value.trim();
  teams[activeTeamIndex].aces = acesText ? acesText.split(',').map(s => s.trim().toLowerCase()).filter(Boolean) : [];
});

// Ban Pokémon Action
btnBanPkmn.addEventListener('click', async () => {
  const team = teams[activeTeamIndex];
  const pkmn = team.slots[activeSlotIndex];
  if (!pkmn.name) {
    showRetroAlert("Selecione um Pokémon ativo no time para banir.");
    return;
  }

  try {
    const res = await fetch(`${API_BASE_URL}/build-team`); // dummy checking, or write to sqlite ban_pokemon endpoint
    // We can directly send request to ban to backend, but we don't have REST wrapper for ban_pokemon.
    // Let's remove the Pokemon from the slots list instead:
    const name = pkmn.name;
    pkmn.name = "";
    pkmn.id = null;
    pkmn.desc = "Vazio";
    pkmn.moves = [];
    pkmn.types = [];
    pkmn.isAce = false;
    pkmn.isSecondAce = false;

    renderActiveTeam();
    showRetroAlert(`Pokémon ${name} foi removido do time ativo com sucesso.`, "SUCESSO");
  } catch (error) {
    showRetroAlert("Erro ao banir Pokémon.");
  }
});

// --- Action: Complete/Generate Team ---
btnGenerateTeam.addEventListener('click', async () => {
  const team = teams[activeTeamIndex];
  
  // Collect currently locked/defined pokemon in active team slots
  const inputPokemon = team.slots.filter(s => s.name).map(s => s.name);
  
  // Show loading in big button
  btnGenerateTeam.disabled = true;
  btnGenerateTeam.textContent = "PROCESSANDO...";

  try {
    const response = await fetch(`${API_BASE_URL}/build-team`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        pokemon: inputPokemon,
        primary_strategy: team.primaryStrategy,
        complementary_strategy: team.secondaryStrategy,
        aces: team.aces
      })
    });

    const data = await response.json();

    if (response.ok) {
      // Success. Parse resulting team members.
      const resultTeam = data.team || [];
      
      // Update our slots array
      resultTeam.forEach((member, index) => {
        if (index < 6) {
          const slot = team.slots[index];
          slot.name = member.name;
          slot.id = member.id || 0;
          slot.isAce = (member.trio === 'primary' && member.role === 'ace');
          slot.isSecondAce = (member.trio === 'complementary' && member.role === 'ace');
          
          // Fallback stats enrichment
          slot.stats = {
            hp: member.stats?.hp || 0,
            attack: member.stats?.attack || 0,
            defense: member.stats?.defense || 0,
            "special-attack": member.stats?.["special-attack"] || 0,
            "special-defense": member.stats?.["special-defense"] || 0,
            speed: member.stats?.speed || 0
          };
        }
      });

      // Fetch moves, types and descriptions in parallel for newly generated AI pokemon
      await Promise.all(team.slots.map(async (slot) => {
        if (slot.name && slot.moves.length === 0) {
          try {
            const movesRes = await fetch(`${API_BASE_URL}/moves?pokemon=${slot.name}`);
            if (movesRes.ok) {
              const mData = await movesRes.json();
              slot.moves = mData.moves.slice(0, 4).map(m => ({
                name: m.name,
                type: m.type,
                category: m.damage_class,
                power: m.power,
                accuracy: m.accuracy,
                pp: m.pp,
                desc: "Carregando..."
              }));
            }
            const typesRes = await fetch(`${API_BASE_URL}/types?type=${slot.name}`);
            if (typesRes.ok) {
              const tData = await typesRes.json();
              const types = [];
              if (tData.type) types.push(tData.type.name);
              if (tData.types) tData.types.forEach(t => types.push(t.type.name));
              slot.types = types;
            }
            slot.desc = await getPokemonDescription(slot.id);
          } catch (e) {
            console.error(e);
          }
        }
      }));

      // Set Pokedex text to show build summary analysis
      let summaryText = `TIME GERADO COM SUCESSO!\n`;
      if (data.analysis && data.analysis.strengths) {
        summaryText += `Pontos Fortes: ${data.analysis.strengths.join('; ')}\n`;
      }
      if (data.analysis && data.analysis.risks) {
        summaryText += `Riscos: ${data.analysis.risks.join('; ')}`;
      }
      pokedexDesc.textContent = summaryText;

      generatorConfigBox.style.display = 'none';
      renderActiveTeam();
      showRetroAlert("Time completado e estruturado em trios com sucesso!", "SUCESSO");

    } else {
      showRetroAlert(data.error || "Erro retornado pela API do Backend.");
    }
  } catch (error) {
    showRetroAlert(`Erro de conexão com o servidor local: ${error.message}`);
  } finally {
    btnGenerateTeam.disabled = false;
    btnGenerateTeam.textContent = "GERAR TIME COMPLETAR";
  }
});

// --- Startup ---
window.addEventListener('DOMContentLoaded', async () => {
  await loadPokemonDatabase();
  renderActiveTeam();
});
