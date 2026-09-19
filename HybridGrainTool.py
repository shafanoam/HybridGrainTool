import time
import math
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import ImageTk
from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
import numpy as np
from cv2 import resize
from skfmm import distance


# "draw" a circle in the array
def array_gen_circle(x, y, radius, value, array=np.array(float)):
    x_coord = 0
    y_coord = radius
    d = 3-2*radius
    while x_coord <= y_coord:

        array_gen_circle_helper(x_coord, y_coord, x, y, value, array)

        if d < 0:
            d += 4*x_coord + 6
        else:
            d += 4*(x_coord-y_coord) + 10
            y_coord -= 1

        x_coord += 1


def array_gen_circle_helper(x, y, x_offset, y_offset, value, array=np.array(float)):
    # plot in all octants via symetry
    points = [(x, y), (-x, y), (x, -y), (-x, -y), (y, x), (-y, x), (y, -x), (-y, -x)]
    for point in points:
        array[point[1] + y_offset, point[0] + x_offset] = value


# "paint bucket" in the array
def array_paint_bucket_old(x, y, value, array=np.array(float)):
    value_to_change = array[y, x]

    queue = np.array([(x, y)])
    print(time.time())
    while len(queue) > 0:
        current_x, current_y = queue[0]
        queue = np.delete(queue, 0, 0)
        if array[current_y, current_x] == value_to_change:
            array[current_y, current_x] = value
        if array.shape[1] > current_x + 1 and array[current_y, current_x + 1] == value_to_change:
            queue = np.vstack((queue, np.array([(current_x + 1, current_y)])))
        if array.shape[0] > current_y + 1 and array[current_y + 1, current_x] == value_to_change:
            queue = np.vstack((queue, np.array([(current_x, current_y + 1)])))
        if current_x > 0 and array[current_y, current_x - 1] == value_to_change:
            queue = np.vstack((queue, np.array([(current_x - 1, current_y)])))
        if current_y > 0 and array[current_y -1, current_x] == value_to_change:
            queue = np.vstack((queue, np.array([(current_x, current_y - 1)])))
    print(time.time())


def array_paint_bucket(x, y, value, array=np.array(str)):

    if array[y, x] == value:
        return

    value_to_change = array[y, x]

    queue = np.array([(x, x, y, 1), (x, x, y-1, -1)])

    while len(queue) > 0:
        # pop the top of the queue
        x1, x2, y, dy = queue[0]
        queue = np.delete(queue, 0, 0)

        x = x1
        if 0 <= y < array.shape[0] and array[y, x] == value_to_change:
            while 0 <= x-1 <= array.shape[1] and array[y, x-1] == value_to_change:
                array[y, x-1] = value
                x -= 1
            if x < x1:
                queue = np.vstack((queue, np.array([(x, x1-1, y-dy, -dy)])))
        while x1 <= x2:
            while 0 <= y < array.shape[0] and 0 <= x1+1 <= array.shape[1] and array[y, x1] == value_to_change:
                array[y, x1] = value
                x1 += 1
            if x1 > x:
                queue = np.vstack((queue, np.array([(x, x1 - 1, y + dy, dy)])))
            if x1-1 > x2:
                queue = np.vstack((queue, np.array([(x2 + 1, x1 - 1, y - dy, -dy)])))
            x1 += 1
            while y < array.shape[0] and x1 < x2 and not array[y, x1] == value_to_change:
                x1 += 1
            x = x1


def array_draw_line_LOW(x0, y0, x1, y1, value, array):
    dx = x1 - x0
    dy = y1 - y0
    y = y0

    if dy < 0:
        yChange = -1
        dy = -dy
    else:
        yChange = 1

    D = 2*dy - dx

    for x in range(int(round(x0)), int(round(x1))+1):
        array[int(round(y)), x] = value
        if D > 0:
            y += yChange
            D += (2*(dy-dx))
        else:
            D += 2*dy


def array_draw_line_HIGH(x0, y0, x1, y1, value, array):
    dx = x1 - x0
    dy = y1 - y0
    x = x0

    if dx < 0:
        xChange = -1
        dx = -dx
    else:
        xChange = 1

    D = 2 * dx - dy

    for y in range(int(round(y0)), int(round(y1))+1):
        array[y, int(round(x))] = value
        if D > 0:
            x += xChange
            D += (2*(dx-dy))
        else:
            D += 2*dx


def array_draw_line(x0, y0, x1, y1, value, array):
    if abs(y1-y0) < abs(x1-x0):
        if x0 > x1:
            array_draw_line_LOW(x1, y1, x0, y0, value, array)
        else:
            array_draw_line_LOW(x0, y0, x1, y1, value, array)
    else:
        if y0 > y1:
            array_draw_line_HIGH(x1, y1, x0, y0, value, array)
        else:
            array_draw_line_HIGH(x0, y0, x1, y1, value, array)


def array_draw_star(diameter, sides, amplitude, value, array):
    # getting the center x and y coords of the array
    centerx, centery = array.shape
    centerx //= 2
    centery //= 2
    vertexList = []
    theta = 0
    vector_long = diameter//2 + amplitude//2
    vector_short = diameter//2 - amplitude//2

    # generate the verticies
    for i in range(sides):
        vector_coords = (centerx + vector_long * math.cos(theta), centery + vector_long * math.sin(theta))
        vertexList.append(vector_coords)
        theta += (2*math.pi)/sides/2
        vector_coords = (centerx + vector_short * math.cos(theta), centery + vector_short * math.sin(theta))
        vertexList.append(vector_coords)
        theta += (2*math.pi)/sides/2

    # generate the lines
    for i in range(0, -len(vertexList), -1):
        array_draw_line(vertexList[i][0], vertexList[i][1], vertexList[i-1][0], vertexList[i-1][1], value, array)

    array_paint_bucket(centerx, centery, value, array)


