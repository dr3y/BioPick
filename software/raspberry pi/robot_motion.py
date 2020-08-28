import csv
import serial
#(Robot)
#/dev/ttyUSB1
#serial.Serial("COM4",250000)
class colonyPicker:
    def __init__(self,plate_dict,culture_plate,robocomm=None,robobaud=250000,posfile="robot_positions.csv"):
        self.robocomm = robocomm
        self.culture_plate = culture_plate
        self.plate_dict = plate_dict
        self.robopos = self.load_posfile(posfilename = posfile)
        self.robocomm = None
        if(robocomm is not None):
            self.robocomm = serial.Serial(robocomm,robobaud)
        #plate dict looks something like this: 
        #{"A1":"testconstruct1","A2":"con2_2"}
        #numbers are the plate position, strings are the names of the plates
        #TODO: validate plate dict

    def load_posfile(self,posfilename):
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
                    if(row[3]==""):
                        posx = None
                    else:
                        posx = float(row[3])
                    if(row[4]==""):
                        posy=None
                    else:
                        posy = float(row[4])
                    if(row[5]==""):
                        posz=None
                    else:
                        posz = float(row[5])
                    if(row[6]==""):
                        pose = None
                    else:
                        pose = float(row[6])
                    if(row[7]==""):
                        s0pos = None
                    else:
                        s0pos = float(row[7])
                    if(row[8]==""):
                        s1pos = None
                    else:
                        s1pos = float(row[8])
                    if(posname in posdict):
                        posdict[posname].update({locname:{"X":posx,"Y":posy,"Z":posz,"E":pose,"S0pos":s0pos,"S1pos":s1pos}})
                    else:
                        posdict[posname] = {locname:{"X":posx,"Y":posy,"Z":posz,"E":pose,"S0pos":s0pos,"S1pos":s1pos}}

                line_count += 1
        return posdict
    
    def move_robot(self,px=None,py=None,pz=None,pe=None):
        assert(sum([px is not None,py is not None, pz is not None, pe is not None])>=1)
        if(pz is not None):
            self.robocomm.write("G1 Z{} F2500\n".format(str(pe)))
        xymove = "G1 "
        if(px is not None):
            xymove += "X{} ".format(str(px))
        if(py is not None):
            xymove += "Y{} ".format(str(py))
        xymove += "F2500\n"
        if((px is not None) or (py is not None)):
            self.robocomm.write(xymove)
        if(pe is not None):
            self.robocomm.write("G1 E{} F400".format(str(pe)))
    def grip(self):
        assert(self.robopos is not None)
        grip_pos = self.robopos["servo"]["grip"]["S1pos"]
        self.robocomm.write("M400\n")
        self.robocomm.write("M280 P1 S{}\n".format(grip_pos))
        self.robocomm.write("G4 P500\n")
    def ungrip(self):
        assert(self.robopos is not None)
        grip_pos = self.robopos["servo"]["ungrip"]["S1pos"]
        self.robocomm.write("M400\n")
        self.robocomm.write("M280 P1 S{}\n".format(grip_pos))
        self.robocomm.write("G4 P500\n")
    def lid_grip(self):
        assert(self.robopos is not None)
        grip_pos = self.robopos["servo"]["lid_grip"]["S1pos"]
        self.robocomm.write("M400\n")
        self.robocomm.write("M280 P1 S{}\n".format(grip_pos))
        self.robocomm.write("G4 P500\n")
    def flip_lid_down(self):
        assert(self.robopos is not None)
        grip_pos = self.robopos["servo"]["lid_down"]["S0pos"]
        self.robocomm.write("M400\n")
        self.robocomm.write("M280 P0 S{}\n".format(grip_pos))
        self.robocomm.write("G4 P500\n")
    def flip_lid_up(self):
        assert(self.robopos is not None)
        grip_pos = self.robopos["servo"]["lid_up"]["S0pos"]
        self.robocomm.write("M400\n")
        self.robocomm.write("M280 P0 S{}\n".format(grip_pos))
        self.robocomm.write("G4 P500\n")

    def get_plate(self,platepos):
        assert(self.robopos is not None)
        