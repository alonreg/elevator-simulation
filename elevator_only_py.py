import random
import pandas as pd  # package for some uses and maybe for visualization
import numpy as np
import heapq
from matplotlib.pylab import plot, show, bar
import matplotlib.pyplot as plt
plt.style.use("ggplot")

#####################################################
##### initiating arrival rates array, from csv ######
#####################################################
df = pd.read_csv('arrival_rates.csv')
df  # TODO: what is this?

floors_num = 25

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
    def __init__(self, start_floor, destination, arrival_time):
        self.start_floor = start_floor
        self.current_floor = start_floor  # TODO is it needed?
        self.is_traveler = (start_floor != 0 and destination != 0) and ((
            start_floor > 15 and destination <= 15) or (start_floor <= 15 and destination > 15))
        self.current_leg = 1  # describes the current part of the journey. Either 1 or 2
        self.destination = destination
        self.elevator = -1  # waits before entering elevator
        self.patience = 15*60  # 15 minutes patience
        self.arrival_time = arrival_time
        passenger_count += 1
        self.id = passenger_count  # unique identifier

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
    def __init__(self, name, starting_floor, top_elevator):
        self.name = name
        self.curr_floor = starting_floor
        self.prev_floor = None
        self.stop_time = 0  # last stop time
        self.passengers = []
        self.passengers = []
        self.max_capacity = 15
        self.remaining_space = self.max_capacity - len(self.passengers)
        self.direction = 1  # direction is up
        self.is_top_elevator = top_elevator
        self.is_broken = False  # elevator starts un-broken
        self.last_broken_time = False  # time of last break
        self.fix_time = False  # time of expected fix
        self.floors_since_fix = 0  # Floors that passed since fix

    # Gets the elevator destination. Checks if it was broken until arriving
    def check_elevator_is_broken(self, dest):
        if self.is_broken:
            # was broken at curr_floor.
            # check if fix is ready

        else:
            pass

        return False

    def switch_direction(self):
        self.direction *= -1

    # TODO perhaps return if elevator has broken
    def move_elevator(self, floor):
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

    def is_stuck(self):
        return False

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

# TODO check if same section, and check if same direction


def get_travel_time(start_floor, end_floor):
    # TODO: keep in mind floors 15, 25, and 0
    elevator_start_time = 2
    elevator_stop_time = 2
    # return elevator_start_time + end_floor - start_floor + elevator_stop_time
    if start_floor < end_floor:
        return (end_floor-start_floor) * 10
    else:
        return (start_floor-end_floor) * 10
# returns if the start floor and end floor are in the same section


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


def get_leaving_time(start, end):
    # TODO test for room in elevator
    if start <= 15:
        # lower floors
        time0 = elevator0.get_arrival_time(floor_stop=start, end=end)
        time1 = elevator1.get_arrival_time(floor_stop=start, end=end)
        if time1 > time0:
            return time0, elevator0
        else:
            return time1, elevator1
    else:
        # upper floors
        time2 = elevator2.get_arrival_time(floor_stop=start, end=end)
        time3 = elevator3.get_arrival_time(floor_stop=start, end=end)
        if time3 > time2:
            return time2, elevator2
        else:
            return time3, elevator3


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
curr_time = 0
P = []
A = 0
SIM_TIME = 14*60  # simulation time in minutes
L = [0]*24  # initiate empty line in every floor # TODO delete this?
passenger_count = 0

##### Create the Elevators #####
##### Lower-floors elevator ####
# TODO change to regular elevator?
elevator0 = Elevator("Elevator1", 0, False)
elevator1 = Elevator("Elevator2", 0, False)
#### Higher-floors elevator ####
elevator2 = Elevator("Elevator3", 0, True)
elevator3 = Elevator("Elevator4", 0, True)
# all elevators
elevators = [elevator0, elevator1, elevator2, elevator3]
bottom_elevators = [elevator0, elevator1]
top_elevators = [elevator2, elevator3]
##### Create the Floors ######
floors = [Floor()] * 26


##################################################################################
################################## Initialize ####################################
##################################################################################
# initiate first arrival for each floor
# each floor has a person traveling to one of the 3 floor-groups
for floor_number in range(1, 26):
    time1 = np.random.exponential(get_current_rate_by_floor(floor_number, 0))
    time2 = np.random.exponential(get_current_rate_by_floor(floor_number, 15))
    time3 = np.random.exponential(get_current_rate_by_floor(floor_number, 25))

    new_passenger1 = Passenger(arrival_time=time1, destination=get_destination(
        0), start_floor=floor_number)
    new_passenger2 = Passenger(arrival_time=time2, destination=get_destination(
        15), start_floor=floor_number)
    new_passenger3 = Passenger(arrival_time=time3, destination=get_destination(
        25), start_floor=floor_number)

    Event(time1, "arriving", new_passenger1)  # GROUP 1
    Event(time2, "arriving", new_passenger2)  # GROUP 2
    Event(time3, "arriving", new_passenger3)  # GROUP 3

# initiate passengers from zero floor
time2 = np.random.exponential(get_current_rate_by_floor(0, 15))
time3 = np.random.exponential(get_current_rate_by_floor(0, 25))
new_passenger2 = Passenger(
    arrival_time=time2, destination=get_destination(15), start_floor=0)
new_passenger3 = Passenger(
    arrival_time=time3, destination=get_destination(25), start_floor=0)
Event(time2, "arriving", new_passenger2)  # GROUP 2
Event(time3, "arriving", new_passenger3)  # GROUP 3

#######################################################################################
###################################### Loop ###########################################
#######################################################################################
#####################
## simulation loop ##
#####################
while curr_time < SIM_TIME:  # LOOP stops when time ends

    event = heapq.heappop(P)  # get next event
    prev_time = curr_time  # time of last event
    curr_time = event.time  # current event's time

    #################################
    ##########  ARRIVE  #############
    #################################
    if event.eventType == "arriving":
        passenger = event.passenger
        # test what is the first elevator to come
        time, elevator = get_leaving_time(
            start=passenger.start_floor, end=passenger.destination)
        if time > 15*60:
            # no more patience, customer is taking the stairs
            Event(time=curr.time + 15*60, eventType="stairs",
                  passenger=passenger)
        elif passenger.is_traveler:
            # passenger is going to floor 0, for a 2-part journey
            Event(time=time, eventType="journey",
                  passenger=passenger, elevator=elevator)
        else:
            # passenger is prepared to leave the system at this time
            Event(time=time, eventType="leaving",
                  passenger=passenger, elevator=elevator)
        # Create next arrival, based on the last passenger on the same floor
        # random floor in same section
        new_pass_dest = get_destination(passenger.destination)
        new_passenger = Passenger(
            arrival_time=curr_time, destination=new_pass_dest, start_floor=passenger.start_floor)
        Event(time=time, eventType="arriving",
              passenger=new_passenger, elevator=elevator)

    elif event.eventType == "leaving":
        # TODO:
        # 1. check elevator broken (use elevator object to decide)
        # 2. move elevator if not broken
        # 3. clear passenger
        elevator = event.elevator
        passenger = event.passenger
        if elevator.is_broken():
            pass
        elif elevator.will_
    elif event.eventType == "journey":
        pass
    elif event.eventType == "replace":
        pass
    elif event.eventType == "stairs":
        pass

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
