

def find_zero_crossing(begin, inSeries, startCapital):
    a = begin
    b = a + 1
    x = inSeries[a] - startCapital
    y = startCapital - inSeries[b]
    alfa = 1 / (1 + (y / x))

    return a + alfa

def makeTracesToColorEqChart(startCapital, equity_values):
    # iterate through equity_values 
    # if value is positive then color is green else red
    # return list of colors

    crossings = []
    # global startCapital
    # global equity_values
    # find points where equity crosses startCapital

    if len(equity_values) >= 2:
        for i, j in zip(equity_values, equity_values[1:]):
            if (i < startCapital and j > startCapital) or (i > startCapital and j < startCapital):
                # print(i)
                # print(j)
                newPoint = find_zero_crossing(equity_values.index(i), equity_values, startCapital)

                crossings.append(newPoint)

    it = 0

    greenTraceX = []
    breakEvenTraceX = []
    redTraceX = []

    greenTraceY = []
    breakEvenTraceY = []
    redTraceY = []

    if len(equity_values) >= 2: 
        for x, a in zip(equity_values, equity_values[1:]):
            if (x < startCapital and a > startCapital) or (x > startCapital and a < startCapital):
                
                greenTraceY.append(max(x, startCapital))
                breakEvenTraceY.append(startCapital)
                redTraceY.append(min(x, startCapital))

                greenTraceX.append(equity_values.index(x))
                breakEvenTraceX.append(equity_values.index(x))
                redTraceX.append(equity_values.index(x)) 

                greenTraceY.append(startCapital)
                breakEvenTraceY.append(startCapital)
                redTraceY.append(startCapital)

                greenTraceX.append(crossings[it])
                breakEvenTraceX.append(crossings[it])
                redTraceX.append(crossings[it])
                it = it + 1

            else:

                greenTraceY.append(max(x, startCapital))
                breakEvenTraceY.append(startCapital)
                redTraceY.append(min(x, startCapital))

                greenTraceX.append(equity_values.index(x))
                breakEvenTraceX.append(equity_values.index(x))
                redTraceX.append(equity_values.index(x)) 

    
        greenTraceY.append(max(equity_values[-1], startCapital))
        breakEvenTraceY.append(startCapital)
        redTraceY.append(min(equity_values[-1], startCapital))

        greenTraceX.append(len(equity_values) - 1)
        breakEvenTraceX.append(len(equity_values) - 1)
        redTraceX.append(len(equity_values) - 1)

    else:
        greenTraceY.append(max(equity_values[0], startCapital))
        breakEvenTraceY.append(startCapital)
        redTraceY.append(min(equity_values[0], startCapital))

        greenTraceX.append(0)
        breakEvenTraceX.append(0)
        redTraceX.append(0)       
        
    traces = [greenTraceX, breakEvenTraceX, redTraceX, greenTraceY, 
              breakEvenTraceY, redTraceY]


    return traces