simulationInstanceFrame = np.array([[i for i in range(0,220)] for j in range(0,220)], dtype=float)
# simulationFrames = np.array([simulationInstanceFrame.copy()], dtype=float)
simulationFrameList = [simulationInstanceFrame.copy()]
simulationImages = []

circleMask = np.array([[0 for i in range(0, 220)] for j in range(0, 220)], dtype=float)
array_gen_circle(110, 110, 109, 1, circleMask)
array_paint_bucket(110, 110, 1, circleMask)

outerMask = np.array([[0.5 for i in range(0, 220)] for j in range(0, 220)], dtype=float)
array_gen_circle(110, 110, 109, 0, outerMask)
array_paint_bucket(110, 110, 0, outerMask)


lastSingleSimData = []


simming = False
def single_sim():
    global simming
    simming = True
    global simulationFrameList
    global lastSingleSimData

    lastSingleSimData = []
    ratioPlottingData = []
    timePlottingData = []

    cell_size = float(simCellSize_entry.get())
    sim_timestep = float(simTimestepSize_entry.get())
    sim_maxTime = float(maxSimTime_entry.get())

    # figure out the dimensions of everything!
    actual_OD = int(round(float(fuelOuter_entry.get()) * distance_converter_dict[fuelOuter_units.get()]))
    actual_ID = int(round(float(fuelInner_entry.get()) * distance_converter_dict[fuelInner_units.get()]))
    actual_height = float(fuelHeight_entry.get()) * distance_converter_dict[fuelHeight_units.get()]
    actual_amplitude = int(round(float(singleSimAmplitude.get()) * distance_converter_dict[singleSimAmpUnits.get()]))
    print(f"Outer diameter is {actual_OD * cell_size} mm")
    print(f"Inner diameter is {actual_ID * cell_size} mm")
    print(f"Star amplitude is {actual_amplitude * cell_size} mm")

    actual_MassFlow = float(mass_flow_converter_dict[massFlow_units.get()]) * float(massFlow_entry.get())
    print(f"Mass flow is {actual_MassFlow} kg/s")
    actual_fuelDensity = float(fuelDensity_entry.get()) * density_converter_dict[fuelDensity_units.get()]

    burnCoeff_A = float(burnCoeff_a_entry.get())
    burnCoeff_N = float(burnCoeff_n_entry.get())


    initialTime = time.time()

    # creating simulation frames
    # instanceFrame = np.array([[1.0 for i in range(0, actual_OD)] for j in range(0, actual_OD)], dtype=float)
    instanceFrame = np.ones((actual_OD, actual_OD))
    print(instanceFrame.shape)
    # reset simulation lists
    simulationFrameList = [instanceFrame.copy()]

    # generate initial starting frame
    initialFrame = simulationFrameList[0]  # points to actual instance, apparently

    array_draw_star(actual_ID, int(singleSimSideCount.get()), actual_amplitude, 0.0, initialFrame)

    distanceFrame = distance(initialFrame, dx=cell_size)

    # simulation state variables

    class simClass():
        def __init__(self):
            self.portArea = 0  # in m^2
            self.massFlux = 0  # in kg/s/m^2
            self.regressionRate = 0  # in mm/s
            self.nominalRegressionDistance = 0  # in mm
            self.oxFuelRatio = 0  # unitless value
            self.timeElapsed = 0

    sim = simClass()

    # save first frame to frames list
    # simulationFrames = np.vstack((simulationFrames, [initialFrame]))
    update_shapeCanvas(initialFrame)
    dist = 1 - 1/actual_OD  # TODO: check if this is fine or needs to account for cell size!
    # while 0 in (cv2.resize(simulationFrames[-1], dsize=(220,220)) * circleMask + outerMask):
    continuing = True

    def step_sim(distFrame, startTime):
        global simulationFrameList
        nonlocal continuing
        nonlocal dist
        global lastSingleSimData

        # calculate simulation state
        sim.portArea = cell_size**2 * (actual_OD**2 - np.count_nonzero(simulationFrameList[-1])) / 1000**2
        sim.massFlux = actual_MassFlow / sim.portArea
        sim.regressionRate = burnCoeff_A * (sim.massFlux ** burnCoeff_N)

        sim.nominalRegressionDistance += sim.regressionRate * sim_timestep


        dist = sim.nominalRegressionDistance
        # print(f"{dist}\t{sim.nominalRegressionDistance}\t{sim.regressionRate}")

        # newFrame = (distFrame - distFrame.max()) / (distFrame.min() - distFrame.max())  # normalizing!
        # newFrame[newFrame > dist] = 0
        newFrame = distFrame.copy()
        newFrame[newFrame < dist] = 0

        # figure out mass flow rate by delta grain area times height!
        newFrameBool = newFrame.copy()
        newFrameBool[newFrameBool > 0] = True
        newFrameBool[newFrameBool == 0] = False

        try:
            oldFrameBool = simulationFrameList[-5].copy()
            i = 5
        except:
            oldFrameBool = simulationFrameList[-1].copy()
            i = 1
        oldFrameBool[oldFrameBool > 0] = True
        oldFrameBool[oldFrameBool == 0] = False

        deltaGrain = np.logical_xor(newFrameBool, oldFrameBool)
        deltaArea = np.count_nonzero(deltaGrain) * cell_size**2 / (1000**2)  # in m^2
        fuelMassFlow = actual_fuelDensity * deltaArea * (actual_height * cell_size) / sim_timestep / i  # in kg/s
        try:
            sim.oxFuelRatio = actual_MassFlow / fuelMassFlow
        except ZeroDivisionError:
            pass
        # print(f"{actual_MassFlow}\t{deltaArea}\t{fuelMassFlow}\t{sim.oxFuelRatio}")

        sim.timeElapsed += sim_timestep

        simulationFrameList.append(newFrame)

        smallFrame = resize(newFrame, dsize=(220, 220))
        smallFrame[smallFrame > 0] = 1
        if (sim.timeElapsed > sim_maxTime) or (1 not in smallFrame * circleMask + outerMask):
            continuing = False

        stepComputationTime = time.time() - startTime

        lastSingleSimData.append({
            "Port Area": sim.portArea,
            "Mass Flux": sim.massFlux,
            "Regression Rate": sim.regressionRate,
            "Nominal Regression Distance": sim.nominalRegressionDistance,
            "O/F Ratio": sim.oxFuelRatio,
            "Time Elapsed": sim.timeElapsed,
            "Timestep Computation Time": stepComputationTime
        })

        ratioPlottingData.append(sim.oxFuelRatio)
        timePlottingData.append(sim.timeElapsed)

        # update_shapeCanvas(newFrame)

    while continuing:
        step_sim(distanceFrame, time.time())
        # dist -= 1/actual_OD

    print(f"Simulation time: {sim.timeElapsed}")
    print(time.time() - initialTime)

    # place onto graph

    ratioPlotPlt.clear()
    ratioPlotPlt.plot(timePlottingData, ratioPlottingData)
    desiredOF = float(massRatio_entry.get())
    ratioSides = float(validRatio_entry.get())
    ratioPlotPlt.set_ylim(desiredOF - ratioSides, desiredOF + ratioSides)
    ratioCanvas.draw()



