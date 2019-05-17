#should let creatures scavenge for dead bodies

import creatures as c
import SQLPanda as spd
import random as r
import numpy as np

class SimSettings():
    def __init__(self,from_dict={}):
        self.settings = from_dict
        if from_dict.keys().__len__() == 0:
            self.settings["x"] = None
            self.settings["y"] = None
            self.settings["blob_count_init"] = None
            self.settings["blob_starting_food"] = None
            self.settings["blob_reproduce_at"] = None
            self.settings["blob_reproduction_loss"] = None
            self.settings["blob_vision"] = None
            self.settings["blob_speed"] = None
            self.settings["blob_mass"] = None
            self.settings["meat_eff"] = None
            self.settings["grass_eff"] = None
            self.settings["speed_cost"] = None
            self.settings["mass_cost"] = None
            self.settings["digestion_cost"] = None
            self.settings["sight_cost"] = None
            self.settings["chance_food_spawn"] = None
            self.settings["food_spawn_amount"] = None
            self.settings["cycle_length"] = 10
            self.settings["cycle_count"] = 10
    def sim_settings_ready(self):
        return self.missing_settings().__len__()==0
    def missing_settings(self):
        missing = []
        for key in self.settings.keys():
            if self.settings[key] is None:
                missing.append(key)
        return missing
    def duration(self,
                cycle_length=None,
                cycle_count=None):
        if cycle_length is None:
            cycle_length=self.settings["cycle_length"]
        if cycle_count is None:
            cycle_count=self.settings["cycle_count"]
        self.settings["cycle_length"] = cycle_length
        self.settings["cycle_count"] = cycle_count
        return self
    def map(self,
            x = None,
            y = None,
            chance_food_spawn = None,
            food_spawn_amount = None):
        if x is None:
            x = self.settings["x"]
        if y is None:
            y = self.settings["y"]
        if chance_food_spawn is None:
            chance_food_spawn = self.settings["chance_food_spawn"]
        if food_spawn_amount is None:
            food_spawn_amount = self.settings["food_spawn_amount"]
        self.settings["x"] = x
        self.settings["y"] = y
        self.settings["chance_food_spawn"] = chance_food_spawn
        self.settings["food_spawn_amount"] = food_spawn_amount
        return self
    def blob(self,
            food_start=None,
            reproduce_at=None,
            reproduction_loss=None,
            vision=None,
            speed=None,
            mass=None,
            meat_eff=None,
            grass_eff=None):

        if food_start is None:
            food_start = self.settings["blob_starting_food"]
        if reproduce_at is None:
            reproduce_at = self.settings["blob_reproduce_at"]
        if reproduction_loss is None:
            reproduction_loss = self.settings["blob_reproduction_loss"]
        if vision is None:
            vision = self.settings["blob_vision"]
        if speed is None:
            speed = self.settings["blob_speed"]
        if mass is None:
            mass = self.settings["blob_mass"]
        if meat_eff is None:
            meat_eff = self.settings["meat_eff"]
        if grass_eff is None:
            grass_eff = self.settings["grass_eff"]

        self.settings["blob_starting_food"] = food_start
        self.settings["blob_reproduce_at"] = reproduce_at
        self.settings["blob_reproduction_loss"] = reproduction_loss
        self.settings["blob_vision"] = vision
        self.settings["blob_speed"] = speed
        self.settings["blob_mass"] = mass
        self.settings["meat_eff"] = meat_eff
        self.settings["grass_eff"] = grass_eff
        return self
    def costs(self,
                speed = None,
                mass = None,
                digestion = None,
                sight = None):
        if speed is None:
            speed = self.settings["speed_cost"]
        if mass is None:
            mass = self.settings["mass_cost"]
        if digestion is None:
            digestion = self.settings["digestion_cost"]
        if sight is None:
            sight = self.settings["sight_cost"]
        self.settings["speed_cost"] = speed
        self.settings["mass_cost"] = mass
        self.settings["digestion_cost"] = digestion
        self.settings["sight_cost"] = sight
        return self
