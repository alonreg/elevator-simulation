######### IMPORT ###########
from collections import deque
import random
import pandas as pd  # package for some uses and maybe for visualization
import numpy as np
import heapq
from matplotlib.pylab import plot, show, bar
import matplotlib.pyplot as plt
plt.style.use("ggplot")
df = pd.read_csv('arrival_rates.csv')
df  # TODO: what is this?
floors_num = 25
arrival_rates_by_floor_section = [
    [18, 10.8, 40.8], [50, 6.8, 12.8], [11, 4.8, 7.8]]
arrival_rates = [
    [[], []],
    [[], [], []],
    [[], [], []]
]
k = -1
for i in range(3):
    for j in range(len(arrival_rates[i])):
        k += 1
        if k == 8:
            break
        opc = [df.loc[k, "other"], df.loc[k, "15--18"], df.loc[k, "7--10"]]
        arrival_rates[i][j].extend(opc)
arrival_rates[0].insert(0, None)
np.random.seed(0)
# Creating a dictionary with the range of each floor
# the range ressembles the location in the rate array
lower_floor_range = {floor: 1 for floor in range(1, 16)}
upper_floor_range = {floor: 2 for floor in range(16, 26)}
lower_floor_range.update(upper_floor_range)
floor_range = lower_floor_range
floor_range[0] = 0  # ground floor


######### CLASS ###########
class Event():
    def __init__(self, time, eventType, passenger=-1, elevator=-1):
        self.time = time  # event time
        self.eventType = eventType  # type of the event
        self.passenger = passenger
        self.elevator = elevator
        heapq.heappush(P, self)  # add the event to the events list

    def __lt__(self, event2):
        return self.time < event2.time

########################
#### Passenger class ###
########################


class Passenger(object):
    def __init__(self, start, end, arrival_time):
        self.id = passenger_count  # unique identifier
        self.start = start
        self.end = end
        self.arrival_time = arrival_time  # time of first arrival
        #self.current_floor = floor
        self.in_journey = (start != 0 and end != 0) and ((
            start > 15 and end <= 15) or (start <= 15 and end > 15))
        # self.journey_started = False  # describes the current part of the journey. Either 1 or 2
        self.patience_left = 15*60  # 15 minutes patience
        self.left = False
        if end > start:
            self.direction = -1
        else:
            self.direction = 1


class Elevator(object):
    def __init__(self, id, starting_floor, direction, top_floor):
        self.id = id
        self.curr_floor = starting_floor
        self.prev_floor = starting_floor
        self.stop_time = 0  # last stop time
        self.passengers = []
        self.max_capacity = 20
        self.remaining_space = self.max_capacity - len(self.passengers)
        self.direction = direction  # up / down
        self.is_top_elevator = top_floor == 25
        self.top_floor = top_floor
        if top_floor == 15:
            self.min_floor = 1  # lowest floor in section
        else:
            self.min_floor = 16  # lowest floor in section
        self.is_broken = False  # elevator starts un-broken
        self.last_broken_time = -1  # time of last break

    # Gets the elevator destination. Checks if it was broken until arriving

    def move(self):
        self.stop_time = curr_time - 5  # last stopped before 5 sec
        self.prev_floor = self.curr_floor
        if self.is_top_elevator:
            if self.curr_floor == 16 and self.direction == -1:
                self.curr_floor -= 16  # move the elevator past sector #1
            elif self.curr_floor == 0 and self.direction == 1:
                self.curr_floor += 16  # move the elevator past sector #1
        else:
            self.curr_floor += self.direction
        if (self.curr_floor == 0 and self.direction == -1) or (self.curr_floor in [15, 25] and self.direction == 1):
            # if reached end of section, flip direction
            self.direction *= -1

    def did_break(self):
        rnd = np.random.random()
        if rnd < 0.0005:
            self.is_broken = True
            self.last_broken_time = curr_time
            return True
        self.is_broken = False
        return False

    def switch_direction(self):
        self.direction *= -1

    # removes leaving passengers and
    def release_passengers(self):
        journey_passengers = []
        if self.curr_floor == 0:
            # journey passengers are saved in the system
            journey_passengers = list(
                [p for p in self.passengers if p.in_journey])
            self.passengers = list(
                [p for p in self.passengers if self.curr_floor != p.end and not p.in_journey])
        else:
            # create new passengers list with all the passengers that stay
            self.passengers = list(
                [p for p in self.passengers if self.curr_floor != p.end])
        return journey_passengers

     # removes leaving passengers and
    def release_when_broken(self, direction):
        released = list(
            [p for p in self.passengers if self.direction == direction])
        self.passengers = list(
            [p for p in self.passengers if self.curr_floor != p.end])
        return released


