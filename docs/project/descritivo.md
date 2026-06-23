# Descritivo do projeto

Descrição de tela de pokemon por consumo de API.

# Telas

## Tela de montagem de time 

Essa tela inicial demonstra um pokemon com seus detalhes (selecionado da party) e até 6 pokemons da party sem detalhes.

Os detalhes do pokemon selecionado devem ser exibidos de maneira interativa. Os detalhes do time de 6 pokemons deve ser seus sprites.

Cada pokemon possui informações customizadas:

- Pontos distribuídos (pontos de IV que são adicionados pelo usuário)
- Golpes escolhidos
- Item escolhido
- Informações gerais do pokemon (via BFF Python)

Os dados informados pelo usuário são armazenados em um banco de dados via Fast API.

### Listar pokemons com filtro

Aplica filtro de listagem:

- Tipo A (seletor)
- Tipo B (seletor)
- Nome (barra de pesquisa)
- Numero de pokedex (barra de pesquisa)

Na listagem quando se adicionar uma letra deve-se compor uma nova lista apresentando os pokemons em ordem de numero da pokedex.

Chamada à Pokeapi via BFF Python.

### Listar naturezas

Deve-se apresentar uma lista (seletor) com as naturezas possíveis de um pokemon. A natureza deve apresentar seu bonus e onus de status, bem como a descrição.

- Nome
- Status bonus
- Status onus
- Descrição

Chamada à Pokeapi via BFF Python. 

### Listar Items

Deve-se apresentar uma lista (seletor) contendo todos os items possíveis para um pokemon. A lista deve ser usada para selecionar o item de um pokemon e deve apresentar para cada item:

- Nome
- Descrição
- URL da imagem

Chamada à Pokeapi via BFF Python.

### Buscar dados do pokemon

Ao selecionar um pokemon da listagem deve-se buscar os dados do pokemon e apresenta-los na aba da esquerda, a aba contém dados de:

- Nome
- Tipo A
- Tipo B
- Status (pontos base por status do pokemon)
- Status total (calculo da pontuação via BFF Python)
- Lista de golpes
- Lista de habilidades
- URL da imagem

Chamada à Pokeapi via BFF Python.

### Buscar dados de vários golpes

Ao selecionar um pokemon, aparecem 4 campos para seleção de quatro golpes. Cada campo seleciona um golpe de modo a abrir uma lista de golpes e permitir a seleção de um. Cada golpe da lista é composto por:

- Nome
- Tipo
- Power
- PP
- Descrição
- Tipo de ataque (Fisico ou especial)

Ao selecionar um golpe o movimento deve ser adicionado a um dos blocos de golpes e esse deve sair da lista de seleção.

Seus dados devem popular o campo (descrição em um pop-up ao passar o mouse).

## Tela de exibição de time

Na tela de montagem deve haver um botão para salvar o time. Na tela de exibição serão exibidos todos os times, com paginação de 3 a 3. As chamadas serão mistas no BFF Python para a Pokeapi e na Fast API.