class Simulator():
    _simulations_ = "simulations"
    _blobs_alive_ = "blobs_alive"
    _blobs_ = "blobs"

    def __init__(self,file,create_new_database=False):
        self.df = spd.lite_load(file)
        if create_new_database:
            self.create_tables()
    def create_tables(self):
        global create_blobs_table
        global create_blobs_alive_table
        global create_simulations_table
        self.df.q(create_blobs_table)
        self.df.q(create_blobs_alive_table)
        self.df.commit(create_simulations_table)
    def run(self,sim_settings):
        last_sim = self.df.q("select max(id) from simulations").loc[0,"max(id)"]
        sim_number = last_sim
        if last_sim is None:
            sim_number = 0
        sim_number += 1

        s = sim_settings.settings
        if not sim_settings.sim_settings_ready():
            print(f"""
            Sim settings missing {sim_settings.missing_settings()}.
            Simulation aborted.
            """)
            return
        init_efficiencies = {c.food_meat : s["meat_eff"], c.food_grass : s["grass_eff"]}
        costs = {
            c.speed : lambda x : x*s["speed_cost"],
            c.mass : lambda x : x*s["mass_cost"],
            c.efficiency : lambda x : s["digestion_cost"]**x + (s["digestion_cost"]/1000)**(x*3)+x**s["digestion_cost"] + x**(s["digestion_cost"]*s["digestion_cost"]*s["digestion_cost"]),
            c.sight : lambda x : x*s["sight_cost"]
        }
        self.map_init(s)
        self.blobs_init(s,init_efficiencies)
        self.board_init(s,costs)
        self.df.q(simulations_insert.format(
                                        s["blob_count_init"],
                                        s["x"],
                                        s["y"],
                                        s["blob_starting_food"],
                                        s["blob_reproduce_at"],
                                        s["blob_reproduction_loss"],
                                        s["blob_vision"],
                                        s["blob_speed"],
                                        s["blob_mass"],
                                        s["meat_eff"],
                                        s["grass_eff"],
                                        s["speed_cost"],
                                        s["mass_cost"],
                                        s["digestion_cost"],
                                        s["sight_cost"],
                                        s["chance_food_spawn"],
                                        s["food_spawn_amount"],
                                        s["cycle_length"],
                                        s['cycle_count']))
        for i in range(s["cycle_count"]):
            try:
                #print(f"starting cycle {i}")
                for j in range(s["cycle_length"]):
                    self.board.step()
                #print("fin steps")
                pop_count = len(self.board.blobs.values())
                print(f"population {pop_count},    cycle {i}")
                if pop_count == 0:
                    print("Simulation ending due to death of population")
                    break
                for blob in self.board.blobs.values():
                    self.df.q(f"""
                    insert into blobs_alive(blob_id,
                    sim_step,
                    sim_id,
                    meat_lifetime,
                    grass_lifetime,
                    reproduction_lifetime,
                    grass_meals_lifetime,
                    meat_meals_lifetime)
                    values
                    ({blob.id},{10+i*10},{sim_number},{blob.lifetimes["meat"]},{blob.lifetimes["grass"]},{blob.lifetimes["reproduction"]},{blob.lifetimes["grass_meals"]},{blob.lifetimes["meat_meals"]})
                    """)
                self.df.q("commit")
                if pop_count > 50000:
                    print("Simulation ending due to population explosion")
                    break
            except KeyboardInterrupt:
                print('Interrupted, commiting all existing to table')
                break
        for blob in self.board.blobs_existed:
            self.df.q(f"""
            insert into blobs(
            id,
            sim_id,
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
            {sim_number},
            {blob.reproduce_at},
            {blob.vision},
            {blob.speed},
            {blob.mass},
            {blob.food_efficiencies["meat"]},
            {blob.food_efficiencies["grass"]}
            )
            """)
        self.df.q("commit")


    def board_init(self,settings,costs):
        self.board = c.Board(self.blobs,self.map,lambda:food_func(settings['chance_food_spawn'],settings["food_spawn_amount"]),can_eat_func,mutate_func,costs)
    def map_init(self, settings):
        self.map = []
        for i in range(settings["x"]):
            col = []
            for j in range(settings["y"]):
                col.append(c.Space())
            self.map.append(col)
    def blobs_init(self, settings, init_efficiencies):
        s = settings
        self.blobs = []
        for i in range(s["blob_count_init"]):
            self.blobs.append(c.Blob(
                                s["blob_starting_food"],
                                s["blob_reproduce_at"],
                                s["blob_reproduction_loss"],
                                s["blob_vision"],
                                s["blob_speed"],
                                s["blob_mass"],
                                init_efficiencies))










def food_func(chance_food_spawn,food_spawn):
    if r.random() <= chance_food_spawn:
        return food_spawn
    else:
        return 0

def mutate_func(to_mutate):
    mutate_factor = np.random.random_sample()*2
    return mutate_factor*to_mutate

def can_eat_func(blob,target_blob):
    return blob.mass > target_blob.mass*2








create_simulations_table = """
create table simulations(
id integer not null,
starting_blob_count int not null,
x_dimension_map int not null,
y_dimension_map int not null,
blob_starting_food int not null,
blob_start_reproduce_at int not null,
blob_reproduction_loss int not null,
blob_start_vision int not null,
blob_start_speed int not null,
blob_start_mass int not null,
blob_start_meat_eff real not null,
blob_start_grass_eff real not null,
speed_cost real not null,
mass_cost real not null,
digestion_cost real not null,
sight_cost real not null,
chance_food_spawn real not null,
food_spawn_amount int not null,
cycle_length int not null,
cycle_count int not null,
primary key (id)
)
"""
create_blobs_alive_table = """
create table blobs_alive(
id integer not null,
blob_id int not null,
sim_step int not null,
sim_id int not null,
meat_lifetime real not null,
grass_lifetime real not null,
reproduction_lifetime real not null,
grass_meals_lifetime int not null,
meat_meals_lifetime int not null,
primary key (id)
)
"""
create_blobs_table = """
create table blobs(
id int not null,
sim_id int not null,
reproduce_at real not null,
vision real not null,
speed real not null,
mass real not null,
meat_eff real not null,
grass_eff real not null,
primary key(id,sim_id)
)
"""
simulations_insert = """
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
food_spawn_amount,
cycle_length,
cycle_count
)
values (
{},
{},
{},
{},
{},
{},
{},
{},
{},
{},
{},
{},
{},
{},
{},
{},
{},
{},
{}
)
"""
