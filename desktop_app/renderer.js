const { ipcRenderer } = require('electron');

// Base URLs
const API_BASE_URL = 'http://127.0.0.1:8002/api';

// Cache of 151 standard Pokemon for immediate autocomplete feedback
const POKEMON_DATABASE = [
  "bulbasaur", "ivysaur", "venusaur", "charmander", "charmeleon", "charizard",
  "squirtle", "wartortle", "blastoise", "caterpie", "metapod", "butterfree",
  "weedle", "kakuna", "beedrill", "pidgey", "pidgeotto", "pidgeot",
  "rattata", "raticate", "spearow", "fearow", "ekans", "arbok",
  "pikachu", "raichu", "sandshrew", "sandslash", "nidoran-f", "nidorina", "nidoqueen",
  "nidoran-m", "nidorino", "nidoking", "clefairy", "clefable", "vulpix", "ninetales",
  "jigglypuff", "wigglytuff", "zubat", "golbat", "oddish", "gloom", "vileplume",
  "paras", "parasect", "venonat", "venomoth", "diglett", "dugtrio", "meowth", "persian",
  "psyduck", "golduck", "mankey", "primeape", "growlithe", "arcanine",
  "poliwag", "poliwhirl", "poliwrath", "abra", "kadabra", "alakazam",
  "machop", "machoke", "machamp", "bellsprout", "weepinbell", "victreebel",
  "tentacool", "tentacruel", "geodude", "graveler", "golem", "ponyta", "rapidash",
  "slowpoke", "slowbro", "magnemite", "magneton", "farfetchd", "doduo", "dodrio",
  "seel", "dewgong", "grimer", "muk", "shellder", "cloyster", "gastly", "haunter", "gengar",
  "onix", "drowzee", "hypno", "krabby", "kingler", "voltorb", "electrode",
  "exeggcute", "exeggutor", "cubone", "marowak", "hitmonlee", "hitmonchan",
  "lickitung", "koffing", "weezing", "rhyhorn", "rhydon", "chansey", "tangela", "kangaskhan",
  "horsea", "seadra", "goldeen", "seaking", "staryu", "starmie", "mr-mime", "scyther",
  "jynx", "electabuzz", "magmar", "pinsir", "tauros", "magikarp", "gyarados", "lapras",
  "ditto", "eevee", "vaporeon", "jolteon", "flareon", "porygon", "omanyte", "omastar",
  "kabuto", "kabutops", "aerodactyl", "snorlax", "articuno", "zapdos", "moltres",
  "dratini", "dragonair", "dragonite", "mewtwo", "mew"
];

// App State
let selectedPokemon = [];

// DOM Elements
const primaryStrategyInput = document.getElementById('primary-strategy');
const complementaryStrategyInput = document.getElementById('complementary-strategy');
const aceInputs = document.getElementById('ace-inputs');
const pokemonSearchInput = document.getElementById('pokemon-search');
const suggestionsDiv = document.getElementById('suggestions');
const selectedListDiv = document.getElementById('selected-list');
const selectedCountSpan = document.getElementById('selected-count');
const btnGenerate = document.getElementById('btn-generate');
const alertContainer = document.getElementById('alert-container');

// AI Chat elements
const aiProviderSelect = document.getElementById('ai-provider-select');
const chatMessagesDiv = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const btnChatSend = document.getElementById('btn-chat-send');

// Trio Containers
const primaryStrategyBadge = document.getElementById('primary-strategy-badge');
const complementaryStrategyBadge = document.getElementById('complementary-strategy-badge');
const primaryCardsDiv = document.getElementById('primary-cards');
const complementaryCardsDiv = document.getElementById('complementary-cards');

// Analysis
const strengthsList = document.getElementById('strengths-list');
const risksList = document.getElementById('risks-list');
const typeGrid = document.getElementById('type-grid');

// Modal Elements
const detailModal = document.getElementById('detail-modal');
const modalPokemonName = document.getElementById('modal-pokemon-name');
const modalStatsDiv = document.getElementById('modal-stats');
const modalMovesDiv = document.getElementById('modal-moves');
const modalCloseBtn = document.getElementById('modal-close');

