import csv
import serial
import time
import robot_gcodes as rcd
#(Robot)

class colonyPicker:
    def __init__(self,plate_dict,culture_plate,robocomm=None,\
                        robobaud=250000,hometimeout = 10,posfile="robot_positions.csv"):
        self.robocomm = robocomm
        self.plate_order = {"C":[3,2,1],"B":[3,2,1],"A":[3,2,1]}
        
        self.culture_plate = culture_plate
        self.plate_dict = plate_dict
        self.robopos = self.load_posfile(posfilename = posfile)
        if(self.robopos is not None):
            self.staging_floors = sorted(list(self.robopos["plate_staging"].keys()))
        else:
            self.staging_floors = None
        self.robocomm = None
        self.hometimeout = hometimeout #number of minutes without action before you need to home again
        self.lasthomed = -hometimeout
        if(robocomm is not None):
            self.robocomm = serial.Serial(robocomm,robobaud,timeout=5)
            time.sleep(8)
            _=self.read_till_ok(empty_is_ok=True)
        #plate dict looks something like this: 
        #{"A1":"testconstruct1","A2":"con2_2"}
        #numbers are the plate position, strings are the names of the plates
        #TODO: validate plate dict
    @classmethod
    def load_posfile(cls,posfilename):
        posdict = {}
        with open(posfilename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            colnames = []
            for row in csv_reader:
                if line_count == 0:
                    colnames = row
                    #print(f'Column names are {", ".join(row)}')
                else:
                    posname = row[0]
                    locname = row[1]
                    locdict = {locname:{}}
                    if(row[3]==""):
                        posx = None
                    else:
                        posx = float(row[3])
                        locdict[locname]["X"]=posx
                    if(row[4]==""):
                        posy=None
                    else:
                        posy = float(row[4])
                        locdict[locname]["Y"]=posy
                    if(row[5]==""):
                        posz=None
                    else:
                        posz = float(row[5])
                        locdict[locname]["Z"]=posz
                    if(row[6]==""):
                        pose = None
                    else:
                        pose = float(row[6])
                        locdict[locname]["E"]=pose
                    if(row[7]==""):
                        s0pos = None
                    else:
                        s0pos = float(row[7])
                        locdict[locname]["S0pos"]=s0pos
                    if(row[8]==""):
                        s1pos = None
                    else:
                        s1pos = float(row[8])
                        locdict[locname]["S1pos"]=s1pos
                    if(posname in posdict):
                        posdict[posname].update(locdict)
                    else:
                        posdict[posname] = locdict

                line_count += 1
        return posdict
    def read_till_ok(self,alternative_ending=None,empty_is_ok=False):
        if(self.robocomm is None or not self.robocomm.is_open):
            print("Robot is not connected")
            return
        readtext = ""
        while True:
            x = str(self.robocomm.readline())[2:-1]
            readtext += x
            if("ok" in x):
                return readtext
            elif((alternative_ending is not None )and (alternative_ending in x)):
                return readtext
            elif(x==""):
                if(not empty_is_ok):
                    print("== NO OK RECIEVED ==")
                    raise serial.SerialException("no ok recieved")
                else:
                    return readtext
        
    def send_gcode_multiline(self,gcode_list,retval="\n"):
        for gcode_line in gcode_list:
            if(retval not in gcode_line):
                self.robocomm.write(bytes(gcode_line+retval, 'utf-8'))
                self.robocomm.flush()
                machine_output=self.read_till_ok()
            else:
                gsplit = gcode_line.split(retval)
                for subline in gsplit:
                    self.robocomm.write(bytes(subline+retval, 'utf-8'))
                    self.robocomm.flush()
                    machine_output=self.read_till_ok()
        return machine_output
    def home(self):
        self.send_gcode_multiline(rcd.gcode_home())
    #TODO def get_current_pos(self):
    #    pos_output = self.send_gcode_multiline(["M114"])
    #    for sline in pos_output.split("\\n"):

    #def safe_move_robot(self,px=None,py=None,pz=None,pe=None,F=None):
    #    top_pos = self.robopos["z_heights"]["top"]["Z"]
    #    if((px is not None) or (py is not None)):
    #        self.move_robot(pz = top_pos)
    def get_servo_pos(self,servonum=0):
        self.send_gcode_multiline(["M400"])
        servo_output = self.send_gcode_multiline(["M280 P"+str(servonum)])
        posnum = None
        for sline in servo_output.split("\\n"):
            if("Servo "+str(servonum) in sline):
                newsplit = sline.split(":")
                posnum = int(newsplit[-1])
        return posnum
    def get_XYZE_pos(self):
        self.send_gcode_multiline(["M400"])
        position_output = self.send_gcode_multiline(["M114"])
        print(position_output)
    def move_robot(self,px=None,py=None,pz=None,pe=None,F=None):
        assert(sum([px is not None,py is not None, pz is not None, pe is not None])>=1)
        if(self.robocomm is None or not self.robocomm.is_open):
            print("Robot is not connected")
            return
        curtime_minutes = time.time()/60
        if(curtime_minutes - self.lasthomed >= self.hometimeout):
            #this means the robot hasnt homed in a while and should home asap
            self.home()
        curtime_minutes = time.time()/60
        self.lasthomed = curtime_minutes
        drive_feed = 2500
        plate_shake_feed = 400
        if(F is not None):
            drive_feed = F
            plate_shake_feed = F
        if(pz is not None):
            self.send_gcode_multiline(["G1 Z{} F{}".format(str(pz),str(drive_feed))])
        xymove = "G1 "
        if(px is not None):
            xymove += "X{} ".format(str(px))
        if(py is not None):
            xymove += "Y{} ".format(str(py))
        xymove += "F{}".format(str(drive_feed))
        if((px is not None) or (py is not None)):
            self.send_gcode_multiline([xymove])
        if(pe is not None):
            self.send_gcode_multiline(["G1 E{} F{}".format(str(pe),str(plate_shake_feed))])
    def servo_move(self,servonum,position):
        if(self.robocomm is None or not self.robocomm.is_open):
            print("Robot is not connected")
            return
        spos = self.get_servo_pos(servonum)
        if(spos == position):
            return
        else:
            self.send_gcode_multiline(["M400",
                                    "M280 P{} S{}".format(servonum,position),
                                    "G4 P500"])
    def grip(self):
        assert(self.robopos is not None)
        grip_pos = self.robopos["servo"]["grip"]["S1pos"]
        self.servo_move(1,grip_pos)
    def ungrip(self):
        assert(self.robopos is not None)
        ungrip_pos = self.robopos["servo"]["ungrip"]["S1pos"]
        self.servo_move(1,ungrip_pos)
    def lid_grip(self):
        assert(self.robopos is not None)
        lidgrip_pos = self.robopos["servo"]["lid_grip"]["S1pos"]
        self.servo_move(1,lidgrip_pos)
    def gripper_is_lid_down(self):
        assert(self.robopos is not None)
        lid_down = self.robopos["servo"]["lid_down"]["S0pos"]
        return self.get_servo_pos(0)==lid_down
    def gripper_is_lid_up(self):
        assert(self.robopos is not None)
        lid_up = self.robopos["servo"]["lid_up"]["S0pos"]
        return self.get_servo_pos(0)==lid_up
    def flip_lid_down(self):
        assert(self.robopos is not None)
        lid_down = self.robopos["servo"]["lid_down"]["S0pos"]
        self.servo_move(0,lid_down)
    def flip_lid_up(self):
        assert(self.robopos is not None)
        lid_up = self.robopos["servo"]["lid_up"]["S0pos"]
        self.servo_move(0,lid_up)
    def get_plate(self,platepos="0",platepos_name="plate_stack",plate_orientation="down"):
        assert(self.robopos is not None)
        top_pos = self.robopos["z_heights"]["top"]["Z"]
        if(not (platepos in self.robopos[platepos_name])):
            raise ValueError("no position found for plate "+str(platepos)+" in "+str(platepos_name))
        plate_pos_coords = self.robopos[platepos_name][platepos]
        self.move_robot(pz=top_pos)
        self.ungrip()
        if(plate_orientation == "down"):
            self.flip_lid_down()
        elif(plate_orientation=="up"):
            self.flip_lid_up()
        else:
            raise ValueError("invalid plate orientation "+str(plate_orientation)+", only 'up' or 'down' accepted")

        self.move_robot(px = plate_pos_coords["X"],py = plate_pos_coords["Y"])
        if("E" in plate_pos_coords):
            #move the culture plate out of the way if we need to
            self.move_robot(pe = plate_pos_coords["E"])
        self.move_robot(pz = plate_pos_coords["Z"])
        self.grip()
        self.move_robot(pz=plate_pos_coords["Z"]+10)
    def put_plate(self,platepos="0",platepos_name="plate_stack",plate_orientation="down"):
        assert(self.robopos is not None)
        top_pos = self.robopos["z_heights"]["top"]["Z"]
        flip_height = self.robopos["z_heights"]["plate_flip"]["Z"]
        if(not (platepos in self.robopos[platepos_name])):
            raise ValueError("no position found for plate "+str(platepos)+" in "+str(platepos_name))
        plate_pos_coords = self.robopos[platepos_name][platepos]
        #TODO this next part should be done only if the servo is in the wrong spot!

        neut_pos = self.robopos["neutral_position"]["0"]
        if(((plate_orientation == "down") and (not self.gripper_is_lid_down())) or
            ((plate_orientation == "up") and (not self.gripper_is_lid_up()))):
            self.move_robot(pz=top_pos)
            self.move_robot(px = neut_pos["X"],py=neut_pos["Y"])
            
            self.move_robot(pz=flip_height)
            if(plate_orientation == "down"):
                self.flip_lid_down()
            elif(plate_orientation=="up"):
                self.flip_lid_up()
            else:
                raise ValueError("invalid plate orientation "+str(plate_orientation)+", only 'up' or 'down' accepted")
        self.move_robot(pz=top_pos)
        self.move_robot(px = plate_pos_coords["X"],py = plate_pos_coords["Y"])
        if("E" in plate_pos_coords):
            #move the culture plate out of the way if we need to
            self.move_robot(pe = plate_pos_coords["E"])
        self.move_robot(pz = plate_pos_coords["Z"]+10)
        self.move_robot(pz = plate_pos_coords["Z"],F=400)
        self.ungrip()
        self.move_robot(pz = top_pos)
    def induction_heat(self,time_sec,power=255):
        """activate the heater for some number of seconds"""
        self.send_gcode_multiline(["M140 S{}".format(str(power)),\
                "G4 P{}".format(str(int(1000*float(time_sec)))),\
                "M140 S0"])
    def sync(self):
        """wait until all movements are done"""
        self.send_gcode_multiline(["M500"])
    def grab_lid(self,platepos="0",platepos_name="plate_backlight"):
        assert(self.robopos is not None)
        if(not (platepos in self.robopos[platepos_name])):
            raise ValueError("no position found for plate "+str(platepos)+" in "+str(platepos_name))
        top_pos = self.robopos["z_heights"]["top"]["Z"]
        plate_pos_coords = self.robopos[platepos_name][platepos]
        lid_z_addition = self.robopos["modifiers"]["lid_z_addition"]["Z"]
        lid_z_height = plate_pos_coords["Z"]+lid_z_addition
        if("E" in plate_pos_coords):
            #move the culture plate out of the way if we need to
            self.move_robot(pe = plate_pos_coords["E"])
        self.ungrip()
        self.move_robot(pz = top_pos)
        self.flip_lid_up()
        self.move_robot(px=plate_pos_coords["X"],py = plate_pos_coords["Y"])
        self.move_robot(pz =lid_z_height)
        self.lid_grip()
        self.move_robot(pz = lid_z_height+10)
    def place_lid(self,platepos="0",platepos_name="plate_backlight"):
        assert(self.robopos is not None)
        if(not (platepos in self.robopos[platepos_name])):
            raise ValueError("no position found for plate "+str(platepos)+" in "+str(platepos_name))
        top_pos = self.robopos["z_heights"]["top"]["Z"]
        plate_pos_coords = self.robopos[platepos_name][platepos]
        lid_z_addition = self.robopos["modifiers"]["lid_z_addition"]["Z"]
        lid_z_height = plate_pos_coords["Z"]+lid_z_addition
        if("E" in plate_pos_coords):
            #move the culture plate out of the way if we need to
            self.move_robot(pe = plate_pos_coords["E"])
        self.move_robot(pz = top_pos)
        self.flip_lid_up()
        self.move_robot(px=plate_pos_coords["X"],py = plate_pos_coords["Y"])
        self.move_robot(pz =lid_z_height+10)
        self.move_robot(pz =lid_z_height,F=400)
        self.ungrip()
        self.move_robot(pz = lid_z_height+10)

    def light_on(self,strength=0.5):
        value = int(strength*255)
        self.send_gcode_multiline(["M106 S"+str(value)])
    def light_off(self):
        self.send_gcode_multiline(["M106 S0"])
    
    def move_needle(self,needle_pos=0,needle_pos_name="culture_24well",retract=True,offset_x=0,offset_y=0,offset_z=0):
        assert(self.robopos is not None)
        if(not (needle_pos in self.robopos[needle_pos_name])):
            raise ValueError("no position found for "+str(needle_pos)+" in "+str(needle_pos_name))
        top_pos = self.robopos["z_heights"]["top"]["Z"]
        needle_pos_coords = self.robopos[needle_pos_name][needle_pos]
        self.move_robot(pz = top_pos)
        if("E" in needle_pos_coords):
            #move the culture plate out of the way if we need to
            self.move_robot(pe = needle_pos_coords["E"])
        self.move_robot(px=needle_pos_coords["X"]+offset_x,py=needle_pos_coords["Y"]+offset_y)

        needle_zpos_upper = needle_pos_coords["Z"]+offset_z+10
        needle_zpos_lower = needle_pos_coords["Z"]+offset_z
        if(needle_zpos_upper > 67):
            needle_zpos_upper = 67

        self.move_robot(pz = needle_zpos_upper)
        self.move_robot(pz = needle_zpos_lower,F=400)
        if(retract):
            self.move_robot(pz=top_pos)
        