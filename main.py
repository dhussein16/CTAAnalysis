# Dua'a Hussein
# CS 341 Spring 2024
# UIN:655469322
# Professor Kidane
# This program uses the CTADailyRidershsip database in order to analyze
# and print out stastics and information about the riders, stations,
# and more using SQL and Python. The program allows for users to see
# graphs and tables of information depending on the command that they
# input to run. 

import sqlite3
import matplotlib.pyplot as plt
import calendar # researched this, apparently it's very useful for plotting!
import math # needed for Command 9
import datetime # will potentially help fix plotting errors in command 8

##################################################################  
# print_stats
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    print("General Statistics:")
    
    # prints out the number of stations
    dbCursor.execute("Select count(*) From Stations;")
    row = dbCursor.fetchone()
    print("  # of stations:", f"{row[0]:,}")

    # prints out the numbers of stops 
    dbCursor.execute("Select DISTINCT(count(*)) From Stops")
    stopCount = dbCursor.fetchone()
    print("  # of stops:", f"{stopCount[0]:,}")

    # prints out the number of rides
    dbCursor.execute("Select count(*) from Ridership")
    rideEntries = dbCursor.fetchone()
    print("  # of ride entries:", f"{rideEntries[0]:,}")

    # prints out the start and end dates
    dbCursor.execute("Select date(Ride_Date) from Ridership Order By Ride_Date asc Limit 1")
    startDate = dbCursor.fetchone()
    dbCursor.execute("Select date(Ride_Date) from Ridership Order By Ride_Date desc Limit 1")
    endDate = dbCursor.fetchone()
    print("  date range:", startDate[0], "-", endDate[0])

    # prints out the total number of riders
    dbCursor.execute("Select SUM(Num_Riders) from Ridership")
    totalRiders = dbCursor.fetchone()
    print("  Total ridership:", f"{totalRiders[0]:,}")

##################################################################  
# check_validity
# A function that is used to check whether the userInput
# is between the values of 1 or 9 or x. Returns True
# if the input is valid, false otherwise
def check_validity(userInput):
    if userInput.isdigit() and 1 <= int(userInput) <= 9:
        return True
    elif userInput.lower() == 'x':
        return True
    else:
        return False

################################################################## 
# command_one 
# This function controls command 1, where it allows for the user to 
# input a partial station name and search the database for stations
# that may have that input somewhere in its name. 
def command_one(dbConn):
    dbCursor = dbConn.cursor()
    
    # ask the user for input
    print()
    userStation = input("Enter partial station name (wildcards _ and %): ")

    # execute SQL query with user input and get the response
    dbCursor.execute("SELECT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE ? ORDER BY Station_Name ASC", (userStation,))
    allStations = dbCursor.fetchall()

    # if the list/dictionary was empty, return
    if(len(allStations) == 0):
        print("**No stations found...")
    # otherwise print out the station id and statoin
    else:
        for stationId, stationName in allStations:
            print(f"{stationId} : {stationName}")
    
################################################################## 
# command_two
# given a user input, this function should find the percentage of riders on
# weekdays, Saturdays, and Sundays/Holidays for a specific station, where the
# user must submit an EXACT name for the station and the percentage 
# is based off of the total amount of riders. Takes dbConn as parameters,
# prints out statistics as output
def command_two(dbConn):
    dbCursor = dbConn.cursor()
    print()
    userStation = input("Enter the name of the station you would like to analyze: ")

    # Create an SQLquery to select the Day type and the total riders for a selected station
    # Notice the lack of "LIKE" in the WHERE section means that the input from the user
    # MUST be an exact search
    sqlQuery = """
                SELECT Type_of_Day, SUM(Num_Riders) AS TotalRiders
                FROM Ridership R
                JOIN Stations S ON R.Station_ID = S.Station_ID
                WHERE S.Station_Name = ?
                GROUP BY Type_of_Day
               """
    
    # the query is run against the user input and the answer is saved
    dbCursor.execute(sqlQuery, (userStation,))
    allStations = dbCursor.fetchall()

    # if nothing was found on user's station, return "No data found"
    if(len(allStations) == 0):
        print("**No data found...")
    
    else:
        # Calculating the total ridership (_ is to ignore the type of day for total)
        totalRiders = sum([count for _, count in allStations])

        # Dictionary to hold day types and their corresponding total riders
        dayTypesTotals = {result[0]: result[1] for result in allStations}

        # Printing all results with percentages
        print("Percentage of ridership for the", userStation, "station: ")
        for dayType in ['W', 'A', 'U']:  # W for Weekday, A for Saturday, U for Sunday/Holiday
            count = dayTypesTotals.get(dayType)
            percentage = (count / totalRiders) * 100
            if(dayType == 'W'):
                print(f"  Weekday ridership: {count:,} ({percentage:.2f}%)")
            elif(dayType == 'A'):
                print(f"  Saturday ridership: {count:,} ({percentage:.2f}%)")
            else:
                print(f"  Sunday/holiday ridership: {count:,} ({percentage:.2f}%)")

        print("  Total ridership:", f"{totalRiders:,}") # print the total

