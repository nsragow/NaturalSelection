import numpy as np

#Speed, Mass, Food type efficiency, sight
#speed_cost, mass_cost,

#when to reproduce

#asexual reproduction
food_meat = "meat"
food_grass = "grass"

speed = "speed"
mass = "mass"
efficiency = "efficiency"
sight = "sight"

last_id = 796848
def next_id():
    global last_id
    last_id += 1
    return last_id





class Space():
    def __init__(self):
        self.food = 0
        self.occupants = {}
    def add_blob(self,blob):
        self.occupants[blob.id] = blob
    def add_food(self,food):
        self.food += food

#tweakable food spawn
class Board():
    def __init__(self,blobs,map,food_func,can_eat_func,mutate_func,costs):
        self.blobs = {}
        for blob in blobs:
            self.blobs[blob.id] = blob
        self.blobs_existed = set(blobs)
        self.food_func = food_func
        self.map = map
        self.costs = costs
        self.x_len = len(map)
        self.y_len = len(map[0])
        self.mutate_func = mutate_func
        self.can_eat_func = can_eat_func
        self.place_blobs()
    def step(self):
        self.add_food()
        self.eat()
        self.move()
        self.tire()
        self.reproduce()
        self.clean_up_dead()
    def place_blobs(self):
        for blob in self.blobs.values():
            x = np.random.randint(len(self.map))
            y = np.random.randint(len(self.map[0]))
            blob.set_pos((x,y))
            self.map[x][y].add_blob(blob)
    def add_food(self):
        for x in range(self.x_len):
            for y in range(self.y_len):
                if self.map[x][y].food < 1:
                    self.map[x][y].food = self.food_func()
    def eat(self):
        for x in range(self.x_len):
            for y in range(self.y_len):
                occupancy = len(self.map[x][y].occupants.keys())
                if occupancy > 0:

                    occupants_sorted = list(sorted(self.map[x][y].occupants.values(),key=lambda blob : blob.mass,reverse=True))
                    while eat_occurs(occupants_sorted,self.can_eat_func):
                        occupants_sorted = simulate_eat(occupants_sorted,self.blobs)
                    self.map[x][y].occupants = {}
                    for blob in occupants_sorted:
                        self.map[x][y].occupants[blob.id] = blob
                    #at this point all the blobicide is finished, now plant eating will take place
                    food_count = self.map[x][y].food/len(self.map[x][y].occupants.keys())
                    for blob in self.map[x][y].occupants.values():
                        global food_grass
                        blob.eat(food_count,food_grass)
                    self.map[x][y].food = 0
    def move(self):
        for blob in self.blobs.values():
            current_space = self.map[blob.pos[0]][blob.pos[1]]
            new_pos = where_will_he_move(blob,self.map,self.can_eat_func)
            if new_pos is None:
                print("Hi")
            blob.pos = new_pos
            destination_space = self.map[blob.pos[0]][blob.pos[1]]
            del current_space.occupants[blob.id]
            destination_space.occupants[blob.id] = blob

    def tire(self):
        global speed
        global mass
        global efficiency
        global sight
        for blob in self.blobs.values():
            blob.exaust(self.costs[speed],
                        self.costs[mass],
                        self.costs[efficiency],
                        self.costs[sight])
    def reproduce(self):
        marked_to_add = []
        for blob in self.blobs.values():
            if blob.will_reproduce():
                new_blob = blob.reproduce(self.mutate_func)
                destination_space = self.map[new_blob.pos[0]][new_blob.pos[1]]
                destination_space.occupants[new_blob.id] = new_blob
                self.blobs_existed.add(new_blob)
                marked_to_add.append(new_blob)
        for blob in marked_to_add:
            self.blobs[blob.id] = blob
    def clean_up_dead(self):
        marked = []
        for blob in self.blobs.values():
            if blob.food < 0:
                del self.map[blob.pos[0]][blob.pos[1]].occupants[blob.id]
                marked.append(blob.id)
        for mark in marked:
            del self.blobs[mark]