### TODO DELETE: ###

    def move_elevator(self, floor):  # move elevator according to plan
        self.stop_time = curr_time
        # if elevator hasn't been moven, return
        if self.curr_floor == floor:
            return
        self.prev_floor = self.curr_floor
        self.curr_floor = floor
        if self.direction > 0:
            if self.prev_floor > self.curr_floor:
                self.direction *= -1
        else:
            if self.prev_floor < self.curr_floor:
                self.direction *= -1

    def get_arrival_time(self, floor_stop, end):
        top_floor = 25 if self.is_top_elevator else 15
        if floor_stop > end:
            # passenger going down
            if self.direction == -1:
                # both elevator and passenger are going down
                if self.curr_floor > floor_stop:
                    # the elevator is passing by this passenger
                    arrival_time = self.stop_time + \
                        get_travel_time(self.curr_floor, end)
                else:
                    # the elevator isnt passing by this passenger
                    arrival_time = self.stop_time + \
                        get_travel_time(self.curr_floor, 0) + get_travel_time(0,
                                                                              top_floor) + get_travel_time(top_floor, end)
            else:
                # elevator is going up, passenger is going down
                arrival_time = self.stop_time + \
                    get_travel_time(self.curr_floor, top_floor) + \
                    get_travel_time(top_floor, end)
        else:
            # passenger going up
            if self.direction == -1:
                # passenger is going up, elevator is going down
                arrival_time = self.stop_time + \
                    get_travel_time(self.curr_floor, 0) + \
                    get_travel_time(0, end)
            else:
                # passenger is going up, elevator is going up
                if self.curr_floor > floor_stop:
                    # is not passing by passenger
                    arrival_time = self.stop_time + \
                        get_travel_time(self.curr_floor, top_floor) + \
                        get_travel_time(top_floor, 0) + get_travel_time(0, end)
                else:
                    arrival_time = self.stop_time + \
                        get_travel_time(self.curr_floor, end)

        return arrival_time  # return the elevator and time


######### FUNCTION ###########

## returns current rate ##
##########################
def get_current_rate_by_floor(start_floor, end_floor):
    # get current arrival rate according to start floor,
    # destination, (or section) and curr_time(which would be determined
    # at the start of each While iteration)
    start_floor_section = floor_range[start_floor]
    end_floor_section = floor_range[end_floor]
    if curr_time >= 60 and curr_time < 4*60:
        # 07:00-10:00
        hour_range = 2
    elif curr_time >= 9*60 and curr_time < 12*60:
        # 15:00-18:00
        hour_range = 1
    else:
        # any other time
        hour_range = 0

    rate = arrival_rates[start_floor_section][end_floor_section][hour_range]
    # Convert to exponential rate
    return 60/rate

# returns a random destination in the same section


def get_rand_dest(end):
    if end == 0:
        return 0
    elif end > 15:
        return np.random.randint(16, 26)
    else:
        return np.random.randint(1, 16)


def get_travel_time(floors):
    start = 2
    stop = 2
    wait = 5
    pass_by = 1
    return floors * pass_by + start + stop + wait


######### INITIATE ###########
# initialize simulation
curr_time = 0  # current time
SIM_TIME = 14*60  # simulation time in minutes

P = []  # heap
L_up = [[]]*26  # going up line in every floor
L_down = [[]]*26  # going down line in every floor
passenger_count = 0

##### Create the Elevators #####
##### Lower-floors elevator ####
elevator1 = Elevator("Elevator1", 0, 1, False)
elevator2 = Elevator("Elevator2", 0, 1, False)
#### Higher-floors elevator ####
elevator3 = Elevator("Elevator3", 0, 1, True)
elevator4 = Elevator("Elevator4", 0, 1, True)

elevators = [Elevator(id=1, starting_floor=0, direction=1, top_floor=15), Elevator(id=2, starting_floor=0, direction=1, top_floor=15), Elevator(
    id=3, starting_floor=0, direction=1, top_floor=25), Elevator(id=4, starting_floor=0, direction=1, top_floor=25)]

for start in range(0, 26):
    for segment in [0, 15, 25]:
        if start + segment == 0:
            continue
        time = np.random.exponential(get_current_rate_by_floor(start, segment))
        end = get_rand_dest(segment)
        new_passenger = Passenger(start, end, time)
        Event(time, "arriving", passenger=new_passenger)

for elevator in elevators:
    Event(curr_time + 5, "elevator_close", elevator=elevator)