################################################################## 
# command_three
# command_three outputs the total ridership on weekdays for each station with the station names
# It should show the percentages based on total ridership, and be ordered by descending order
def command_three(dbConn):
    dbCursor = dbConn.cursor()
    print("Ridership on Weekdays for Each Station")

    # SQL query to get the total number of weekday riders for each station, execute
    sqlQuery = """
                SELECT S.Station_Name, SUM(R.Num_Riders) AS WeekdayRiders
                FROM Ridership R
                JOIN Stations S ON R.Station_ID = S.Station_ID
                WHERE R.Type_of_Day = 'W'
                GROUP BY S.Station_ID
                ORDER BY WeekdayRiders DESC
               """
    dbCursor.execute(sqlQuery)

    # Fetching the results
    results = dbCursor.fetchall()

    # Calculating the total weekday ridership for all stations
    totalRiders = sum([riders for _, riders in results])

    # Printing the results with percentages
    for station, riders in results:
        percentage = (riders / totalRiders) * 100
        print(f"{station} : {riders:,} ({percentage:.2f}%)")

################################################################## 
# command_four
# Given a line color and direction, the stops for the line color/direction
# will be outputs in ascending order. It takes dbConn as an input 
# and outputs a series of print statements. 
def command_four(dbConn):
    dbCursor = dbConn.cursor()

    # for whitespace
    print()
    print()

    # get the user's line color and check if it exists
    userLine = input("Enter a line color (e.g. Red or Yellow): ")
    dbCursor.execute("SELECT Color FROM Lines WHERE LOWER(Color) = LOWER(?)", (userLine,))
    retrievedLine = dbCursor.fetchall()
    if(len(retrievedLine) == 0):
        print("**No such line...")
        return;

    # get the user's direction and check if the direction
    # exists for their chosen line
    userDirection = input("Enter a direction (N/S/W/E): ")
    sqlQuery = """
                SELECT DISTINCT St.Direction
                FROM Stops St
                JOIN StopDetails SD ON St.Stop_ID = SD.Stop_ID
                JOIN Lines L ON SD.Line_ID = L.Line_ID
                WHERE LOWER(L.Color) = LOWER(?) 
               """
    dbCursor.execute(sqlQuery, (userLine,))
    results = dbCursor.fetchall()

    # conduct a check to see if the direction for the designated line exists
    if(not any(userDirection.lower() == direction[0].lower() for direction in results)):
        print("**That line does not run in the direction chosen...")
        return;
    
    # for this query, we need the stop name, the direction, and whether its handicap 
    # accesible since that is what the output information contains
    sqlQuery = """
            SELECT St.Stop_Name, St.Direction, St.ADA
            FROM Stops St
            JOIN StopDetails SD ON St.Stop_ID = SD.Stop_ID
            JOIN Lines L ON SD.Line_ID = L.Line_ID
            WHERE LOWER(L.Color) = LOWER(?) AND LOWER(St.Direction) = LOWER(?)
            ORDER BY St.Stop_Name
            """
    dbCursor.execute(sqlQuery, (userLine, userDirection))
    stops = dbCursor.fetchall()

    # a for loop that prints out the information
    for stop_name, stop_direction, ada in stops:
        ada_status = "handicap accessible" if ada else "not handicap accessible"
        print(f"{stop_name} : direction = {stop_direction} ({ada_status})") 