class Blob():
    def __init__(self,food_init,reproduce_at,reproduction_loss,vision,speed,mass,food_efficiencies):
        self.id = next_id()
        self.food = food_init
        self.reproduce_at = reproduce_at
        self.reproduction_loss = reproduction_loss
        self.vision = vision
        self.speed = speed
        self.mass = mass
        self.food_efficiencies = food_efficiencies
        self.lifetimes = {"grass":0,"meat":0,"grass_meals":0,"meat_meals":0,"reproduction":0}
    def set_pos(self,pos):
        self.pos = pos
        return self
    def will_reproduce(self):
        return self.reproduce_at <= self.food
    def reproduce(self,mutate):
        self.food = (self.food - self.reproduction_loss)/2
        new_efficiencies = {}
        for key in self.food_efficiencies.keys():
            new_efficiencies[key] = mutate(self.food_efficiencies[key])
        self.lifetimes["reproduction"]+=1
        return Blob(self.food,
                    mutate(self.reproduce_at),
                    self.reproduction_loss,
                    max(mutate(self.vision),1),
                    mutate(self.speed),
                    mutate(self.mass),new_efficiencies).set_pos(self.pos)
    def eat(self,food_count,food_type):
        self.lifetimes[food_type]+=self.food_efficiencies[food_type]*food_count
        self.lifetimes[f"{food_type}_meals"]+=1
        self.food += self.food_efficiencies[food_type]*food_count
    def exaust(self,speed_cost,mass_cost,efficiency_cost,sight_cost):
        self.food -= (speed_cost(self.speed) +
                        mass_cost(self.mass) +
                        sight_cost(self.vision))
        for eff in self.food_efficiencies.values():
            self.food -= efficiency_cost(eff)
def eat_occurs(occupants_sorted,can_eat_func):
    for pair in [(x,y) for x in occupants_sorted for y in occupants_sorted if x is not y]:
        if can_eat_func(pair[0],pair[1]):
            return True
    return False
def simulate_eat(occupants_sorted,blob_dict):
    eater = occupants_sorted[0]
    eaten = occupants_sorted[-1]
    global food_meat
    eater.eat(eaten.food,food_meat)
    del blob_dict[eaten.id]
    return occupants_sorted[:-1]
def where_will_he_move(blob,map,can_eat_func):

    desired_pos = (-1,-1)

    pos = blob.pos
    vision = blob.vision

    up = [(blob.pos[0],blob.pos[1]+offset) for offset in range(1,int(blob.vision)+1) if blob.pos[1]+offset<len(map[0])]
    down = [(blob.pos[0],blob.pos[1]-offset) for offset in range(1,int(blob.vision)+1) if blob.pos[1]-offset>=0]
    right = [(blob.pos[0]+offset,blob.pos[1]) for offset in range(1,int(blob.vision)+1) if blob.pos[0]+offset<len(map)]
    left = [(blob.pos[0]-offset,blob.pos[1]) for offset in range(1,int(blob.vision)+1) if blob.pos[0]-offset>=0]
    all_pos = up+down+right+left
    all_pos = list(set(all_pos))
    #if len(all_pos) == 0:

    have_food = {}
    for p in all_pos:
        if food_count(blob,map[p[0]][p[1]],can_eat_func)>0:
            have_food[p] = abs(pos[0] - p[0]) + abs(pos[1] - p[1])
    if len(have_food.values()) > 0:
        closest = min(have_food.values())
        last_check = []
        for key in have_food.keys():
            if have_food[key] == closest:
                last_check.append(key)
        desired_pos = list(sorted(last_check,key=lambda p : food_count(blob,map[p[0]][p[1]],can_eat_func),reverse=True))[0]
    else:
        desired_pos = all_pos[np.random.randint(len(all_pos))]

    x_move = desired_pos[0] - pos[0]
    y_move = desired_pos[1] - pos[1]

    if abs(x_move) + abs(y_move) <= blob.speed:
        return desired_pos
    else:
        if x_move != 0:
            if x_move > 0:
                return (pos[0]+int(blob.speed),pos[1])
            else:
                return (pos[0]-int(blob.speed),pos[1])
        else:
            if y_move > 0:
                return (pos[0],pos[1]+int(blob.speed))
            else:
                return (pos[0],pos[1]-int(blob.speed))

def food_count(blob,space,can_eat_func):
    total_food = space.food/(len(space.occupants.keys())+1)
    for other_blob in space.occupants.values():
        if can_eat_func(blob,other_blob):
            total_food+=other_blob.food
    return total_food