def timeSlider_MOVED(position):
    global simulationFrameList
    position = int(float(position))
    try:
        update_shapeCanvas(simulationFrameList[position])
        stateLabel_PortArea.config(text=str(round(lastSingleSimData[position]["Port Area"] * 100**2, 4)) + " cm^2")
        stateLabel_MassFlux.config(text=str(round(lastSingleSimData[position]["Mass Flux"], 4)) + " kg/m^2/s")
        stateLabel_RegRate.config(text=str(round(lastSingleSimData[position]["Regression Rate"], 4)) + " mm/s")
        stateLabel_NomReg.config(text=str(round(lastSingleSimData[position]["Nominal Regression Distance"], 4)) + " mm")
        stateLabel_MassRatio.config(text=str(round(lastSingleSimData[position]["O/F Ratio"], 4)))
        stateLabel_TimeElapsed.config(text=str(round(lastSingleSimData[position]["Time Elapsed"], 4)) + " s")
        stateLabel_CompTime.config(text=str(round(lastSingleSimData[position]["Timestep Computation Time"] * 1000, 4)) + " ms")
    except:
        pass

def update_shapeCanvas(frame):

    global shapeCanvas
    global outerMask

    smallFrame = resize(frame, dsize=(220, 220))  # zoom(frame.copy(), 220/frame.shape[0])



    smallFrame[smallFrame > 0] = 255
    colors = smallFrame * circleMask + outerMask * 255

    # this is like the entire below (before using ImageTK), compressed to one line. Not actually faster.
    # [[toShow.put(f"#{str(hex(int(colors[col][row])))[2:]*3}", (col, row)) for col in range(1, colors.shape[0])] for row in range(1, colors.shape[1])]

    BobtheImage = Image.new("L", (220,220))
    row = 0
    col = 0
    for color in colors:
        for color2 in color:
            thing = str(hex(int(color2.item())))[2:]
            # toShow.put(f"#{thing*3}", (col, row))
            BobtheImage.putpixel((row, col), int(color2.item()))
            col += 1
        row += 1
        col = 0
    toShow = ImageTk.PhotoImage(BobtheImage)

    # toShow.write("plotty.png")

    shapeCanvas.create_image(110, 110, image=toShow, anchor="center")
    # apparently this is needed to remove the auto garbage collection of toShow???
    # Ok so apparently it deletes toShow afterwar the function finishes (exits its scope)
    # and then the reference that is being rendered disappears
    # this binds it to the root window instead so that it survives exiting the context
    root.toShow = toShow


def export_CSV():
    if len(lastSingleSimData) <= 1:
        return

    file = tk.filedialog.asksaveasfile(mode="w", defaultextension=".csv")
    if file is None:  # return if cancelled
        return

    file.write("Time Elapsed, Port Area, Mass Flux, Regression Rate, Nominal Regression Distance, O/F Ratio, "
               "Timestep Computation Time, ")
    file.write(f"Sim parameters. Ox mass flow: {massFlow_entry.get()} {massFlow_units.get()}"
               f" Fuel density: {fuelDensity_entry.get()} {fuelDensity_units.get()}"
               f" Grain OD: {fuelOuter_entry.get()} {fuelOuter_units.get()}"
               f" Grain nom. ID: {fuelInner_entry.get()} {fuelInner_units.get()}"
               f" Grain height: {fuelHeight_entry.get()} {fuelHeight_units.get()}"
               f" Burn coeff. A: {burnCoeff_a_entry.get()} mm/s"
               f" Burn coeff. B: {burnCoeff_n_entry.get()}"
               f" Timestep size: {simTimestepSize_entry.get()} s"
               f" Sim fidelity: {simCellSize_entry.get()} mm"
               f" # of sides: {singleSimSideCount.get()}"
               f" Side amplitude: {singleSimAmplitude.get()} {singleSimAmpUnits.get()}"
               f"\n")

    for timestep in lastSingleSimData:
        file.write(f"{timestep['Time Elapsed']}, {timestep['Port Area']}, {timestep['Mass Flux']}, "
                   f"{timestep['Regression Rate']}, {timestep['Nominal Regression Distance']}, {timestep['O/F Ratio']}"
                   f", {timestep['Timestep Computation Time']}")
        file.write("\n")

    file.close()  # get it out of memory once done!