######### LOOP ###########
while curr_time < SIM_TIME:  # loop until sim time ends

    event = heapq.heappop(P)  # get next event
    prev_time = curr_time  # time of last event
    curr_time = event.time  # current event's time

    ## arriving ##
    if event.eventType == "arriving":
        passenger = event.passenger
        # insert passenger to floor line
        if passenger.direction == 1:
            heapq.heappush(L_up[passenger.start],
                           (passenger.arrival_time, id(passenger), passenger))
        else:
            heapq.heappush(L_down[passenger.start],
                           (passenger.arrival_time, id(passenger), passenger))
        # check if he will be out of patience
        Event(curr_time + 15*60, "out_of_patience", passenger)
        # generate next passenger
        rate = get_current_rate_by_floor(passenger.start, passenger.end)
        new_time = curr_time + np.random.exponential(rate)
        new_passenger_end = get_rand_dest(passenger.end)
        new_passenger = Passenger(passenger.start, new_passenger_end, new_time)
        Event(new_time, "arriving", passenger=new_passenger)
        # TODO you can also flip the order and create the passenger on event
    ##############

    ## elevator_close ##
    elif event.eventType == "elevator_close":
        elevator = event.elevator
        did_break = elevator.did_break()
        # passengers with this destination are free to go, returns journey passengers in floor 0
        journey_passengers = elevator.release_passengers()
        if elevator.curr_floor == 0:
            # if in floor 0, add journey passengers to queue
            for j_passenger in journey_passengers:
                # add journey passengers back to the line
                # they always go up if in middle of journey
                print(curr_time)
                print(type(curr_time))
                heapq.heappush(L_up[elevator.curr_floor],
                               (curr_time - 5, id(j_passenger), j_passenger))
        for other_elevator in elevators:
            if other_elevator != elevator and other_elevator.top_floor == elevator.top_floor:
                if other_elevator.is_broken and other_elevator.curr_floor == elevator.curr_floor and other_elevator.direction == elevator.direction:
                    # other elevator is stuck right now on same floor and with same direction
                    # and also the current elevator didnt break
                    # therefore we will take any passenger we can with us
                    released_from_broken = other_elevator.release_when_broken(
                        elevator.direction)

                    for p in released_from_broken:
                        if elevator.remaining_space > 0:
                            # both are going in the same direction
                            # passenger enters the elevator
                            # appends randomly
                            # TODO change to do this by order
                            elevator.passengers.append(p)
        if did_break:
            # handle elevator broken
            print(" elevator has broken ")
            fix_time = curr_time + np.random.randint(5, 16) * 60
            Event(fix_time, "elevator_close", elevator=elevator)
            # TODO TODO TODO make the passengers return to line to be first in line

            # if elevator is stuck, it won't be moving
        else:
            if elevator.direction == 1:
                waiting_passengers = L_up[elevator.curr_floor]
            else:
                waiting_passengers = L_down[elevator.curr_floor]

            while waiting_passengers:
                if elevator.remaining_space > 0:
                    # both are going in the same direction
                    # passenger enters the elevator
                    next_in_line = heapq.heappop(waiting_passengers)[2]
                    elevator.passengers.append(next_in_line)
                else:
                    break  # stop inserting passengers to elevator, no room or no more passengers
            if (elevator.curr_floor == 16 and elevator.direction == -1) or (elevator.curr_floor == 0 and elevator.direction == 1 and elevator.is_top_elevator):
                next_time = curr_time + get_travel_time(floors=16)
                print("time from floor zero to floor 16 is:" +
                      str(get_travel_time(floors=16)))
            else:
                next_time = curr_time + get_travel_time(floors=1)
            # if not broken, move as scheduled to next floor
            Event(next_time, "elevator_close", elevator=elevator)
            elevator.move()  # moves elevator to next floor + open + close doors

        ##############

        ## arriving ##
    # elif event.eventType == "elevator_fixed":
    #    pass
    ##############

    ## out_of_patience ##
    elif event.eventType == "out_of_patience":
        passenger = event.passenger
        if passenger.left is False:
            passenger.left = True
            # will always be next passenger
            if passenger.direction == 1:
                heapq.heappop(L_up[passenger.curr_floor])
            else:
                heapq.heappop(L_down[passenger.curr_floor])
            # L[passenger.curr_floor].remove((passenger))
            # heapq.heappush(L[passenger.curr_floor],
            #                  (curr_time - 5, j_passenger))

            # TODO num_leavers[movie] += 1
            # theater.L -=1
            # people_in.append(theater.L)
            # time.append(curr_time)
        ##############

# gal explains how to התפלגות משך שירות
# https://moodle.tau.ac.il/mod/forum/discuss.php?d=29815
