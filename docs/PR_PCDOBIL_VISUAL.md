# Pull Request: Implementação da Interface Visual "PC do Bill" (16-bit Retro)

## 📌 Descrição do PR
Este PR implementa a reformulação visual completa do aplicativo desktop (`desktop_app`) com base na especificação [`docs/pcdobil.md`](docs/pcdobil.md), trazendo uma estética retrô de RPG de 16 bits inspirada no sistema de armazenamento de Pokémon (PC do Bill).

---

## 🎨 Principais Mudanças e Componentes

### 1. Barra Superior Retrô (`AppShell.tsx`)
- Adicionada a tag `"DADOS"` no canto esquerdo.
- Botão verde-pálido `"EQUIPE POKEMON"` e botão azul-pálido `"FECHAR CAIXA"` para navegação.
- Botão cinza-escuro `"GERENCIADOR"` no canto direito.

### 2. Painel da Esquerda: Perfil do Pokémon (`PokemonDetailPanel.tsx`)
- Cabeçalho com seletor de **Level (1-100)** e botões de **Gênero (♂ / ♀)**.
- Retrato do Pokémon com moldura azul-clara e fundo quadriculado em cinza.
- Metadados em Português Brasileiro (Nome, Tipos com badges oficiais e Item Equipado).
- **4 botões coloridos de golpes** de acordo com o tipo do movimento, abrindo o modal de detalhes [`MoveDetailModal`](desktop_app/src/renderer/components/MoveDetailModal.tsx) com Nome, Categoria (Físico/Especial/Status), Tipo, Potência, Precisão, PP e Descrição.
- Gráfico de barras horizontais dos 6 atributos ([`StatBarChart`](desktop_app/src/renderer/components/StatBarChart.tsx)) para HP, Atk, Def, SpA, SpD e Spe.

### 3. Painel Central: Caixa de Armazenamento & Pokédex
- **Banner de Título da Caixa** ([`BoxHeader`](desktop_app/src/renderer/components/BoxHeader.tsx)) com árvores em pixel art (`🌲🌲`), título editável `"Time X (6 PkmN)"` e setas `<` e `>` para navegar entre até 10 times.
- **Grade de Pokémon** ([`PartySlotGrid`](desktop_app/src/renderer/components/PartySlotGrid.tsx)) sobre gramado verde, com sprites clássicos e marcadores visuais:
  - ⭐ **Estrela vermelha** no Ace do 1º trio.
  - ❤️ **Coração vermelho** no 2º Pokémon do trio.
- **Área "POKEDEX"** ([`PokedexEntryBox`](desktop_app/src/renderer/components/PokedexEntryBox.tsx)) com fundo quadriculado em azul-claro e texto descritivo/lore do Pokémon selecionado.

### 4. Painel da Direita: Gerenciador (`PokemonSearchPanel.tsx`)
- Abas "Pokémons" e "Sugestões".
- Catálogo completo com busca, filtros de tipo e tooltip retrô ao passar o mouse.
- Seção **"Sugestões"** ([`SynergySuggestions`](desktop_app/src/renderer/components/SynergySuggestions.tsx)) com 3 linhas de Pokémon recomendados que complementam o Pokémon ativo no time.

### 5. Design System Retrô (`app.css`)
- Paleta de cores oficial para os 18 tipos elementais de Pokémon.
- Padrões de textura em CSS (`bg-checkered-gray`, `bg-checkered-blue`, `bg-grass-field`).
- Tipografia retrô e bordas com sombreamento chanfrado.

---

## 📁 Arquivos Afetados

### Novos Arquivos:
- `desktop_app/src/renderer/components/BoxHeader.tsx`
- `desktop_app/src/renderer/components/MoveDetailModal.tsx`
- `desktop_app/src/renderer/components/PokedexEntryBox.tsx`
- `desktop_app/src/renderer/components/StatBarChart.tsx`
- `desktop_app/src/renderer/components/SynergySuggestions.tsx`
- `desktop_app/src/renderer/utils/pokemonFormatters.ts`
- `desktop_app/tests/renderer/pcdobilComponents.test.tsx`
- `docs/pcdobil-changes.md`

### Arquivos Modificados:
- `desktop_app/src/renderer/components/AppShell.tsx`
- `desktop_app/src/renderer/components/PartySlotGrid.tsx`
- `desktop_app/src/renderer/components/PokemonDetailPanel.tsx`
- `desktop_app/src/renderer/components/PokemonSearchPanel.tsx`
- `desktop_app/src/renderer/pages/TeamBuilderPage.tsx`
- `desktop_app/src/renderer/state/appState.ts`
- `desktop_app/src/renderer/types/app-state.ts`
- `desktop_app/src/renderer/styles/app.css`

---

## 🧪 Cobertura de Testes e Validação
- **Vitest**: `npm test` executado com **15 arquivos e 45 testes passando (100% de sucesso)**.
- **Typecheck**: `npm run typecheck` executado sem erros.
- **Build**: `npm run build` executado com sucesso gerando bundles de produção.
- **Python Unittest Suite**: `python3 -m unittest ...` executado com 69 testes passando sem regressões.