def config_save():

    file = tk.filedialog.asksaveasfile(mode="w", defaultextension=".hgt", filetypes=[("HGT Config File", ".hgt")])

    if file is None:  # return if cancelled
        return

    file.write("Name: " + engineName_entry.get() + "\n")
    file.write("Description: " + engineWords_entry.get() + "\n")
    file.write("OxFlow: " + massFlow_entry.get() + " " + massFlow_units.get() + "\n")
    file.write("Target_O/F: " + massRatio_entry.get() + "\n")
    file.write("O/F_BoundRadius: " + validRatio_entry.get() + "\n")
    file.write("Fuel_Density: " + fuelDensity_entry.get() + " " + fuelDensity_units.get() + "\n")
    file.write("Grain_OD: " + fuelOuter_entry.get() + " " + fuelOuter_units.get() + "\n")
    file.write("Grain_ID: " + fuelInner_entry.get() + " " + fuelInner_units.get() + "\n")
    file.write("Grain_Height: " + fuelHeight_entry.get() + " " + fuelHeight_units.get() + "\n")
    file.write("Coeff_Preset: " + standardCoeffSelector.get() + "\n")
    file.write("Coeff_A: " + burnCoeff_a_entry.get() + "\n")
    file.write("Coeff_N: " + burnCoeff_n_entry.get() + "\n")
    file.write("Timestep: " + simTimestepSize_entry.get() + "\n")
    file.write("Cell_Size: " + simCellSize_entry.get() + "\n")
    file.write("Max_Sim_Time: " + maxSimTime_entry.get() + "\n")
    file.write("Side_Count: " + singleSimSideCount.get() + "\n")
    file.write("Side_Amplitude: " + singleSimAmplitude.get() + " " + singleSimAmpUnits.get() + "\n")

    file.close()


def config_load():

    file = tk.filedialog.askopenfile(mode="r", defaultextension=".hgt", filetypes=[("HGT Config File", ".hgt")])

    if file is None:  # return if cancelled
        return

    lines = file.readlines()

    lines = [thing.split() for thing in lines]

    engineName_entry.delete(0, "end")
    engineName_entry.insert(index=0, string=lines[0][1:])

    engineWords_entry.delete(0, "end")
    engineWords_entry.insert(index=0, string=lines[1][1:])

    massFlow_entry.delete(0, "end")
    massFlow_entry.insert(index=0, string=lines[2][1])
    massFlow_units.set(lines[2][2])

    massRatio_entry.delete(0, "end")
    massRatio_entry.insert(index=0, string=lines[3][1])
    validRatio_entry.delete(0, "end")
    validRatio_entry.insert(index=0, string=lines[4][1])

    fuelDensity_entry.delete(0, "end")
    fuelDensity_entry.insert(index=0, string=lines[5][1])
    fuelDensity_units.set(lines[5][2])

    fuelOuter_entry.delete(0, "end")
    fuelOuter_entry.insert(index=0, string=lines[6][1])
    fuelOuter_units.set(lines[6][2])

    fuelInner_entry.delete(0, "end")
    fuelInner_entry.insert(index=0, string=lines[7][1])
    fuelInner_units.set(lines[7][2])

    fuelHeight_entry.delete(0, "end")
    fuelHeight_entry.insert(index=0, string=lines[8][1])
    fuelHeight_units.set(lines[8][2])

    burnCoeff_a_entry.config(state="normal")
    burnCoeff_n_entry.config(state="normal")

    standardCoeffSelector.set(lines[9][1])
    burnCoeff_a_entry.delete(0, "end")
    burnCoeff_a_entry.insert(index=0, string=lines[10][1])
    burnCoeff_n_entry.delete(0, "end")
    burnCoeff_n_entry.insert(index=0, string=lines[11][1])
    if standardCoeffSelector.get() != "Custom":
        burnCoeff_a_entry.config(state="disabled")
        burnCoeff_n_entry.config(state="disabled")

    simTimestepSize_entry.delete(0, "end")
    simTimestepSize_entry.insert(index=0, string=lines[12][1])

    simCellSize_entry.delete(0, "end")
    simCellSize_entry.insert(index=0, string=lines[13][1])

    maxSimTime_entry.delete(0, "end")
    maxSimTime_entry.insert(index=0, string=lines[14][1])

    singleSimSideCount.delete(0, "end")
    singleSimSideCount.insert(index=0, string=lines[15][1])

    singleSimAmplitude.delete(0, "end")
    singleSimAmplitude.insert(index=0, string=lines[16][1])
    singleSimAmpUnits.set(lines[16][2])

    file.close()


# the default is mostly nonsense numbers, just to get something visible on the graph
def reset_to_default():

    engineName_entry.delete(0, "end")
    engineName_entry.insert(index=0, string="Untitled Engine")
    engineWords_entry.delete(0, "end")
    engineWords_entry.insert(index=0, string="No Description")

    massFlow_entry.delete(0, "end")
    massFlow_entry.insert(index=0, string="1")
    massFlow_units.set("kg/s")

    massRatio_entry.delete(0, "end")
    massRatio_entry.insert(index=0, string="8")
    validRatio_entry.delete(0, "end")
    validRatio_entry.insert(index=0, string="4")

    fuelDensity_entry.delete(0, "end")
    fuelDensity_entry.insert(index=0, string="10")

    fuelOuter_entry.delete(0, "end")
    fuelOuter_entry.insert(index=0, string="5")
    fuelOuter_units.set("cm")
    fuelInner_entry.delete(0, "end")
    fuelInner_entry.insert(index=0, string="3")
    fuelHeight_units.set("cm")
    fuelHeight_entry.delete(0, "end")
    fuelHeight_entry.insert(index=0, string="1")

    burnCoeff_a_entry.config(state="normal")
    burnCoeff_n_entry.config(state="normal")


    standardCoeffSelector.set("custom")
    burnCoeff_a_entry.delete(0, "end")
    burnCoeff_a_entry.insert(index=0, string="1")
    burnCoeff_n_entry.delete(0, "end")
    burnCoeff_n_entry.insert(index=0, string="1")

    simTimestepSize_entry.delete(0, "end")
    simTimestepSize_entry.insert(index=0, string="0.1")

    simCellSize_entry.delete(0, "end")
    simCellSize_entry.insert(index=0, string="0.1")

    maxSimTime_entry.delete(0, "end")
    maxSimTime_entry.insert(index=0, string="100")

    singleSimSideCount.delete(0, "end")
    singleSimSideCount.insert(index=0, string="8")
    singleSimAmplitude.delete(0, "end")
    singleSimAmplitude.insert(index=0, string="1")
    singleSimAmpUnits.set("cm")