################################################################## 
# command_five 
# this function will output the number of stops for each line color
# and separated by direction, where it is organized in ascending order by 
# their direction along with their percentage taken from the total
# number of stops
def command_five(dbConn):
    dbCursor = dbConn.cursor()
    
    # create the SQL query, execute it, and get the results
    sqlQuery = """
                SELECT L.Color, St.Direction, COUNT(*)
                FROM Stops St
                JOIN StopDetails SD ON St.Stop_ID = SD.Stop_ID
                JOIN Lines L ON SD.Line_ID = L.Line_ID
                GROUP BY L.Color, St.Direction
                ORDER BY L.Color ASC, St.Direction ASC
                """
    dbCursor.execute(sqlQuery)
    results = dbCursor.fetchall()

    # created a query to count the total number of stops from the Stops table!
    # in order to calculate %, calculate the total from the executed query
    calcTotalStopsQuery = """
                            SELECT COUNT(Stop_ID)
                            From Stops
                          """
    dbCursor.execute(calcTotalStopsQuery)
    totalStops = dbCursor.fetchone()[0]

    # print results and findings
    print("Number of Stops For Each Color By Direction")
    for color, direction, count in results:
        percentage = (count / totalStops) * 100
        print(f"{color} going {direction} : {count} ({percentage:.2f}%)")


