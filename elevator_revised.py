######### IMPORT ###########
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
#### Passenger class ####
########################


class Passenger(object):
    def __init__(self, start, end, arrival_time):
        passenger_count += 1
        self.id = passenger_count  # unique identifier
        self.start_floor = start
        #self.current_floor = floor
        self.in_journey = (start != 0 and end != 0) and ((
            start > 15 and end <= 15) or (start <= 15 and end > 15))
        # self.journey_started = False  # describes the current part of the journey. Either 1 or 2
        self.end = end
        self.patience_left = 15*60  # 15 minutes patience


class Elevator(object):
    def __init__(self, id, starting_floor, direction, top_floor):
        self.id = id
        self.curr_floor = starting_floor
        self.prev_floor = starting_floor
        self.stop_time = 0  # last stop time
        self.passengers = []
        self.max_capacity = 20
        self.remaining_space = self.max_capacity - len(self.passengers)
        self.direction = direction  # direction is up
        self.is_top_elevator = top_floor == 25
        self.is_broken = False  # elevator starts un-broken
        self.last_broken_time = False  # time of last break
        self.fix_time = False  # time of expected fix
        self.floors_passed_since_fix = 0  # Floors that passed since fix

    # Gets the elevator destination. Checks if it was broken until arriving
    def check_elevator_is_broken(self, dest):
        return False

    def switch_direction(self):
        self.direction *= -1

    def move_elevator(self):  # move elevator according to plan
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
######### INITIATE ###########
######### LOOP ###########