root = tk.Tk()
root.title("Hybrid Grain Tool")
root.configure(background="whitesmoke")
root.geometry("800x600")
root.resizable(False, False)

rootBook = ttk.Notebook(root)
rootBook.pack(expand=True, fill="both")


########################### welcome page
welcomeFrame = tk.Frame(rootBook, bg="whitesmoke")
tk.Label(welcomeFrame, text="Hybrid Rocket Grain Analysis Tool", bg="whitesmoke",
         font=("Arial", 20)).place(relx=0.5, rely=0.02, anchor="n")
tk.Label(welcomeFrame, text="This program is created to simulate the regression of arbitrarily-shaped hybrid rocket "
                            "fuel grains. It has been verified through TAMU-SRT's Ignis engine as of the time of"
                            " publishing.", wraplength=700, bg="whitesmoke"
         ).place(relx=0.5, rely=0.08, anchor="n")
ttk.Separator(rootBook, orient="horizontal").place(relx=0.5, rely=0.2, anchor="n", relwidth=0.9)
tk.Label(welcomeFrame, font="15", text="Notes for use:", bg="whitesmoke").place(relx=0.15, rely=0.2, anchor="nw")
tk.Label(welcomeFrame, text="* Your use of this program is AT YOUR OWN RISK!\n\n"
                                       "* Ensure all fields are filled when saving the configuration.\n\n"
                                       "* This simulator assumes constant oxidizer mass flow rate. Adjust accoardingly\n\n"
                                       "* Mess around with the simulation timestep and cell size to produce smoother results.\n\n"
                                       "* Check units! (Note that there is a suspected bug w/ the fuel density units.)",
         bg="whitesmoke", justify="left").place(relx=0.15, rely=0.25, anchor="nw")
tk.Label(welcomeFrame, text="Created by Noam A.  Distribution, modification, and use is allowed with attribution to 'Noam A.' for"
                            " educational purposes. May not be distributed, modified, or used for any other purpose.",
         wraplength=775, bg="whitesmoke").place(relx=0.5, rely=0.98, anchor="s")


welcomeFrame.pack(expand=True, fill="both")

rootBook.add(welcomeFrame, text="Welcome")


########################### General Units Dropdown

class unitPicker(ttk.Combobox):
    def __init__(self, parent, type=""):
        super().__init__(parent, state="readonly")
        if type == "mass":
            self.config(values=["kg", "lb", "g", "oz"])
            self.set("kg")
        elif type == "distance":
            self.config(values=["m", "cm", "mm", "ft", "in"])
            self.set("cm")
        elif type == "mass flow":
            self.config(values=["kg/s", "lb/s", "g/s", "oz/s"])
            self.set("kg/s")
        elif type == "density":
            self.config(values=["kg/m^3", "g/cm^3", "oz/in^3", "lb/yd^3"])
            self.set("g/cm^3")
        else:
            exit("Not a valid type of unit for unitPicker!")


class distance_converter(dict):  # distance unit conversion that ACCOUNTS for cell size upon access!
    def __getitem__(self, key):
        divisor = float(simCellSize_entry.get())
        initial = {"m": 1000, "cm": 10, "mm": 1, "ft": 304.8, "in": 25.4}[key]  # conversion to 1mm
        return initial / divisor


distance_converter_dict = distance_converter()

# distance_converter_dict = {"m": 10000, "cm": 100, "mm": 10, "ft": 3048, "in": 254} # conversion to "general unit" of 0.1mm

mass_flow_converter_dict = {"kg/s": 1, "g/s": 0.001, "lb/s": 0.453592, "oz/s": 0.0283495}  # conversion to 1kg/s

density_converter_dict = {"kg/m^3": 1, "g/cm^3": 0.001, "oz/in^3": 0.000578037, "lb/yd^3": 1.68555}  # conversion to kg/m^3


########################### Basic setup page

baseSetupFrame = tk.Frame(rootBook, bg="whitesmoke")

# props entry
propsSetupFrame = tk.LabelFrame(baseSetupFrame, text="Propellants", bg="whitesmoke")
propsSetupFrame.place(relx=0.01, rely=0, relwidth=0.59, relheight=0.25)

tk.Label(propsSetupFrame, text="Oxidizer Mass Flow = ", justify="right",
         bg="whitesmoke").place(relx=0.3, rely=0.2, relwidth=0.3, anchor="e")
massFlow_entry = tk.Entry(propsSetupFrame)
massFlow_entry.place(relx=0.3, rely=0.2, relwidth=0.4, anchor="w")
massFlow_units = unitPicker(propsSetupFrame, type="mass flow")
massFlow_units.place(relx=0.75, rely=0.2, relwidth=0.2, anchor="w")

