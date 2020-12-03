# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

import pandas as pd  # package for some uses and maybe for visualization
import random
import numpy as np
import heapq
from pylab import plot, show, bar
import matplotlib.pyplot as plt
plt.style.use("ggplot")

#####################################################
##### initiating arrival rates array, from csv ######
#####################################################
df = pd.read_csv('arrival_rates.csv')
df  # TODO: what is this?

floors = 25

# TODO: Maxim - Please pull this data from the csv instead of manual input
# this represents the total number of people incoming in every hour in every section
#  data structure: [ other times: [floors: 0, 1-15, 15+], 15--18: [0, 1-15, 15+], 7--10: [0, 1-15, 15+]]
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

np.random.seed(0)  # set the seed for the random numbers
# TODO: perhaps change to other-to-other to zeros instead of none
print(arrival_rates)


########################################################
## Creating a dictionary with the range of each floor ##
# the range ressembles the location in the rate array ##
########################################################
lower_floor_range = {floor: 1 for floor in range(1, 16)}
upper_floor_range = {floor: 2 for floor in range(16, 26)}
lower_floor_range.update(upper_floor_range)
floor_range = lower_floor_range
floor_range[0] = 0  # ground floor

print(floor_range)

#######################################################################################
#######################################################################################
#######################################################################################
########################
##### Event class ######
########################


class Event():
    def __init__(self, time, eventType, passenger=-1):
        self.time = time  # event time
        self.eventType = eventType  # type of the event
        self.passenger = passenger
        heapq.heappush(P, self)  # add the event to the events list

    def __lt__(self, event2):
        return self.time < event2.time

########################
#### Passenger class ####
########################


class Passenger(object):
    def __init__(self, start_floor, destination, arrival_time, id, is_traveler):
        self.start_floor = start_floor
        self.current_floor = start_floor  # TODO is it needed?
        self.is_traveler = is_traveler  # if passenger
        self.current_leg = 1  # describes the current part of the journey. Either 1 or 2
        self.destination = destination
        self.elevator = -1  # waits before entering elevator
        self.patience = 15
        self.arrival_time = arrival_time
        self.id = id  # unique identifier

    # TODO CHANGE THAT LATER SO IT WILL USE THE floor_range DICTIONARY
    def is_elevator_exchange_needed(self):
        # checks if start_floor and destination are in the same floor range
        # TODO: why use 2 methods?
        if (self.start_floor <= 15 and self.destination <= 15) or (self.start_floor in [0]+list(range(16, 26)) and self.destination in [0]+list(range(16, 26))):
            return False
        else:
            return True

########################
#### Elevator class ####
########################


class Elevator(object):
    def __init__(self, name, starting_floor):
        self.name = name
        self.current_floor = starting_floor
        self.previous_floor = previous_floor
        self.passengers = []
        self.max_capacity = 15
        self.remaining_space = self.max_capacity - len(self.passengers)


########################
## Low-Elevator class ##
########################
class Lower_floors_Elevator(Elevator):
    def __init__(self, name, current_floor):
        Elevator.__init__(self, name, current_floor)
        Elevator.floor_range = range(16)

#########################
## High-Elevator class ##
#########################


class Upper_floors_Elevator(Elevator):
    def __init__(self, name, current_floor):
        # TODO: perhaps use super()
        Elevator.__init__(self, name, current_floor)
        # TODO: changed from self. to elevator.
        Elevator.floor_range = [0] + list(range(16, 26))


#########################
##       Floors        ##
#########################
class Floor(object):
    def __init__(self):
        self.L = 0  # holds the line for this floor
        # notice: although there's 25 slots, every floor can reach only specific floors
        # for each one of the 25 destinations
        self.passengers_in_line = [[]] * 25
    # add a new passenger to the line

    def add_passenger(self, passenger):
        self.passengers_in_line.append(passenger)
    # return waiting passengers for this destination

    def get_waiting_passengers(self, destination):
        return self.passengers_in_line[destination]


#######################################################################################
#######################################################################################
#######################################################################################
##########################
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

##########################
## returns current rate ##
##########################


def get_current_cumulative_rate_by_section(section):
    if curr_time >= 60 and curr_time < 4*60:
        # 07:00-10:00
        # Convert to exponential rate
        return 60/arrival_rates_by_floor_section[section][2]
    elif curr_time >= 9*60 and curr_time < 12*60:
        # 15:00-18:00
        # Convert to exponential rate
        return 60/arrival_rates_by_floor_section[section][1]
    else:
        # any other time
        # Convert to exponential rate
        return 60/arrival_rates_by_floor_section[section][0]

    rate = arrival_rates[start_floor_section][end_floor_section][hour_range]
    return 60/rate

###############################
## returns total travel time ##
###############################


def get_travel_time(start_floor, end_floor):
    elevator_start_time = 2
    elevator_stop_time = 2
    return elevator_start_time + end_floor - start_floor + elevator_stop_time


