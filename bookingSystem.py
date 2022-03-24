from datetime import datetime, timedelta
from flask import Flask, flash, request, render_template, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = "abs"
# global array 
data = confData = []
errMessage = ""

@app.route("/info")
def info():
    # Task 4 : define data structures to store tickect info 
    # You have to include ticket price table (use variable options to store all information), 
    # extra attractions table (use variable attractions to store all information), 
    # and days available table (use variable days to store all information) 
    # variable posts is the place to store all data you need to display in the browser
    options = [['one adults', 20, 30],['one child', 12, 18],['one senior', 16, 24]]
    attractions = [['lion feeding', 2.5], ['penguin feeding', 2], ['evening barbecue', 5]]
    days = display_days()
    posts = [options, attractions, days]
    return render_template('info.html', posts=posts)

@app.route("/home", methods=('GET','POST'))
def home():
    if request.method == 'GET': 
        return render_template("home.html")
    elif request.method == 'POST' :
        name = request.form.get('name')
        phone = request.form.get('phone')
        checkin = request.form.get('checkin')
        checkout = request.form.get('checkout')
        seniors = request.form.get('seniors')
        adults = request.form.get('adults')
        children = request.form.get('children')
        attraction = request.form.getlist('attraction')
        #store the data from the front-end into global data structure named data
        global data, confData
        data.append(name)
        data.append(phone)
        data.append(checkin)
        data.append(checkout)
        data.append(seniors)
        data.append(adults)
        data.append(children)
        data.append(attraction)

        # validate the information the user entered 
        if validation(): 
            confData = data
            data = []
            return redirect(url_for('confirmation'))
        else :
            # just like print in python
            flash(errMessage)
            data = []
            return render_template("home.html")
    else : 
        return 0

@app.route("/confirmation")
def confirmation():
    # Task 6: calculate the total cost of the booking order
    global confData
    now = datetime.now().date()
    #1. convert datetime object now to a string object
    now = datetime.strftime(now, '%Y-%m-%d')
    #2. prepare the data for calculation
    checkin = datetime.strptime(confData[2], '%Y-%m-%d')
    checkout = datetime.strptime(confData[3], '%Y-%m-%d')
    seniors = int(confData[4])
    adults = int(confData[5])
    children = int(confData[6])
    interval =  checkout - checkin
    #3. calculate the number of people
    totalPeople = seniors + adults + children
    #4. one adult may bring up to 2 children, re-arrange the number of adults, senoirs, and children
    if children - ((adults + seniors) * 2) > 0:
        extadults = (children - ((adults + seniors) * 2))
        adults = adults + extadults
        children = children - extadults 
    #5. calculate the total cost without attractions
    if interval.days == 0:
        totalCost = seniors * 16 + adults * 20 + children * 12
    else:
        totalCost = seniors * 24 + adults * 30 + children * 18
    #6. calculate the total cost with attractions
    totalCostAtt = 0
    totalCostAltAtt = 0
    if "1" in confData[7]:
        totalCostAtt = totalPeople * 2.5 + totalCost
    elif "2" in confData[7]:
        totalCostAtt = totalPeople * 2 + totalCost
    elif "3" in confData[7]:
        totalCostAtt = totalPeople * 5 + totalCost
    else:
        totalCostAtt = totalCost
    # Task 7: display the options the customer chose

    # You need to define the data structures to organize the options the customer chose
    # and properly display the total cost based on the customer's choice
    table1 = [
        ["one child", interval.days + 1, children, (12 * children) * (interval.days * 1.5)], 
        ["one adult", interval.days + 1, adults, (20 * adults) * (interval.days * 1.5)],
        ["one senior", interval.days + 1, seniors, (16 * seniors) * (interval.days * 1.5)],
    ]
    if "1" in confData[7]:
        table1 += [["lion feeding", "", totalPeople, (totalPeople * 2.5)]]
    if "2" in confData[7]:
        table1 += [["penguin feeding", "", totalPeople, (totalPeople * 2)]]
    if "3" in confData[7]:
        table1 += [["evening barbecue", "", totalPeople, (totalPeople * 5)]]
    
    # Task 8: offer an alternative if available and calculate the costs
    #calculate the cheapest option
    children = int(confData[6])
    adults = int(confData[5])
    seniors = int(confData[4])
    familyT = 0
    sixT = 0
    divChildren = 0
    divAdSe = 0
    totalCostAlt = 0
    arrayList = alternatives(children, adults, seniors, familyT, sixT)
    if interval.days == 0:
        totalCostAlt = arrayList[0] * 12 + arrayList[1] * 20 + arrayList[2] * 16 + arrayList[3] * 60 + arrayList[4] * 15
    else:
        totalCostAlt = arrayList[0] * 18 + arrayList[1] * 30 + arrayList[2] * 24 + arrayList[3] * 90 + arrayList[4] * 22.5
    if totalCostAlt > totalCost:
        totalCostAlt = totalCost
    
    # Task 9: display the alternative, including the total cost and options the customer could choose
    if totalCostAlt <= totalCost:
        table2 = [
            ["one child", interval.days + 1, arrayList[0], (12 * arrayList[0]) * (interval.days * 1.5)], 
            ["one adult", interval.days + 1, arrayList[1], (20 * arrayList[1]) * (interval.days * 1.5)], 
            ["one senior", interval.days + 1, arrayList[2], (16 * arrayList[2]) * (interval.days * 1.5)],
            ["family ticket", interval.days + 1, arrayList[3], (60 * arrayList[3]) * (interval.days * 1.5)],
            ["group ticket", interval.days + 1, arrayList[4], (15 * arrayList[4]) * (interval.days * 1.5)],
        ]
        if "1" in confData[7]:
            table2 += [["lion feeding", "", totalPeople, (totalPeople * 2.5)]]
        if "2" in confData[7]:
            table2 += [["penguin feeding", "", totalPeople, (totalPeople * 2)]]
        if "3" in confData[7]:
            table2 += [["evening barbecue", "", totalPeople, (totalPeople * 5)]]
    
    elif totalCostAlt > totalCost:
        table2 = table1
    
    if "1" in confData[7]:
        totalCostAltAtt = totalPeople * 2.5 + totalCostAlt
    elif "2" in confData[7]:
        totalCostAltAtt = totalPeople * 2 + totalCostAlt
    elif "3" in confData[7]:
        totalCostAltAtt = totalPeople * 5 + totalCostAlt
    else:
        totalCostAltAtt = totalCostAlt
    # Task 10: Save data to be ready to display
    # allocate an unique booking number and display the selected days
    # you have to display all other info you've prepared in previous tasks
    bookingNumber = ''
    #generate a ramdom booking number
    for i in range(0, 10):
        bookingNumber += str(random.randint(0,9))
    #display the selected days 
    days = ''
    if interval.days == 0:
        days = datetime.strftime(checkin, '%Y-%m-%d')
    elif interval.days == 1:
        days = datetime.strftime(checkin, '%Y-%m-%d') + ' to ' + datetime.strftime(checkout, '%Y-%m-%d')
    posts = [bookingNumber, days, table1, totalCost, table2, totalCostAlt, totalCostAtt, totalCostAltAtt]
    confData = []
    return render_template("confirmation.html", posts=posts)
   