tk.Label(propsSetupFrame, text="Target O/F Ratio = ", justify="right",
         bg="whitesmoke").place(relx=0.3, rely=0.5, relwidth=0.3, anchor="e")
massRatio_entry = tk.Entry(propsSetupFrame)
massRatio_entry.place(relx=0.3, rely=0.5, relwidth=0.4, anchor="w")
tk.Label(propsSetupFrame, text="±", bg="whitesmoke").place(relx=0.74, rely=0.5, anchor="e")
validRatio_entry = tk.Entry(propsSetupFrame)
validRatio_entry.place(relx=0.85, rely=0.5, anchor="center", relwidth=0.2)

tk.Label(propsSetupFrame, text="Fuel Density = ", justify="right",
         bg="whitesmoke").place(relx=0.3, rely=0.8, relwidth=0.3, anchor="e")
fuelDensity_entry = tk.Entry(propsSetupFrame)
fuelDensity_entry.place(relx=0.3, rely=0.8, relwidth=0.4, anchor="w")
fuelDensity_units = unitPicker(propsSetupFrame, type="density")
fuelDensity_units.place(relx=0.75, rely=0.8, relwidth=0.2, anchor="w")

# grain entry
fuelSetupFrame = tk.LabelFrame(baseSetupFrame, text="Fuel Grain", bg="whitesmoke")
fuelSetupFrame.place(relx=0.01, rely=0.25, relwidth=0.59, relheight=0.25)

tk.Label(fuelSetupFrame, text="OD = ", justify="right",
         bg="whitesmoke").place(relx=0.3, rely=0.2, relwidth=0.3, anchor="e")
fuelOuter_entry = tk.Entry(fuelSetupFrame)
fuelOuter_entry.place(relx=0.3, rely=0.2, relwidth=0.4, anchor="w")
fuelOuter_units = unitPicker(fuelSetupFrame, type="distance")
fuelOuter_units.place(relx=0.75, rely=0.2, relwidth=0.2, anchor="w")

tk.Label(fuelSetupFrame, text="Nominal ID = ", justify="right",
         bg="whitesmoke").place(relx=0.3, rely=0.5, relwidth=0.3, anchor="e")
fuelInner_entry = tk.Entry(fuelSetupFrame)
fuelInner_entry.place(relx=0.3, rely=0.5, relwidth=0.4, anchor="w")
fuelInner_units = unitPicker(fuelSetupFrame, type="distance")
fuelInner_units.place(relx=0.75, rely=0.5, relwidth=0.2, anchor="w")

tk.Label(fuelSetupFrame, text="Height = ", justify="right",
         bg="whitesmoke").place(relx=0.3, rely=0.8, relwidth=0.3, anchor="e")
fuelHeight_entry = tk.Entry(fuelSetupFrame)
fuelHeight_entry.place(relx=0.3, rely=0.8, relwidth=0.4, anchor="w")
fuelHeight_units = unitPicker(fuelSetupFrame, type="distance")
fuelHeight_units.place(relx=0.75, rely=0.8, relwidth=0.2, anchor="w")


coeffValues = {  # formatted a,n
    "N2O + HTPB": (0.198, 0.325),
    "N2O + ABS": (0.198, 0.325)

}
# TODO: find better coefficients for ABS that aren't "ah more or less like HTPB"


def update_coeff_entries(event):
    if standardCoeffSelector.get() == "Custom":
        burnCoeff_a_entry.config(state="normal")
        burnCoeff_n_entry.config(state="normal")
    else:
        burnCoeff_a_entry.config(state="normal")
        burnCoeff_n_entry.config(state="normal")

        burnCoeff_a_entry.delete(0, "end")
        burnCoeff_a_entry.insert(index=0, string=str(coeffValues[standardCoeffSelector.get()][0]))

        burnCoeff_n_entry.delete(0, "end")
        burnCoeff_n_entry.insert(index=0, string=str(coeffValues[standardCoeffSelector.get()][1]))

        burnCoeff_a_entry.config(state="disabled")
        burnCoeff_n_entry.config(state="disabled")


# coefficient inputs
regressionCoefficientsFrame = tk.LabelFrame(baseSetupFrame, text="Regression Coefficients", bg="whitesmoke")
regressionCoefficientsFrame.place(relx=0.61, rely=0, relwidth=0.38, relheight=0.5)
standardCoeffSelector = ttk.Combobox(regressionCoefficientsFrame, state="readonly",
                                     values=["Custom", "N2O + HTPB", "N2O + ABS"])
standardCoeffSelector.set("Custom")
standardCoeffSelector.bind("<<ComboboxSelected>>", update_coeff_entries)
standardCoeffSelector.place(relx=0.5, rely=0.1, anchor="n")
tk.Label(regressionCoefficientsFrame, text="Select a known set of coefficients, or manually enter them below.",
         bg="whitesmoke", wraplength=280, justify="left").place(relx=0.5, rely=0.25, anchor="n")

innerRegressionCoefficientsFrame = tk.Frame(regressionCoefficientsFrame, bg="whitesmoke")
innerRegressionCoefficientsFrame.place(relx=0, rely=0.4, relwidth=1, relheight=0.6)
tk.Label(innerRegressionCoefficientsFrame, text="a = ", justify="right",
         bg="whitesmoke").place(relx=0.3, rely=0,relwidth=0.3, anchor="ne")
burnCoeff_a_entry = tk.Entry(innerRegressionCoefficientsFrame)
burnCoeff_a_entry.place(relx=0.3, rely=0, relwidth=0.5)
tk.Label(innerRegressionCoefficientsFrame, text="mm/s", bg="whitesmoke").place(relx=0.875, rely=0, anchor="n")

tk.Label(innerRegressionCoefficientsFrame, text="n = ", justify="right",
         bg="whitesmoke").place(relx=0.3, rely=0.2, relwidth=0.3, anchor="ne")
