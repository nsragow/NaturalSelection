import sim_functions as func

dict_settings_base = {
"x":1000,
"y":1000,
"blob_count_init":2000,
"blob_starting_food":50,
"blob_reproduce_at":150,
"blob_reproduction_loss":35,
"blob_vision":2,
"blob_speed":1,
"blob_mass":10,
"meat_eff":1,
"grass_eff":.7,
"speed_cost":5,
"mass_cost":.5,
"digestion_cost":5,
"sight_cost":3,
"chance_food_spawn":.05,
"food_spawn_amount":50,
"cycle_length":10,
"cycle_count":10
}



dict_settings = {
"x":10,
"y":10,
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
"chance_food_spawn":.7,
"food_spawn_amount":200000,
"cycle_length":50,
"cycle_count":2000
}

#s1 = func.SimSettings(dict_settings_base)
s2 = func.SimSettings(dict_settings)

#sim = func.Simulator("blobs.sqlite",True)
sim = func.Simulator("longercyclebigmap.sqlite",True)
#sim.run(s1)
sim.run(s2)