@app.route("/complete")
def complete():
    return render_template("complete.html")

#########################################################################################################
# functions related to validation
def validation():
    # Task 1： check if the following input variables match the rules: 
    # phone(data[1]) should be a 11-character long digit 
    # phone(data[1]) should be a number
    # no. of seriors (data[4]) should be a number
    # no. of adults (data[5]) should be a number
    # no. of children (data[6]) should be a number
    global errMessage
    if len(data[1]) != 11:
        errMessage = "The length of phone No. should be 11"
        return False
    elif not data[1].isdigit():
        errMessage = "Incorrect format for phone No."
        return False
    elif not validate_days(data[2], data[3]):
        errMessage = "The date you selected is not available"
        return False
    elif not data[4].isdigit():
        errMessage = "Your input for no. of seniors should be a number"
        return False
    elif not data[5].isdigit():
        errMessage = "Your input for no. of adults should be a number"
        return False
    elif not data[6].isdigit():
        errMessage = "Your input for no. of children should be a number"
        return False
    elif not ifBarbecue(data[2], data[3], data[7]):
        errMessage = "You cannot attend this attraction because of your plan"
        return False
    else :
        return True

def validate_days(checkin, checkout):
    # parameter checkin, checkout are two strings
    # Task 2：
    # checkin(data[2])
    # checkout(data[3])
    # checkout - checkin >= 0 day and checkout - checkin < 2 days
    # checkout - now < 7
    # checkin - now >= 0
    # add this function to the function validation() to check if input date matches the rules
    checkin = datetime.strptime(checkin, '%Y-%m-%d')
    checkout = datetime.strptime(checkout, '%Y-%m-%d')
    # interval is datetime.timedelta object
    interval = checkout - checkin
    # convert now to date-00:00:00
    now = datetime.now()
    now = datetime.strftime(now, '%Y-%m-%d')
    now = datetime.strptime(now, '%Y-%m-%d')
    
    if interval.days < 0 or interval.days >= 2:
        return False
    elif (checkout - now).days >= 7 or (checkin - now).days < 0:
        return False
    else :
        return True

def display_days():
    #Task 5: calculate the days available for customer to pick up
    # store the result in the array named days
    days = []
    for i in range(0, 7):
        day = datetime.strftime(datetime.now().date() + timedelta(days=i), '%Y-%m-%d')
        days.append(day)
    return days




def ifBarbecue(checkin, checkout, attractions):
    # Task 3：attractions(data[7]) is an array of string, 
    # check the dates to see if evening barbecue can be chosen
    # return True if evening barbecue is selected and can be selected
    # return False otherwise
    checkin = datetime.strptime(checkin, '%Y-%m-%d')
    checkout = datetime.strptime(checkout, '%Y-%m-%d')
    # interval is datetime.timedelta object
    # Here, interval can only be 0 or 1
    # since checkin and checkout date have been validated 
    # by the function 'validate_days'
    interval = checkout - checkin
    if interval.days == 0 and '3' in attractions :
        return False
    else :
        return True

def alternatives(children, adults, seniors, familyT, sixT):
    divChildren = children // 3
    divAdSe = (adults + seniors) // 2
    familyT = min(divChildren, divAdSe)

    if adults - familyT * 2 >= 0:
        adults = adults - familyT * 2
    else:
        seniors = seniors - (familyT * 2 - adults)
        adults = 0
    children = children - familyT * 3

    if adults >= 2 and children == 2:
        familyT = familyT + 1
        adults = adults - 2
        children = 0
    
    if children > (seniors + adults) * 2:
        extadults = (children - (seniors + adults) * 2) 
        children = children - (seniors + adults) * 2
        adults += extadults
        children -= extadults
    
    if (seniors + adults) >= 6:
        sixT = seniors + adults
        seniors = adults = 0
    
    if (adults == 5) and children == 1:
        sixT += 6
        adults = adults - 5
        children = 0
    elif (seniors == 5) and children == 1:
        sixT += 6
        seniors = seniors - 5
        children = 0
    

    return [children, adults, seniors, familyT, sixT]

#########################################################################################################