burnCoeff_n_entry = tk.Entry(innerRegressionCoefficientsFrame)
burnCoeff_n_entry.place(relx=0.3, rely=0.2, relwidth=0.5)
tk.Label(innerRegressionCoefficientsFrame, text="~", bg="whitesmoke").place(relx=0.85, rely=0.2, anchor="n")
tk.Label(innerRegressionCoefficientsFrame, text="ṙ = aG", bg="whitesmoke", font="25").place(relx=0.5, rely=0.55, anchor="n")
tk.Label(innerRegressionCoefficientsFrame, text="n", bg="whitesmoke").place(relx=0.6125, rely=0.5, anchor="n")

# simulation setup inputs
simSetupFrame = tk.LabelFrame(baseSetupFrame, text="Simulation Fidelity", bg="whitesmoke")
simSetupFrame.place(relx=0.01, rely=0.5, relwidth=0.98, relheight=0.25)

tk.Label(simSetupFrame, text="Timestep = ", justify="right",
         bg="whitesmoke").place(relx=0.15, rely=0.2, relwidth=0.15, anchor="e")
simTimestepSize_entry = tk.Entry(simSetupFrame)
simTimestepSize_entry.place(relx=0.15, rely=0.2, relwidth=0.2, anchor="w")
tk.Label(simSetupFrame, text="s", bg="whitesmoke").place(relx=0.375, rely=0.2, anchor="w")

tk.Label(simSetupFrame, text="Max Sim. Time = ", justify="right",
         bg="whitesmoke").place(relx=0.15, rely=0.45, relwidth=0.15, anchor="e")
maxSimTime_entry = tk.Entry(simSetupFrame)
maxSimTime_entry.place(relx=0.15, rely=0.45, relwidth=0.2, anchor="w")
tk.Label(simSetupFrame, text="s", bg="whitesmoke").place(relx=0.375, rely=0.45, anchor="w")

tk.Label(simSetupFrame, text="Cell Size = ", justify="right",
         bg="whitesmoke").place(relx=0.6, rely=0.2, relwidth=0.15, anchor="e")
simCellSize_entry = tk.Entry(simSetupFrame)
simCellSize_entry.place(relx=0.6, rely=0.2, relwidth=0.2, anchor="w")
tk.Label(simSetupFrame, text="mm", bg="whitesmoke").place(relx=0.825, rely=0.2, anchor="w")

# config save and load

configFrame = tk.LabelFrame(baseSetupFrame, text="Config File", bg="whitesmoke")
configFrame.place(relx=0.01, rely=0.75, relwidth=0.2, relheight=0.24)

resetButton = tk.Button(configFrame, text="  Reset to Default  ", bg="whitesmoke", command=reset_to_default)
resetButton.place(relx=0.5, rely=0.25, relwidth=0.9, anchor="center")

loadConfigButton = tk.Button(configFrame, text="  Load From Disk  ", bg="whitesmoke", command=config_load)
loadConfigButton.place(relx=0.5, rely=0.5, relwidth=0.9, anchor="center")

saveConfigButton = tk.Button(configFrame, text="  Save to Disk  ", bg="whitesmoke", command=config_save)
saveConfigButton.place(relx=0.5, rely=0.75, relwidth=0.9, anchor="center")

# engine name and info

engineInfoFrame = tk.LabelFrame(baseSetupFrame, text="Engine Info", bg="whitesmoke")
engineInfoFrame.place(relx=0.25, rely=0.75, relwidth=0.74, relheight=0.24)

tk.Label(engineInfoFrame, text="Name:", bg="whitesmoke").place(relx=0.14, rely=0.05, anchor="e")
engineName_entry = tk.Entry(engineInfoFrame)
engineName_entry.place(relx=0.15, rely=0.01, relwidth = 0.84)

tk.Label(engineInfoFrame, text="Description:", bg="whitesmoke").place(relx=0.14, rely=0.35, anchor="e")
engineWords_entry = tk.Entry(engineInfoFrame)
engineWords_entry.place(relx=0.15, rely=0.3, relwidth = 0.84, relheight=0.65)


########################### single-sim page
singleSimFrame = tk.Frame(root, bg="whitesmoke")

# update simulation
updateSimFrame = tk.LabelFrame(singleSimFrame, bg="whitesmoke", text="Options")
updateSimFrame.place(relx=0.0125, rely=0, relwidth=0.375, relheight=0.25)
tk.Label(updateSimFrame, text="# of sides: ", justify="right", bg="whitesmoke").place(relx=0.3, rely=0.25, anchor="e")
singleSimSideCount = tk.Entry(updateSimFrame)
singleSimSideCount.place(relx=0.325, rely=0.25, relwidth=0.425, anchor="w")
tk.Label(updateSimFrame, text="~", bg="whitesmoke").place(relx=0.775, rely=0.25, anchor="w")
tk.Label(updateSimFrame, text="Amplitude = ", justify="right",bg="whitesmoke").place(relx=0.3, rely=0.5, anchor="e")
singleSimAmplitude = tk.Entry(updateSimFrame)
singleSimAmplitude.place(relx=0.325, rely=0.5, relwidth=0.425, anchor="w")
singleSimAmpUnits = unitPicker(updateSimFrame, type="distance")
singleSimAmpUnits.place(relx=0.775, rely=0.5, relwidth=0.175, anchor="w")
updateSimButton = tk.Button(updateSimFrame, text="Update Simulation", bg="whitesmoke", command=single_sim)
updateSimButton.place(relx=0.5, rely=0.7, anchor="n")

