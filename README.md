# LP Visualizer

## User Interface

### Core (MVP)

- UI is split vertically into two halves: LP model (left half) and plot (right half)
- LP model: multiple lines describing linear program
  - First line: objective function
    - Objective function in following format:
      - Objective sense: min or max can be selected from dropdown menu
      - x coefficient: number input field
      - x variable: fixed text "x"
      - Sign between terms: fixed text "+"
      - y coefficient: number input field
      - y variable: fixed text "y"
    - Examples: min 2 x + 3 y, max -1 x + 4 y
    - Optional feature: adaptive sign between terms
      - If user inputs positive y coefficient, sign between terms becomes "+" and y coefficient is kept as-is
      - If user inputs negative y coefficient, sign between terms becomes "-" and y coefficient is replaced with its absolute value
      - Example: max 5 x - 6 y instead of max 5 x + -6 y
    - Optional feature: if x coefficient is 0, grey out x variable
    - Optional feature: if y coefficient is 0, grey out y variable and sign between terms
  - All following lines: constraints
    - First constraint line starts with fixed text "s.t." followed by equation of first constraint, all other lines contain just constraints
    - All constraint equations are left-aligned following position of first constraint
    - Every constraint equation looks and functions as follows:
      - x coefficient: number input field
      - x variable: fixed text "x"
      - Sign between terms: fixed text "+"
      - y coefficient: number input field
      - y variable: fixed text "y"
      - Constraint sense: <=, >=, or = can be selected from dropdown menu
      - Right hand side: number input field
    - Examples: 10 x + 20 y <= 30, -5 x + 3 y = -2, 0 x + 1 y >= 0
    - Optional feature: button to toggle constraint on or off
      - Default: on
      - Icon: open eye (constraint is on)/closed eye (off)
      - If constraint is disabled:
        - Its text is greyed out
        - It is drawn on plot with dashed line
        - It does not affect feasible region
        - It does not affect optimal solution
    - Optional feature: button to remove constraint
      - Icon: trash bin on red background
      - On press: constraint is completely removed:
        - From list in UI
        - From LP model (backend)
        - From plot (line is removed, feasible region and optimal soltuion are updated)
    - Optional feature: adaptive sign between terms
      - Similar behavior to objective function
    - Optional feature: if x coefficient is 0, grey out x variable
    - Optional feature: if y coefficient is 0, grey out y variable and sign between terms
  - All equations are aligned vertically
    - Coefficients, variables, and signs in objective and all constraints are aligned vertically
    - x and y coefficients are right-aligned (to make alignment look nice in case of long vs short coefficients and negative vs positive coefficients)
    - Variables and signs are center aligned
    - All equations are left-aligned to right of objective sense (max/min) and leading constraint text ("s.t.")
- Plot: figure drawn with plotly and additional information text underneath
  - Constraints:
    - One solid thin straight black line for every constraint
    - Infinite lines, automatically rescale depending on plot zoom level
  - Objective vector:
    - Square box of fixed size in one of the corners of the plot
    - Fixed length arrow inside the box - rescaled objective vector, representing objective function and LP sense
  - LP solution:
    - If LP has a finite optimum, solid red circle centered at vertex achieving optimum and text "optimal value: {value}" underneath plot
    - If LP is feasible and has no finite optimum, text "unbounded" underneath plot
    - If LP is infeasible, text "infeasible" underneath plot
  - Plot is updated dynamically whenever LP model is updated
  - Optional feature: infinitely many solutions:
    - If LP has infinitely many feasible solutions, solid red circles centered at vertices achieving optimum, solid red line segments connecting them
  - Optional feature: feasible region:
    - Region filled in with semi-transparent blue color
    - Vertices solid blue circles
    - Solid blue thick line segments defining feasible region
    - If unbounded, automatically rescale infinite portion depending on plot zoom level
  - Optional feature: toggle between auto and manual re-optimization
    - Toggle auto: model re-solved on every update
    - Toggle manual: model re-solved only on button press

## Control Flow

### User Action -> Model

change sense -> update model sense
change objective coefficient -> update model objective coefficient
add constraint -> add model constraint
delete constraint -> delete model constraint
enable constraint -> enable model constraint
disable constraint -> disnable model constraint
change constraint coefficient -> update model constraint coefficient
change constraint sense -> update model constraint sense

### Model -> Plot

update model sense -> update objective vector (flip direction), update solution
update model objective coefficient -> update objective vector (change direction), update solution
add constraint -> update polyhedron (add line, update vertices, update feasible region), update solution
delete constraint -> update polyhedron (delete line, update vertices, update feasible region), update solution
enable model constraint -> update polyhedron (make line solid, update vertices, update feasible region), update solution
disable model constraint -> update polyhedron (make line dashed, update vertices, update feasible region), update solution
update model constraint coefficient -> update polyhedron (change line, update vertices, update feasible region), update solution
update model constraint sense -> update polyhedron (update feasible region), update solution