################################################################## 
# command_six 
# This function controls command six, which allows the user 
#  to give an input  a station name and output the total ridership
# in ascending order by year, and the user is allowed to use 
# wild cards
def command_six(dbConn):
    dbCursor = dbConn.cursor()

    print()

    # get user input
    userInput = input("Enter a station name (wildcards _ and %): ")
    
    # execute sql and get results
    sqlQuery = "SELECT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE ?"
    dbCursor.execute(sqlQuery, (userInput,))
    results = dbCursor.fetchall()

    # if there is nothing that matches, or multiple, print out corresponding message and exit
    if(len(results) == 0):
        print("**No station found...")
        return
    if(len(results) > 1):
        print("**Multiple stations found...")
        return

    # save the station name and the id to use in following sql query
    userStationName = results[0][1]
    userStationID = results[0][0]
    
    # get the year and the total riders for that station
    ridershipQuery = """
                        SELECT strftime('%Y', Ride_Date) AS Year, SUM(Num_Riders) AS TotalRiders
                        FROM Ridership
                        WHERE Station_ID = ?
                        GROUP BY Year
                        ORDER BY Year ASC
                     """

    # execute query and get results
    dbCursor.execute(ridershipQuery, (userStationID,)) 
    finalResults = dbCursor.fetchall()

    # print results, save the data into arrays to save for potential plotting
    print(f"Yearly Ridership at {userStationName}")
    years = []
    riderships = []
    for year, totalRiders in finalResults:
        years.append(year)
        riderships.append(int(totalRiders))
        print(f"{year} : {totalRiders:,}")

    # ask user if you want to plot, and if y, plot the data
    plotInput = input("Plot? (y/n) ")
    if plotInput.lower() == 'y':
        plt.figure(figsize=(10, 6))
        plt.plot(years, riderships, color='blue')
        plt.xlabel('Year')
        plt.ylabel('Total Ridership')
        plt.title(f'Yearly Ridership at {userStationName}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show(block =False)
    else: return


################################################################## 
# command_seven
# this command should allow the user to enter a station and
# a year with wildcards for the station, and it should display the 
# monthly totals with the option to plot the corresponding 
# totals 
def command_seven(dbConn):
    print()

    # get the user input and run a query to check to see if there is 
    # only one of those stations present 
    dbCursor = dbConn.cursor()
    userStationInput = input("Enter a station name (wildcards _ and %): ")
    sqlQuery = "SELECT Station_Name FROM Stations WHERE Station_Name LIKE ?"
    dbCursor.execute(sqlQuery, (userStationInput,))
    results = dbCursor.fetchall()

    # if there is nothing that matches, or multiple, print out corresponding message and exit
    if len(results) == 0:
        print("**No station found...")
        return
    if len(results) > 1:
        print("**Multiple stations found...")
        return

    # save the user's station and ask for a year
    userStationName = results[0][0]  # Assuming results[0] is a tuple like (station_name,)
    userYearInput = input("Enter a year: ")

    # execute the yearQuery to get the data for the specific year, and the extract the 
    # results to save to monthlyData
    yearQuery = """SELECT strftime('%m', Ride_Date) AS Month, SUM(Num_Riders) AS MonthlyTotal
               FROM Ridership
               JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
               WHERE Stations.Station_Name = ? AND strftime('%Y', Ride_Date) = ?
               GROUP BY Month
               ORDER BY Month ASC
               """

    dbCursor.execute(yearQuery, (userStationName, userYearInput))
    monthlyData = dbCursor.fetchall()

    # printing the ridership by month with formatting
    print(f"Monthly Ridership at {userStationName} for {userYearInput}")
    for month, total in monthlyData:
        formatted_total = "{:,}".format(int(total))  # Formats the total with commas
        print(f"{month}/{userYearInput} : {formatted_total}")

    # Prepare data for plotting by converting to ints
    months = [int(month) for month, total in monthlyData]
    totals = [int(total) for month, total in monthlyData]

    # Plotting section
    plotInput = input("Plot? (y/n) ")
    if plotInput.lower() == 'y':
        plt.figure(figsize=(10, 6))
        plt.plot(months, totals, marker='o', linestyle='-', color='b')
        plt.title(f'Monthly Ridership for {userStationName} in {userYearInput}')
        plt.xlabel('Month')
        plt.ylabel('Number of Riders')
        plt.xticks(months, [calendar.month_abbr[month] for month in months])
        plt.grid(True)
        plt.show(block =False)
    else: return
################################################################## 
# command_eight
# This function controls command eight, which allows the user to input
# two station names and a year, where it will output the total
# ridership for the first five days and the last five days of the year,
# with the option to plot the given data
def command_eight(dbConn):
    dbCursor = dbConn.cursor()

    print()
    # User's inputs
    userInputYear = input("Year to compare against? \n")
    userFirstStation = input("Enter station 1 (wildcards _ and %): ")
    
    # Query for the first station
    sqlQuery = "SELECT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE ?"
    dbCursor.execute(sqlQuery, (userFirstStation,))
    firstStationResults = dbCursor.fetchall()

    # check if the firstStationResults is exactly one
    if len(firstStationResults) == 0:
        print("**No station found...")
        return
    if len(firstStationResults) > 1:
        print("**Multiple stations found...")
        return

    print()
    # Query for the second station
    userSecondStation = input("Enter station 2 (wildcards _ and %): ")
    dbCursor.execute(sqlQuery, (userSecondStation,))
    secondStationResults = dbCursor.fetchall()

    if len(secondStationResults) == 0:
        print("**No station found...")
        return
    if len(secondStationResults) > 1:
        print("**Multiple stations found...")
        return

    # Function to fetch ridership data
    def fetch_ridership(stationID):
        query = """SELECT date(Ride_Date), SUM(Num_Riders) AS DailyTotal
                   FROM Ridership 
                   WHERE Station_ID = ? AND strftime('%Y', Ride_Date) = ?
                   GROUP BY Ride_Date
                   ORDER BY Ride_Date"""
        dbCursor.execute(query, (stationID, userInputYear))
        return dbCursor.fetchall()

    # Fetching and displaying data for both stations
    count = 1
    for station, stationData in zip([userFirstStation, userSecondStation], [firstStationResults, secondStationResults]):
        data = fetch_ridership(stationData[0][0])
        print(f"Station {count}: {stationData[0][0]} {stationData[0][1]}")
        count = count + 1
        for row in data[:5] + data[-5:]:
            print(f"{row[0]} {row[1]}")

    # Ask for plotting
    plotInput = input("\nPlot? (y/n) ")
    if plotInput.lower() == 'y':
        plt.figure(figsize=(12, 6))

        # Fetch and plot data for the first station
        firstStationData = fetch_ridership(firstStationResults[0][0])
        if firstStationData:
            dates = [datetime.datetime.strptime(row[0], "%Y-%m-%d").timetuple().tm_yday for row in firstStationData]
            riders = [row[1] for row in firstStationData]
            plt.plot(dates, riders, label=f"{firstStationResults[0][1]} Ridership")  # Using station name for label

        # Fetch and plot data for the second station
        secondStationData = fetch_ridership(secondStationResults[0][0])
        if secondStationData:
            dates = [datetime.datetime.strptime(row[0], "%Y-%m-%d").timetuple().tm_yday for row in secondStationData]
            riders = [row[1] for row in secondStationData]
            plt.plot(dates, riders, label=f"{secondStationResults[0][1]} Ridership")  # Using station name for label

        plt.title(f"Daily Ridership Comparison in {userInputYear}")
        plt.xlabel("Day of the Year")
        plt.ylabel("Number of Riders")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show(block=False)

################################################################## 
# command_nine
# The command nine function should take in a users latitude and 
# longitude input,  find all the stations within a mile square radius
# of that input, expecting that the user's coordinates are within chicago
# if the user decides to plot, it should plot the nearby
# stations within the users coordinates on a map of chicago
def command_nine(dbConn):
    dbCursor = dbConn.cursor()

    print()

    # Get user input and validate the input for both latitude and longitude
    latitude = float(input("Enter a latitude: "))
    if not (40 <= latitude <= 43):
        print("**Latitude entered is out of bounds...")
        return

    longitude = float(input("Enter a longitude: "))
    if not (-88 <= longitude <= -87):
        print("**Longitude entered is out of bounds...")
        return
    
    # Calculate the degrees
    milesInDegreesLatitude = 1 / 69
    milesInDegreesLongitude = 1 / 51
    
    # Calculate the lower and upper bounds of latitude and longitude for the one-mile radius
    # if a station is within these boundaries, they should appear in the output
    latitudeUpper = round(latitude + milesInDegreesLatitude, 3)
    latitudeLower = round(latitude - milesInDegreesLatitude, 3)
    longitudeUpper = round(longitude + milesInDegreesLongitude, 3)
    longitudeLower = round(longitude - milesInDegreesLongitude, 3)

    # SQL query to find stations within the calculated bounds, execute it, and get the results
    sqlQuery =  """
                SELECT DISTINCT(S.Station_Name), St.Latitude, St.Longitude 
                FROM Stations S
                JOIN Stops St ON S.Station_ID = St.Station_ID
                WHERE St.Latitude BETWEEN ? AND ? AND St.Longitude BETWEEN ? AND ?
                ORDER BY S.Station_Name asc
                """
    dbCursor.execute(sqlQuery, (latitudeLower, latitudeUpper, longitudeLower, longitudeUpper))
    stations = dbCursor.fetchall()

    if(len(stations) == 0):
        print("**No stations found...")
        return

    print()

    # Display stations (should be distinct)
    print("List of Stations Within a Mile")
    for station in stations:
        print(f"{station[0]} : ({station[1]}, {station[2]})")

    print()

    # If the user wants to plot the results, plot 
    plotInput = input("Plot? (y/n) ")
    if plotInput.lower() == 'y':
        x = [station[2] for station in stations]  # Longitude
        y = [station[1] for station in stations]  # Latitude
        image = plt.imread("chicago.png") # Image of chicago map underlay
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868]  # Area covered by the map
        plt.imshow(image, extent=xydims)
        plt.title("Stations Near You")
        plt.scatter(x, y, color='red', marker='o')  # Plot stations

        # Annotate each station
        for station in stations:
            plt.annotate(station[0], (station[2], station[1]))

        plt.xlim([-87.9277, -87.5569])
        plt.ylim([41.7012, 42.0868])
        plt.show()

################################################################## 
# main
print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')

# print out the general stats
print_stats(dbConn)

userInput = '0' # establish a user input variable

while(userInput != 'x'):
    # prompt for user input
    print()
    userInput = input("Please enter a command (1-9, x to exit): ")

    # check validity of user input 
    if(check_validity(userInput) == False):
        print("**Error, unknown command, try again...")
        continue

    # depending on user's input, execute corresponding command
    # each command is defined and written in a function defined above
    if(userInput == '1'): command_one(dbConn)
    elif(userInput == '2'): command_two(dbConn)
    elif(userInput == '3'): command_three(dbConn)
    elif(userInput == '4'): command_four(dbConn)
    elif(userInput == '5'): command_five(dbConn)
    elif(userInput == '6'): command_six(dbConn)
    elif(userInput == '7'): command_seven(dbConn)
    elif(userInput == '8'): command_eight(dbConn)
    elif(userInput == '9'): command_nine(dbConn)
    else: continue
# done