# show current state of fuel grain shape
showShapeFrame = tk.LabelFrame(singleSimFrame, bg="whitesmoke", text="Shape")
showShapeFrame.place(relx=0.0125, rely=0.25, relwidth=0.375, relheight=0.45)
shapeCanvas = tk.Canvas(showShapeFrame, bg="gray", width=220, height=220)
shapeCanvas.place(relx=0.5, rely=0.5, anchor="center")
# shapeCanvas.create_oval(12.5, 12.5, 212.5, 212.5, outline="black", fill="white")

# show graph of O/F ratio
ratioGraphFrame = tk.LabelFrame(singleSimFrame, bg="whitesmoke", text="O/F Ratio over Time")
ratioGraphFrame.place(relx=0.4, rely=0, relwidth=0.5875, relheight=0.7)
ratioPlotFig = plt.Figure(figsize=(4.5, 3), dpi=100)
ratioPlotPlt = ratioPlotFig.add_subplot(111)
ratioCanvas = FigureCanvasTkAgg(ratioPlotFig, master=ratioGraphFrame)
# ratioCanvas = tk.Canvas(ratioGraphFrame, bg="whitesmoke")
ratioCanvas.get_tk_widget().place(relx=0.5, rely=0.05, anchor="n", width=450, height=300)
# ratioCanvas.create_rectangle(2, 2, 447, 297, outline="black")
# ratioCanvas.create_line(20, 20, 20, 280, fill="black")
# ratioCanvas.create_line(20, 150, 430, 150, fill="black")

timeSlider = ttk.Scale(ratioGraphFrame, from_=0, to=10000000, orient="horizontal", command=timeSlider_MOVED)
timeSlider.place(relx=0.5125, rely=0.95, width=360, anchor="s")

# allow exporting a CSV and image/gif of viewport
exportTableFrame = tk.LabelFrame(singleSimFrame, bg="whitesmoke", text="Export")
exportTableFrame.place(relx=0.0125, rely=0.7, relwidth=0.375, relheight=0.2875)
tk.Button(exportTableFrame, text="Save Simulation Data as CSV",
          command=export_CSV).place(relx=0.5, rely=0.15, anchor="center")
ttk.Separator(exportTableFrame).place(relx=0.5, rely=0.25, anchor="center")
imageExportResolution = tk.Checkbutton(exportTableFrame, text="Export at Sim Resolution instead of 220x220", bg="whitesmoke")
imageExportResolution.place(relx=0.5, rely=0.375, anchor="center")
tk.Button(exportTableFrame, text="Save Current Timestep Image as PNG",
          command=lambda: print("hello!")).place(relx=0.5, rely=0.6, anchor="center")
tk.Button(exportTableFrame, text="Save Simulation Images GIF",
          command=lambda: print("hello!")).place(relx=0.5, rely=0.85, anchor="center")

# show info of current time-step
stateFrame = tk.LabelFrame(singleSimFrame, bg="whitesmoke", text="Simulation State")
stateFrame.place(relx=0.4, rely=0.7, relwidth=0.5875, relheight=0.2875, anchor="nw")

tk.Label(stateFrame, text="Port Area: ", bg="whitesmoke").place(relx=0.25, rely=0.2, anchor="e")
tk.Label(stateFrame, text="Mass Flux: ", bg="whitesmoke").place(relx=0.25, rely=0.4, anchor="e")
tk.Label(stateFrame, text="Regression Rate: ", bg="whitesmoke").place(relx=0.25, rely=0.6, anchor="e")
tk.Label(stateFrame, text="Nom. Regression: ", bg="whitesmoke").place(relx=0.25, rely=0.8, anchor="e")
tk.Label(stateFrame, text="O/F Ratio: ", bg="whitesmoke").place(relx=0.75, rely=0.2, anchor="e")
tk.Label(stateFrame, text="Time Elapsed: ", bg="whitesmoke").place(relx=0.75, rely=0.4, anchor="e")
tk.Label(stateFrame, text="Computation Time: ", bg="whitesmoke").place(relx=0.75, rely=0.6, anchor="e")


stateLabel_PortArea = tk.Label(stateFrame, text="0", bg="whitesmoke")
stateLabel_PortArea.place(relx=0.25, rely=0.2, anchor="w")

stateLabel_MassFlux = tk.Label(stateFrame, text="0", bg="whitesmoke")
stateLabel_MassFlux.place(relx=0.25, rely=0.4, anchor="w")

stateLabel_RegRate = tk.Label(stateFrame, text="0", bg="whitesmoke")
stateLabel_RegRate.place(relx=0.25, rely=0.6, anchor="w")

stateLabel_NomReg = tk.Label(stateFrame, text="0", bg="whitesmoke")
stateLabel_NomReg.place(relx=0.25, rely=0.8, anchor="w")

stateLabel_MassRatio = tk.Label(stateFrame, text="0", bg="whitesmoke")
stateLabel_MassRatio.place(relx=0.75, rely=0.2, anchor="w")

stateLabel_TimeElapsed = tk.Label(stateFrame, text="0", bg="whitesmoke")
stateLabel_TimeElapsed.place(relx=0.75, rely=0.4, anchor="w")

stateLabel_CompTime = tk.Label(stateFrame, text="0", bg="whitesmoke")
stateLabel_CompTime.place(relx=0.75, rely=0.6, anchor="w")




rootBook.add(baseSetupFrame, text="Setup")
rootBook.add(singleSimFrame, text="Simulation")
# rootBook.add(tk.Frame(), text="Multi Sim")

while True:
    root.update_idletasks()
    root.update()
    timeSlider.config(from_=0, to=len(simulationFrameList))

    # for thing in [burnCoeff_a_entry, burnCoeff_n_entry, fuelInner_entry, fuelOuter_entry]:
    #     try:
    #         float(thing.get())
    #         thing.config(bg="white")
    #     except ValueError:
    #         thing.config(bg="yellow")
    #     if not thing.get():
    #         thing.config(bg="white")