// --- Search & Autocomplete Event Listeners ---
pokemonSearchInput.addEventListener('input', (e) => {
  const query = e.target.value.toLowerCase().trim();
  if (!query) {
    suggestionsDiv.style.display = 'none';
    return;
  }

  const matches = POKEMON_DATABASE.filter(name => name.includes(query)).slice(0, 8);
  if (matches.length === 0) {
    suggestionsDiv.style.display = 'none';
    return;
  }

  suggestionsDiv.innerHTML = '';
  matches.forEach(name => {
    const item = document.createElement('div');
    item.className = 'suggestion-item';
    
    // Add miniature pokeball icon
    item.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="color: var(--accent-pink);">
        <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm0 8c1.103 0 2 .897 2 2s-.897 2-2 2-2-.897-2-2 .897-2 2-2z"/>
      </svg>
      <span style="text-transform: capitalize;">${name}</span>
    `;
    item.addEventListener('click', () => {
      addPokemon(name);
      pokemonSearchInput.value = '';
      suggestionsDiv.style.display = 'none';
    });
    suggestionsDiv.appendChild(item);
  });

  suggestionsDiv.style.display = 'block';
});

// Close suggestions when clicking outside
document.addEventListener('click', (e) => {
  if (!pokemonSearchInput.contains(e.target) && !suggestionsDiv.contains(e.target)) {
    suggestionsDiv.style.display = 'none';
  }
});

// Add custom pokemon typing on Enter
pokemonSearchInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    const value = pokemonSearchInput.value.trim().toLowerCase();
    if (value) {
      addPokemon(value);
      pokemonSearchInput.value = '';
      suggestionsDiv.style.display = 'none';
    }
  }
});

// --- State Functions ---
function addPokemon(name) {
  if (selectedPokemon.length >= 6) {
    showAlert('O time pode ter no máximo 6 Pokémon.', 'warning');
    return;
  }
  if (selectedPokemon.includes(name)) {
    showAlert('Este Pokémon já foi adicionado.', 'warning');
    return;
  }
  selectedPokemon.push(name);
  renderSelectedList();
}

function removePokemon(name) {
  selectedPokemon = selectedPokemon.filter(p => p !== name);
  renderSelectedList();
}

function renderSelectedList() {
  selectedCountSpan.textContent = selectedPokemon.length;
  selectedListDiv.innerHTML = '';

  selectedPokemon.forEach(name => {
    const item = document.createElement('div');
    item.className = 'selected-item';

    item.innerHTML = `
      <div class="selected-item-info">
        <span>${name}</span>
        <span class="lock-badge"><i class="fas fa-lock"></i> User</span>
      </div>
      <button class="btn-remove" title="Remove">&times;</button>
    `;

    item.querySelector('.btn-remove').addEventListener('click', () => removePokemon(name));
    selectedListDiv.appendChild(item);
  });
}

// --- Alerts ---
function showAlert(message, type = 'danger') {
  alertContainer.innerHTML = `
    <div class="alert-box">
      <div class="alert-title">${type === 'warning' ? 'Atenção' : 'Erro'}</div>
      <div>${message}</div>
    </div>
  `;
  alertContainer.style.display = 'block';
  setTimeout(() => {
    alertContainer.style.display = 'none';
  }, 5000);
}

// --- API Requests ---
btnGenerate.addEventListener('click', async () => {
  const primaryStrategy = primaryStrategyInput.value.trim() || 'balanced pressure';
  const complementaryStrategy = complementaryStrategyInput.value.trim() || 'complementary coverage';
  
  // Parse Aces
  const acesText = aceInputs.value.trim();
  const aces = acesText ? acesText.split(',').map(s => s.trim().toLowerCase()).filter(Boolean) : [];

  primaryStrategyBadge.textContent = primaryStrategy;
  complementaryStrategyBadge.textContent = complementaryStrategy;

  // Show loading state
  btnGenerate.disabled = true;
  btnGenerate.textContent = 'Generating Team...';

  try {
    const response = await fetch(`${API_BASE_URL}/build-team`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        pokemon: selectedPokemon,
        primary_strategy: primaryStrategy,
        complementary_strategy: complementaryStrategy,
        aces: aces
      })
    });

    const data = await response.json();

    if (response.ok) {
      renderGeneratedTeam(data);
    } else {
      showAlert(data.error || 'Erro ao gerar o time.', 'danger');
    }
  } catch (error) {
    showAlert(`Conexão falhou: ${error.message}. Verifique se o servidor local está rodando na porta 8002.`, 'danger');
  } finally {
    btnGenerate.disabled = false;
    btnGenerate.textContent = 'Generate Team';
  }
});

// --- UI Rendering ---
function renderGeneratedTeam(result) {
  // Clear slots
  primaryCardsDiv.innerHTML = '';
  complementaryCardsDiv.innerHTML = '';

  const team = result.team || [];
  
  // Primary (indices 0, 1, 2)
  const primaryMembers = team.filter(m => m.trio === 'primary');
  // Complementary (indices 3, 4, 5)
  const complementaryMembers = team.filter(m => m.trio === 'complementary');

  renderTrio(primaryMembers, primaryCardsDiv);
  renderTrio(complementaryMembers, complementaryCardsDiv);

  // Render Analysis
  renderAnalysis(result.analysis, team);

  // Render Pending Warnings if any
  if (result.pending && result.pending.length > 0) {
    renderPendingAlerts(result.pending);
  } else {
    alertContainer.style.display = 'none';
  }
}

function renderTrio(members, container) {
  if (members.length === 0) {
    container.innerHTML = '<div class="pokemon-card empty-card"><p>Nenhum Pokémon neste trio.</p></div>';
    return;
  }

  members.forEach(member => {
    const card = document.createElement('div');
    const isAce = member.role === 'ace';
    card.className = `pokemon-card ${isAce ? 'is-ace' : ''}`;
    
    // Official Artwork Image URL
    const spriteUrl = member.id 
      ? `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${member.id}.png`
      : 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/0.png';

    card.innerHTML = `
      ${isAce ? '<div class="ace-badge">👑 ACE</div>' : ''}
      <div class="pkmn-image-wrapper">
        <img class="pkmn-image" src="${spriteUrl}" alt="${member.name}" onerror="this.src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${member.id || 0}.png'">
      </div>
      <div class="pkmn-info">
        <div class="pkmn-header-row">
          <span class="pkmn-name">${member.name}</span>
          <span class="role-badge ${member.role}">${member.role}</span>
        </div>
        <div class="mini-stats">
          <div class="mini-stat-item">
            <span class="stat-lbl">HP</span>
            <span class="stat-val">${member.stats?.hp || 0}</span>
          </div>
          <div class="mini-stat-item">
            <span class="stat-lbl">Atk</span>
            <span class="stat-val">${member.stats?.attack || 0}</span>
          </div>
          <div class="mini-stat-item">
            <span class="stat-lbl">Def</span>
            <span class="stat-val">${member.stats?.defense || 0}</span>
          </div>
          <div class="mini-stat-item">
            <span class="stat-lbl">Spd</span>
            <span class="stat-val">${member.stats?.speed || 0}</span>
          </div>
        </div>
      </div>
    `;

    card.addEventListener('click', () => openMovesetModal(member));
    container.appendChild(card);
  });
}

function renderAnalysis(analysis, team) {
  // Strengths
  strengthsList.innerHTML = '';
  const strengths = analysis.strengths || [];
  if (strengths.length === 0) {
    strengthsList.innerHTML = '<li>Nenhum ponto forte destacado.</li>';
  } else {
    strengths.forEach(str => {
      const li = document.createElement('li');
      li.textContent = str;
      strengthsList.appendChild(li);
    });
  }

  // Risks
  risksList.innerHTML = '';
  const risks = analysis.risks || [];
  if (risks.length === 0) {
    risksList.innerHTML = '<li>Nenhum risco crítico identificado.</li>';
  } else {
    risks.forEach(rsk => {
      const li = document.createElement('li');
      li.textContent = rsk;
      risksList.appendChild(li);
    });
  }

  // Compute Type Resistances on the fly
  computeTypeResistances(team);
}

function renderPendingAlerts(pendings) {
  alertContainer.innerHTML = '';
  pendings.forEach(p => {
    const alertBox = document.createElement('div');
    alertBox.className = 'alert-box';
    alertBox.style.marginBottom = '10px';
    alertBox.innerHTML = `
      <div class="alert-title">⚠️ Aviso (${p.type})</div>
      <div><strong>Entrada:</strong> ${p.input || 'N/A'}</div>
      <div>${p.reason}</div>
    `;
    alertContainer.appendChild(alertBox);
  });
  alertContainer.style.display = 'block';
}

// --- Type Resistance Calculator ---
const TYPE_CHART = {
  normal: { rock: 0.5, ghost: 0, steel: 0.5 },
  fire: { fire: 0.5, water: 0.5, grass: 2, ice: 2, bug: 2, rock: 0.5, dragon: 0.5, steel: 2, fairy: 0.5 },
  water: { fire: 2, water: 0.5, grass: 0.5, ground: 2, rock: 2, dragon: 0.5 },
  electric: { water: 2, electric: 0.5, grass: 0.5, ground: 0, flying: 2, dragon: 0.5 },
  grass: { fire: 0.5, water: 2, grass: 0.5, poison: 0.5, ground: 2, flying: 0.5, bug: 0.5, rock: 2, dragon: 0.5, steel: 0.5 },
  ice: { fire: 0.5, water: 0.5, grass: 2, ice: 0.5, ground: 2, flying: 2, dragon: 2, steel: 0.5 },
  fighting: { normal: 2, ice: 2, poison: 0.5, flying: 0.5, psychic: 0.5, bug: 0.5, rock: 2, ghost: 0, dark: 2, steel: 2, fairy: 0.5 },
  poison: { grass: 2, poison: 0.5, ground: 0.5, rock: 0.5, ghost: 0.5, steel: 0, fairy: 2 },
  ground: { fire: 2, electric: 2, grass: 0.5, poison: 2, flying: 0, bug: 0.5, rock: 2, steel: 2 },
  flying: { electric: 0.5, grass: 2, fighting: 2, bug: 2, rock: 0.5, steel: 0.5 },
  psychic: { fighting: 2, poison: 2, psychic: 0.5, dark: 0, steel: 0.5 },
  bug: { fire: 0.5, grass: 2, fighting: 0.5, poison: 0.5, flying: 0.5, psychic: 2, ghost: 0.5, dark: 2, steel: 0.5, fairy: 0.5 },
  rock: { fire: 2, ice: 2, fighting: 0.5, ground: 0.5, flying: 2, bug: 2, steel: 0.5 },
  ghost: { normal: 0, psychic: 2, ghost: 2, dark: 0.5 },
  dragon: { dragon: 2, steel: 0.5, fairy: 0 },
  dark: { fighting: 0.5, psychic: 2, ghost: 2, dark: 0.5, fairy: 0.5 },
  steel: { fire: 0.5, water: 0.5, electric: 0.5, ice: 2, rock: 2, steel: 0.5, fairy: 2 },
  fairy: { fighting: 2, poison: 0.5, dragon: 0, dark: 2, steel: 0.5 }
};

// Types list for printing
const TYPES_LIST = Object.keys(TYPE_CHART);

async function computeTypeResistances(team) {
  typeGrid.innerHTML = '';
  
  // We need to know each team member's types.
  // Since build_pokemon_team output only contains name and stats, let's fetch type details
  // on the fly, or if they are missing, default to showing type table.
  const teamTypeLists = [];

  for (let member of team) {
    try {
      const response = await fetch(`${API_BASE_URL}/types?type=${member.name}`);
      if (response.ok) {
        const typeData = await response.json();
        // typeData has name, etc.
        const types = typeData.type ? [typeData.type.name] : [];
        if (typeData.types) {
          typeData.types.forEach(t => types.push(t.type.name));
        }
        teamTypeLists.push(types);
      }
    } catch {
      // ignore fetching error
    }
  }

  if (teamTypeLists.length === 0) {
    typeGrid.innerHTML = '<div style="color: var(--text-muted); font-size:12px;">Carregando efetividades...</div>';
    return;
  }

  // Calculate net vulnerability multiplier for each of the 18 types
  const resistances = {};
  TYPES_LIST.forEach(attackingType => {
    let multiplier = 1.0;
    
    teamTypeLists.forEach(memberTypes => {
      let memberMultiplier = 1.0;
      memberTypes.forEach(t => {
        // Look up how attackingType does against t
        if (TYPE_CHART[attackingType] && TYPE_CHART[attackingType][t] !== undefined) {
          memberMultiplier *= TYPE_CHART[attackingType][t];
        }
      });
      multiplier += memberMultiplier; // sum up values
    });

    resistances[attackingType] = multiplier / teamTypeLists.length;
  });

  // Render types
  TYPES_LIST.forEach(type => {
    const val = resistances[type];
    const cell = document.createElement('div');
    cell.className = 'type-cell';
    cell.textContent = type;

    // Color code according to resistance level
    if (val < 1.0) {
      cell.style.background = 'rgba(74, 211, 142, 0.15)';
      cell.style.color = 'var(--accent-green)';
      cell.style.border = '1px solid rgba(74, 211, 142, 0.4)';
    } else if (val > 1.2) {
      cell.style.background = 'rgba(255, 100, 100, 0.15)';
      cell.style.color = '#ff5555';
      cell.style.border = '1px solid rgba(255, 100, 100, 0.4)';
    } else {
      cell.style.background = 'rgba(255, 255, 255, 0.05)';
      cell.style.color = 'var(--text-secondary)';
      cell.style.border = '1px solid var(--border-color)';
    }
    
    typeGrid.appendChild(cell);
  });
}

// --- Moveset Details Modal ---
async function openMovesetModal(member) {
  modalPokemonName.textContent = member.name;
  modalStatsDiv.innerHTML = `
    <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 8px;">
      <strong>Inferred Role:</strong> <span style="text-transform: capitalize; color: var(--accent-cyan); font-weight:700;">${member.role}</span>
    </div>
  `;
  modalMovesDiv.innerHTML = '<div style="color: var(--text-muted); padding: 10px;">Loading ranked movesets...</div>';
  detailModal.style.display = 'flex';

  try {
    const response = await fetch(`${API_BASE_URL}/moves?pokemon=${member.name}`);
    const data = await response.json();

    if (response.ok) {
      renderMovesList(data.moves || []);
    } else {
      modalMovesDiv.innerHTML = `<div style="color: var(--accent-orange); padding: 10px;">${data.error || 'Falha ao buscar movimentos.'}</div>`;
    }
  } catch (error) {
    modalMovesDiv.innerHTML = `<div style="color: var(--accent-pink); padding: 10px;">Erro de conexão: ${error.message}</div>`;
  }
}

function renderMovesList(moves) {
  modalMovesDiv.innerHTML = '';
  
  if (moves.length === 0) {
    modalMovesDiv.innerHTML = '<div style="color: var(--text-muted); padding: 10px;">Nenhum movimento encontrado.</div>';
    return;
  }

  // Slice first 12 moves for display to keep list tidy
  moves.slice(0, 12).forEach(move => {
    const row = document.createElement('div');
    row.className = 'move-row';

    const dmgClass = move.damage_class || 'physical';
    
    row.innerHTML = `
      <div>
        <div class="move-name">${move.name}</div>
        <div class="move-meta">
          <span>Type: <strong style="text-transform:uppercase; color: var(--accent-cyan);">${move.type || 'normal'}</strong></span>
          <span>PP: <strong>${move.pp || 'N/A'}</strong></span>
        </div>
      </div>
      <div style="display: flex; align-items: center; gap: 8px;">
        <span class="move-badge ${dmgClass}">${dmgClass}</span>
        ${move.power ? `<span style="font-size:12px; font-weight:600; color: var(--accent-pink);">Pwr: ${move.power}</span>` : ''}
        ${move.accuracy ? `<span style="font-size:12px; font-weight:600; color: var(--accent-green);">Acc: ${move.accuracy}%</span>` : ''}
      </div>
    `;

    modalMovesDiv.appendChild(row);
  });
}

// Close Modal
modalCloseBtn.addEventListener('click', () => {
  detailModal.style.display = 'none';
});

window.addEventListener('click', (e) => {
  if (e.target === detailModal) {
    detailModal.style.display = 'none';
  }
});

// --- AI Chat Event Listeners & Functions ---

btnChatSend.addEventListener('click', () => sendChatMessage());

chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    sendChatMessage();
  }
});

async function sendChatMessage() {
  const query = chatInput.value.trim();
  if (!query) return;

  const provider = aiProviderSelect.value;
  
  // Clear input
  chatInput.value = '';

  // Append user message bubble
  appendChatBubble(query, 'user');

  // Show typing indicator
  const typingBubble = appendTypingIndicator();

  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: query,
        provider: provider,
        current_team: selectedPokemon
      })
    });

    const data = await response.json();
    
    // Remove typing indicator
    typingBubble.remove();

    if (response.ok) {
      // Append AI response
      appendChatBubble(data.response, 'assistant');
      
      // If AI updated/generated team, automatically render it
      if (data.team_data) {
        if (data.team_data.team) {
          // If the AI updated the locked team members, update our selectedPokemon state
          selectedPokemon = data.team_data.team
            .filter(m => m.source === 'user')
            .map(m => m.name);
          renderSelectedList();
        }
        renderGeneratedTeam(data.team_data);
      }
    } else {
      appendChatBubble(data.error || 'Desculpe, ocorreu um erro ao processar a mensagem.', 'assistant');
    }
  } catch (error) {
    typingBubble.remove();
    appendChatBubble(`Erro de conexão: ${error.message}. Certifique-se de que a API local está rodando e a chave de API da IA está configurada no arquivo .env.`, 'assistant');
  }
}

function appendChatBubble(text, role) {
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${role}`;
  // Use simple formatting: break lines and bold items in Em
  bubble.innerHTML = text.replace(/\n/g, '<br>');
  chatMessagesDiv.appendChild(bubble);
  
  // Scroll to bottom
  chatMessagesDiv.scrollTop = chatMessagesDiv.scrollHeight;
  return bubble;
}

function appendTypingIndicator() {
  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble assistant';
  bubble.innerHTML = `
    <div class="typing-dots">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  chatMessagesDiv.appendChild(bubble);
  chatMessagesDiv.scrollTop = chatMessagesDiv.scrollHeight;
  return bubble;
}