def is_same_section(start_floor, end_floor):
    if start_floor > 15:
        if end_floor <= 15:
            return False
        else:
            return True
    else:
        if end_floor <= 15:
            return True
        else:
            return False

# returns the destination according to the prior passenger


def get_destination(end_floor):
    if end_floor == 0:
        return 0
    elif end_floor > 15:
        return np.random.randint(16, 26)
    else:
        return np.random.randint(1, 16)

#
# def get_arrival_floor():
#    rnd = np.random.rnd() # random number
#    rate_section_0 = 60 / get_current_cumulative_rate_by_section(0)
# #   rate_section_1 = 60 / get_current_cumulative_rate_by_section(1)
 #   rate_section_2 = 60 / get_current_cumulative_rate_by_section(2)
 #   total_arrival = rate_section_0 + rate_section_1 + rate_section_2
#   if rnd > rate_section_0 / total_arrival


#######################################################################################
#######################################################################################
#######################################################################################
# initialize simulation
print('Spaceship Elevator')
curr_time = 0
P = []
A = 0
SIM_TIME = 14*60  # simulation time in minutes
L = [0]*24  # initiate empty line in every floor
passenger_counter = 0

##### Create the Elevators #####
##### Lower-floors elevator ####
elevator0 = Lower_floors_Elevator("Elevator1", 0)
elevator1 = Lower_floors_Elevator("Elevator2", 0)
#### Higher-floors elevator ####
elevator2 = Upper_floors_Elevator("Elevator3", 0)
elevator3 = Upper_floors_Elevator("Elevator4", 0)
# all elevators
elevators = [elevator0, elevator1, elevator2, elevator3]
##### Create the Floors ######
floors = [Floor()] * 26

# initiate first arrival for each floor
# each floor has a person traveling to one of the 3 floor-groups
for floor_number in range(1, 26):
    Event(np.random.exponential(get_current_rate_by_floor(
        floor_number, 0)), "arriving")  # GROUP 1
    Event(np.random.exponential(get_current_rate_by_floor(
        floor_number, 15)), "arriving")  # GROUP 2
    Event(np.random.exponential(get_current_rate_by_floor(
        floor_number, 25)), "arriving")  # GROUP 3

Event(np.random.exponential(get_current_rate_by_floor(0, 15)), "arriving")  # GROUP 2
Event(np.random.exponential(get_current_rate_by_floor(0, 25)), "arriving")  # GROUP 3

#######################################################################################
#######################################################################################
#######################################################################################
#####################
## simulation loop ##
#####################
while curr_time < SIM_TIME:  # LOOP stops when time ends

    event = heapq.heappop(P)  # get next event
    prev_time = curr_time  # time of last event
    curr_time = event.time  # current event's time

    if event.eventType == "arriving":
        passenger_counter += 1
        new_passenger = Passenger(arrival_time=curr_time, destination=get_destination(
            event.passenger.destination), id=passenger_counter, start_floor=event.passenger.start_floor)

        if theater.available[movie] > 0:
            i += 1
            theater.L += 1
            people_in.append(theater.L)
            time.append(curr_time)
            if A == 0:
                A = 1
                Event(curr_time + 1, "buy_tickets", new_customer)
            else:
                heapq.heappush(line, (new_customer.arrival_time, new_customer))
            Event(curr_time + new_customer.patience,
                  "out_of_patience", new_customer)
        Event(curr_time + np.random.exponential(1 / 2),
              "arriving")  # create the next arrivel

    elif event.eventType == "buy_tickets":
        if event.customer.left == False:  # check if the customer left the queue
            movie = event.customer.movie
            # Check if enough tickets left.
            if theater.available[movie] < event.customer.num_tickets:
                # customer leaves after some discussion
                Event(curr_time + 0.5, "argue_with_seller", event.customer)
            else:      # Buy tickets
                theater.available[movie] -= num_tickets
                if theater.available[movie] < 1:
                    # Trigger the "sold out" event for the movie
                    print("HERE MAYBE")
                    Event(curr_time, "sold_out", movie1=movie)
            theater.L -= 1
            people_in.append(theater.L)
            time.append(curr_time)
            event.customer.left = True
        if line:
            arrival_time, customer = heapq.heappop(line)
            Event(curr_time + 1, "buy_tickets", customer)
        else:
            A = 0

    elif event.eventType == "argue_with_seller":
        if line:
            arrival_time, customer = heapq.heappop(line)
            Event(curr_time + 1, "buy_tickets", customer)
        else:
            A = 0

    elif event.eventType == "sold_out":
        print("IM HERE")
        theater.when_sold_out[movie] = curr_time
        theater.available[movie] = 0
        line = [item for item in line if item[1].movie != event.movie]
        if not any([movie == None for movie in theater.when_sold_out.values()]):
            theater.all_sold_out = True

    elif event.eventType == "out_of_patience":
        if event.customer.left != True:
            event.customer.left = True
            theater.num_leavers[movie] += 1
            theater.L -= 1
            people_in.append(theater.L)
            time.append(curr_time)
