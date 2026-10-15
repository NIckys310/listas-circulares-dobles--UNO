# 🃏 Mesa de Turnos UNO: Lista Circular Doble

Taller de Estructuras de Datos. Caso de estudio: **la mesa de turnos de un juego de UNO**.

En UNO los turnos **nunca terminan**: después del último jugador le toca otra vez al primero. Además, la carta **Reversa** cambia el sentido del juego, así que hay que poder avanzar hacia la derecha (`next`) **y** hacia la izquierda (`prev`). Por eso la estructura ideal es una **lista circular doble**.

```
        ┌──────────── next ───────────┐
        ▼                             │
     [Nicky] ⇄ [Alex] ⇄ [Sofía] ⇄ [Mateo]
        │                             ▲
        └──────────── prev ───────────┘
```

## 🌐 Ver en línea

**https://nickys310.github.io/listas-circulares-dobles--UNO/**

En GitHub Pages el mismo código Python corre dentro del navegador con [Pyodide](https://pyodide.org). La primera carga tarda unos segundos.

## ▶️ Cómo ejecutarlo en tu computador

Solo necesitas Python 3.9 o superior (no hay que instalar librerías).

```bash
python server.py
```

Se abre el navegador en **http://localhost:5050**.

Para abrirlo desde un celular conectado al mismo WiFi: `python server.py --lan`.

Pruebas unitarias:

```bash
python -m unittest -v
```

## 🧱 Estructura del código (en inglés)

| Archivo | Contenido |
|---|---|
| `turn_table.py` | Clase `Player` (nodo) y clase `TurnTable` (lista circular doble) |
| `api.py` | Acciones que puede pedir la página (las usa el servidor y la versión en línea) |
| `server.py` | Servidor web local (librería estándar de Python) |
| `index.html` | Entrada para GitHub Pages |
| `static/` | Interfaz en español (HTML, CSS y JavaScript) |
| `test_turn_table.py` | Pruebas unitarias |

### Clase `Player` (nodo)
| Atributo | Significado |
|---|---|
| `name` | Nombre del jugador |
| `cards` | Cartas en la mano |
| `next` | Jugador de la derecha |
| `prev` | Jugador de la izquierda |

### Clase `TurnTable` (lista circular doble)
| Método | Operación de lista | En el juego |
|---|---|---|
| `join_player(name)` | Insertar al final (entre el último y el primero) | Un jugador se sienta |
| `join_player_after(name, neighbour)` | Insertar después de un nodo | Se sienta al lado de alguien |
| `eliminate_player(name)` | Eliminar un nodo y re-enlazar a sus vecinos | Un jugador se va o gana |
| `find_player(name)` | Búsqueda | Buscar a un jugador |
| `traverse(start, clockwise)` | Recorrido en ambos sentidos | Ver el orden de la mesa |
| `next_turn()` | Avanzar por `next` o `prev` | Pasar el turno |
| `reverse_direction()` | Cambiar de `next` a `prev` | Carta **Reversa** |
| `skip_turn()` | Saltar un nodo | Carta **Salta** |
| `play_draw_two()` | Modificar el nodo vecino y saltarlo | Carta **+2** |
| `shuffle_seats()` | Re-enlazar todos los nodos | Mezclar puestos |

### Casos especiales que maneja
- **Un solo jugador:** su `next` y su `prev` apuntan a él mismo.
- **Eliminar el primero (`head`):** `head` pasa al siguiente.
- **Eliminar al que tiene el turno:** el turno pasa al vecino según el sentido del juego.
- **Eliminar el único nodo:** la lista queda vacía (`head = None`).
- **Recorrido sin ciclo infinito:** se para cuando se vuelve al nodo de inicio (`if node is start: break`), porque nunca aparece `None`.

## 🖥️ Interfaz
- Mesa circular con los jugadores (nodos), flechas **next** (sólidas) y **prev** (punteadas).
- Etiquetas **PRIMERO** y **ÚLTIMO** para ver cómo el último se enlaza con el primero.
- Cartas de acción: Numérica, Reversa, Salta, +2 y Robar.
- Formulario para insertar jugadores al final o después de otro.
- Clic sobre un jugador para eliminarlo.
- Tabla de punteros `prev / next` de cada nodo y recorrido en ambos sentidos.
- Podio de ganadores e historial de jugadas.

## 📝 Preguntas del taller
1. ¿Por qué una mesa de UNO se modela mejor con una lista circular **doble** que con una circular simple?
2. ¿A quién apunta el `next` del último jugador? ¿Y el `prev` del primero?
3. ¿Qué punteros cambian cuando un jugador se sienta entre otros dos?
4. ¿Qué pasa con `head` y con `current` si se va el jugador que tiene el turno?
5. ¿Cómo evita `traverse()` un ciclo infinito?
6. ¿Por qué con 2 jugadores la carta Reversa funciona como Salta?
7. ¿Cuál es la complejidad de `join_player`, `eliminate_player` y `find_player`?
8. Propón una carta nueva que use el enlace `prev` de forma creativa.
