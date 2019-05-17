import sim_functions as func

dict_settings_base = {
"x":100,
"y":100,
"blob_count_init":3000,
"blob_starting_food":140,
"blob_reproduce_at":150,
"blob_reproduction_loss":35,
"blob_vision":10,
"blob_speed":1,
"blob_mass":.5,
"meat_eff":.8,
"grass_eff":.8,
"speed_cost":5,
"mass_cost":1,
"digestion_cost":10,
"sight_cost":1,
"chance_food_spawn":.05,
"food_spawn_amount":200,
"cycle_length":10,
"cycle_count":200
}



dict_settings = {
"x":100,
"y":100,
"blob_count_init":3000,
"blob_starting_food":140,
"blob_reproduce_at":150,
"blob_reproduction_loss":35,
"blob_vision":10,
"blob_speed":1,
"blob_mass":.5,
"meat_eff":.8,
"grass_eff":.8,
"speed_cost":5,
"mass_cost":1,
"digestion_cost":10,
"sight_cost":1,
"chance_food_spawn":.05,
"food_spawn_amount":200,
"cycle_length":50,
"cycle_count":200
}

#s1 = func.SimSettings(dict_settings_base)
s2 = func.SimSettings(dict_settings)

#sim = func.Simulator("blobs.sqlite",True)
sim = func.Simulator("database1/test.sqlite",True)
#sim.run(s1)
sim.run(s2)
