#first simulation was a sham


import creatures as c
import random as r
import numpy as np
import SQLPanda as spd


x = 1000
y = 1000
blob_count_init = 2000
blob_starting_food = 50
blob_reproduce_at = 150
blob_reproduction_loss = 35
blob_vision = 2
blob_speed = 1
blob_mass = 10
meat_eff = 1
grass_eff = .7
init_efficiencies = {c.food_meat : meat_eff, c.food_grass : grass_eff}

speed_cost = 5
mass_cost = .5
efficiency_cost = 5
sight_cost = 3
func1 = (lambda x : x*speed_cost)
func2 = (lambda x : x*mass_cost)
func3 = (lambda x : x*efficiency_cost)
func4 = (lambda x : x*sight_cost)
costs = {c.speed : func1, c.mass : func2, c.efficiency : func3, c.sight : func4}


chance_food_spawn = .05
food_spawn = 50

map = []

for i in range(x):
    col = []
    for j in range(y):
        col.append(c.Space())
    map.append(col)

blobs = []
for i in range(blob_count_init):
    blobs.append(c.Blob(blob_starting_food,
                        blob_reproduce_at,
                        blob_reproduction_loss,
                        blob_vision,
                        blob_speed,
                        blob_mass,
                        init_efficiencies))
def food_func():
    global chance_food_spawn
    global r
    if r.random() <= chance_food_spawn:
        return food_spawn
    else:
        return 0
def mutate_func(to_mutate):
    mutate_factor = np.random.random_sample()*2
    return mutate_factor*to_mutate
def can_eat_func(blob,target_blob):
    return blob.mass > target_blob.mass*2




board = c.Board(blobs,map,food_func,can_eat_func,mutate_func,costs)
print("board_init")
df = spd.load("blobs.sqlite")

df.q(f"""
insert into simulations(
starting_blob_count,
x_dimension_map,
y_dimension_map,
blob_starting_food,
blob_start_reproduce_at,
blob_reproduction_loss,
blob_start_vision,
blob_start_speed,
blob_start_mass,
blob_start_meat_eff,
blob_start_grass_eff,
speed_cost,
mass_cost,
digestion_cost,
sight_cost,
chance_food_spawn,
food_spawn_amount
)
values (
{blob_count_init},
{x},
{y},
{blob_starting_food},
{blob_reproduce_at},
{blob_reproduction_loss},
{blob_vision},
{blob_speed},
{blob_mass},
{meat_eff},
{grass_eff},
{speed_cost},
{mass_cost},
{efficiency_cost},
{sight_cost},
{chance_food_spawn},
{food_spawn}
)
""")
df.q("""
create table blobs_alive(
id integer not null,
blob_id int not null,
sim_step int not null,
sim_id int not null,
meat_lifetime real not null,
grass_lifetime real not null,
reproduction_lifetime real not null,
primary key (id)
)
""")
df.q("""
create table blobs(
id int primary key,
reproduce_at real not null,
vision real not null,
speed real not null,
mass real not null,
meat_eff real not null,
grass_eff real not null
)
""")
for i in range(10):
    print(f"starting {i}")
    for j in range(10):
        board.step()
    print("fin steps")
    print(f"population {len(board.blobs.values())}")
    for blob in board.blobs.values():
        df.q(f"""
        insert into blobs_alive(blob_id,sim_step,sim_id)
        values
        ({blob.id},{10+i*10},1)
        """)
    df.q("commit")
for blob in board.blobs_existed:
    df.q(f"""
    insert into blobs(
    id,
    reproduce_at,
    vision,
    speed,
    mass,
    meat_eff,
    grass_eff
    )
    Values
    (
    {blob.id},
    {blob.reproduce_at},
    {blob.vision},
    {blob.speed},
    {blob.mass},
    {blob.food_efficiencies["meat"]},
    {blob.food_efficiencies["grass"]}
    )
    """)
df.q("commit")


print(len(board.blobs))
